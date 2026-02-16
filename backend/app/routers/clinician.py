"""Clinician dashboard routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.schemas.auth import UserResponse
from app.schemas.chat import ConversationResponse, ConversationDetailResponse
from app.schemas.admin import ClinicianNoteCreate, ClinicianNoteResponse
from app.utils.dependencies import require_role
from app.models.user import User, UserRole
from app.models.conversation import Conversation, Message
from app.models.clinician_note import ClinicianNote

router = APIRouter()


@router.get("/patients", response_model=List[UserResponse])
async def list_patients(
    current_user: User = Depends(require_role(UserRole.CLINICIAN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all patient users."""
    result = await db.execute(
        select(User).where(User.role == UserRole.PATIENT).order_by(User.created_at.desc())
    )
    return result.scalars().all()


@router.get("/patients/{patient_id}/conversations", response_model=List[ConversationResponse])
async def get_patient_conversations(
    patient_id: int,
    current_user: User = Depends(require_role(UserRole.CLINICIAN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get all conversations for a specific patient."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == patient_id)
        .order_by(Conversation.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(require_role(UserRole.CLINICIAN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get full conversation transcript."""
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    msg_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    )
    conv.messages = msg_result.scalars().all()
    return conv


@router.post("/notes", response_model=ClinicianNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    data: ClinicianNoteCreate,
    current_user: User = Depends(require_role(UserRole.CLINICIAN)),
    db: AsyncSession = Depends(get_db),
):
    """Add a clinician note for a patient."""
    note = ClinicianNote(clinician_id=current_user.id, **data.model_dump())
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.get("/notes/{patient_id}", response_model=List[ClinicianNoteResponse])
async def get_patient_notes(
    patient_id: int,
    current_user: User = Depends(require_role(UserRole.CLINICIAN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get all notes for a patient."""
    result = await db.execute(
        select(ClinicianNote)
        .where(ClinicianNote.patient_id == patient_id)
        .order_by(ClinicianNote.created_at.desc())
    )
    return result.scalars().all()
