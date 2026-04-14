"""Chat routes — send messages, stream responses, manage conversations."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse,
    ConversationResponse, ConversationDetailResponse,
)
from app.services import chat_service
from app.services.emergency_detector import detect_emergency, EMERGENCY_RESPONSE
from app.services.nlp_pipeline import NLPPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Shared NLP pipeline instance (models loaded lazily on first request)
_nlp_pipeline = NLPPipeline()
_nlp_ready = False


async def _get_nlp_pipeline() -> NLPPipeline:
    """Ensure NLP pipeline is initialised before use."""
    global _nlp_ready
    if not _nlp_ready:
        await _nlp_pipeline.initialize()
        _nlp_ready = True
    return _nlp_pipeline


# Confidence thresholds for hybrid routing
NLP_HIGH_CONFIDENCE  = 0.80   # >= this  → use NLP ML response
NLP_MID_CONFIDENCE   = 0.50   # >= this  → use local AI model
                               # <  0.50  → fall back to NVIDIA API

SESSION_COOKIE = "healthbot_session"


def get_session_id(request: Request, response: Response) -> str:
    """Get or create a session ID from cookies."""
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_id,
            max_age=60 * 60 * 24 * 365,  # 1 year
            httponly=True,
            samesite="lax",
        )
    return session_id


@router.post("/send")
async def send_message(
    request: Request,
    response: Response,
    msg: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and receive a streaming SSE response."""
    session_id = get_session_id(request, response)

    # Get or create conversation
    conversation = await chat_service.get_or_create_conversation(
        db, session_id, msg.conversation_id
    )

    # Save user message
    await chat_service.save_message(db, conversation.id, "user", msg.message)

    # Update title if first message
    if msg.conversation_id is None:
        await chat_service.update_conversation_title(db, conversation, msg.message)

    # Step 1: Emergency detection
    is_emergency, matched_keyword = detect_emergency(msg.message)
    if is_emergency:
        await chat_service.save_message(
            db, conversation.id, "assistant", EMERGENCY_RESPONSE,
            intent="emergency", is_emergency=True,
        )
        await db.commit()
        return StreamingResponse(
            chat_service.stream_response(EMERGENCY_RESPONSE),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Conversation-Id": str(conversation.id),
                "X-Is-Emergency": "true",
                "Access-Control-Expose-Headers": "X-Conversation-Id, X-Is-Emergency",
            },
        )

    # Step 2: Get conversation context (shared by all AI tiers)
    context = await chat_service.get_conversation_context(db, conversation.id)

    # ------------------------------------------------------------------ #
    # Step 3: HYBRID AI DECISION SYSTEM                                   #
    #   Tier 1 (confidence >= 0.80) → NLP ML response (fast, local)      #
    #   Tier 2 (confidence 0.50-0.79) → Local TinyLlama model            #
    #   Tier 3 (confidence < 0.50)  → NVIDIA API fallback                #
    # ------------------------------------------------------------------ #
    nlp = await _get_nlp_pipeline()
    nlp_result = await nlp.process(msg.message, context)

    confidence: float = nlp_result.get("confidence", 0.0)
    ai_tier: str = ""
    response_text: str = ""

    if confidence >= NLP_HIGH_CONFIDENCE:
        # ── Tier 1: High-confidence NLP ML response ──────────────────────
        ai_tier = "nlp_ml"
        response_text = nlp_result["response"]
        logger.info(f"[HybridAI] Tier 1 (NLP ML) — confidence={confidence:.2f}")

    elif confidence >= NLP_MID_CONFIDENCE:
        # ── Tier 2: Local TinyLlama model ───────────────────────────────
        ai_tier = "local_ai"
        local_ai = getattr(request.app.state, "local_ai_service", None)
        if local_ai is not None and local_ai._model_id:
            try:
                response_text = await local_ai.generate_response(msg.message, context)
                logger.info(f"[HybridAI] Tier 2 (Local AI) — confidence={confidence:.2f}")
            except Exception as exc:
                logger.warning(f"[HybridAI] Local AI failed ({exc}), falling back to NVIDIA")
                ai_tier = "nvidia_api_fallback"
        else:
            # Local AI not configured — drop straight to NVIDIA
            ai_tier = "nvidia_api_fallback"
            logger.info("[HybridAI] Local AI not configured, using NVIDIA fallback")

    if not response_text or ai_tier in ("nvidia_api_fallback", ""):
        # ── Tier 3: NVIDIA API fallback ──────────────────────────────────
        ai_tier = ai_tier or "nvidia_api"
        gemini = request.app.state.gemini_service
        try:
            response_text = await gemini.generate_response(msg.message, context)
            logger.info(f"[HybridAI] Tier 3 (NVIDIA API) — confidence={confidence:.2f}")
        except Exception as exc:
            logger.error(f"[HybridAI] NVIDIA API error: {type(exc).__name__}: {exc}")
            response_text = (
                "I'm sorry, I'm having trouble processing your request right now. "
                "Please try again in a moment. If you're experiencing a medical emergency, "
                "please call emergency services immediately."
            )

    # Save assistant response (record which AI tier handled it)
    await chat_service.save_message(
        db, conversation.id, "assistant", response_text,
        intent=ai_tier,
    )
    await db.commit()

    # Stream the response
    return StreamingResponse(
        chat_service.stream_response(response_text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": str(conversation.id),
            "X-Is-Emergency": "false",
            "X-AI-Tier": ai_tier,
            "Access-Control-Expose-Headers": "X-Conversation-Id, X-Is-Emergency, X-AI-Tier",
        },
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current session."""
    session_id = get_session_id(request, response)
    conversations = await chat_service.get_user_conversations(db, session_id)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Get a conversation with all messages."""
    session_id = get_session_id(request, response)
    conv = await chat_service.get_conversation_messages(db, conversation_id, session_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conv


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation."""
    from sqlalchemy import select
    from app.models.conversation import Conversation

    session_id = get_session_id(request, response)

    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.session_id == session_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    await db.delete(conv)
    return {"message": "Conversation deleted."}


@router.get("/ai-status", tags=["Chat"])
async def ai_status(request: Request):
    """
    Health check endpoint for all AI service tiers.
    GET /api/chat/ai-status
    """
    local_ai = getattr(request.app.state, "local_ai_service", None)
    gemini   = getattr(request.app.state, "gemini_service", None)

    local_ai_status = {
        "enabled": local_ai is not None and bool(local_ai._model_id),
        "model": getattr(local_ai, "_model_id", None),
        "model_loaded": getattr(local_ai, "is_ready", False),
        "adapter_path": getattr(local_ai, "_adapter_path", "") or None,
    }

    nvidia_status = {
        "enabled": gemini is not None and gemini._client is not None,
    }

    return {
        "hybrid_routing": {
            "tier1_nlp_threshold": NLP_HIGH_CONFIDENCE,
            "tier2_local_ai_threshold": NLP_MID_CONFIDENCE,
            "description": (
                f"confidence >= {NLP_HIGH_CONFIDENCE} → NLP ML | "
                f"{NLP_MID_CONFIDENCE}-{NLP_HIGH_CONFIDENCE} → Local AI | "
                f"< {NLP_MID_CONFIDENCE} → NVIDIA API"
            ),
        },
        "tier1_nlp_ml": {"enabled": True, "description": "TF-IDF + Logistic Regression"},
        "tier2_local_ai": local_ai_status,
        "tier3_nvidia_api": nvidia_status,
    }
