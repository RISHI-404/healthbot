"""Admin panel routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.schemas.admin import AdminUserResponse, SystemMetrics
from app.utils.dependencies import require_role
from app.models.user import User, UserRole
from app.models.conversation import Conversation, Message
from app.models.appointment import Appointment
from app.models.feedback import Feedback

router = APIRouter()


@router.get("/users", response_model=List[AdminUserResponse])
async def list_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all users in the system."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    await db.delete(user)
    return {"message": f"User {user.email} deleted."}


@router.get("/metrics", response_model=SystemMetrics)
async def get_metrics(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get system usage metrics."""
    users_count = await db.scalar(select(func.count(User.id)))
    convos_count = await db.scalar(select(func.count(Conversation.id)))
    msgs_count = await db.scalar(select(func.count(Message.id)))
    appts_count = await db.scalar(select(func.count(Appointment.id)))
    feedbacks_count = await db.scalar(select(func.count(Feedback.id)))
    avg_rating = await db.scalar(select(func.avg(Feedback.rating)))

    return SystemMetrics(
        total_users=users_count or 0,
        total_conversations=convos_count or 0,
        total_messages=msgs_count or 0,
        total_appointments=appts_count or 0,
        total_feedbacks=feedbacks_count or 0,
        average_rating=round(float(avg_rating), 2) if avg_rating else None,
    )
