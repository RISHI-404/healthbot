"""Feedback routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.models.feedback import Feedback

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback/rating for a chat response."""
    fb = Feedback(user_id=current_user.id, **data.model_dump())
    db.add(fb)
    await db.flush()
    await db.refresh(fb)
    return fb


@router.get("/", response_model=List[FeedbackResponse])
async def list_my_feedback(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all feedback submitted by the current user."""
    result = await db.execute(
        select(Feedback)
        .where(Feedback.user_id == current_user.id)
        .order_by(Feedback.created_at.desc())
    )
    return result.scalars().all()
