"""Chat service — manages conversations and message persistence."""

import json
from typing import List, Dict, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

from app.models.conversation import Conversation, Message


async def get_or_create_conversation(
    db: AsyncSession, session_id: str, conversation_id: Optional[int] = None
) -> Conversation:
    """Get existing conversation or create a new one."""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.session_id == session_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    # Create new conversation
    conv = Conversation(session_id=session_id, title="New Conversation")
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    intent: Optional[str] = None,
    entities: Optional[List[Dict]] = None,
    is_emergency: bool = False,
) -> Message:
    """Save a message to the database."""
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        intent=intent,
        entities=json.dumps(entities) if entities else None,
        is_emergency=is_emergency,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_conversation_context(
    db: AsyncSession, conversation_id: int, limit: int = 10
) -> List[Dict]:
    """Get recent messages for context."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(messages)
    ]


async def update_conversation_title(
    db: AsyncSession, conversation: Conversation, first_message: str
):
    """Update conversation title based on first message."""
    title = first_message[:50] + ("..." if len(first_message) > 50 else "")
    conversation.title = title
    await db.flush()


async def stream_response(response_text: str) -> AsyncGenerator[str, None]:
    """Stream response text token-by-token as SSE events."""
    words = response_text.split(" ")
    for i, word in enumerate(words):
        token = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'token': token})}\n\n"
        await asyncio.sleep(0.03)
    yield f"data: {json.dumps({'done': True})}\n\n"


async def get_user_conversations(db: AsyncSession, session_id: str) -> List[Conversation]:
    """Get all conversations for a session."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .order_by(Conversation.updated_at.desc())
    )
    return result.scalars().all()


async def get_conversation_messages(
    db: AsyncSession, conversation_id: int, session_id: str
) -> Optional[Conversation]:
    """Get a conversation with all its messages."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.session_id == session_id,
        )
    )
    conv = result.scalar_one_or_none()
    if conv:
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        conv.messages = msg_result.scalars().all()
    return conv
