"""Chat routes — send messages, stream responses, manage conversations."""

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

router = APIRouter()

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

    # Step 2: Get context and generate Gemini response
    context = await chat_service.get_conversation_context(db, conversation.id)
    gemini = request.app.state.gemini_service

    try:
        response_text = await gemini.generate_response(msg.message, context)
    except Exception as e:
        import logging
        logging.error(f"Gemini API error: {type(e).__name__}: {e}")
        response_text = (
            "I'm sorry, I'm having trouble processing your request right now. "
            "Please try again in a moment. If you're experiencing a medical emergency, "
            "please call emergency services immediately."
        )

    # Save assistant response
    await chat_service.save_message(
        db, conversation.id, "assistant", response_text,
        intent="gemini_response",
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
            "Access-Control-Expose-Headers": "X-Conversation-Id, X-Is-Emergency",
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
