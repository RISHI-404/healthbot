"""Medication Reminder CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.models.medication import MedicationReminder

router = APIRouter()


@router.get("/", response_model=List[MedicationResponse])
async def list_medications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all medication reminders for the current user."""
    result = await db.execute(
        select(MedicationReminder)
        .where(MedicationReminder.user_id == current_user.id)
        .order_by(MedicationReminder.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    data: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new medication reminder."""
    med = MedicationReminder(user_id=current_user.id, **data.model_dump())
    db.add(med)
    await db.flush()
    await db.refresh(med)
    return med


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a medication reminder."""
    result = await db.execute(
        select(MedicationReminder).where(
            MedicationReminder.id == medication_id,
            MedicationReminder.user_id == current_user.id,
        )
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(med, key, value)
    await db.flush()
    await db.refresh(med)
    return med


@router.delete("/{medication_id}")
async def delete_medication(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a medication reminder."""
    result = await db.execute(
        select(MedicationReminder).where(
            MedicationReminder.id == medication_id,
            MedicationReminder.user_id == current_user.id,
        )
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found.")

    await db.delete(med)
    return {"message": "Medication reminder deleted."}
