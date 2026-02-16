"""Admin Pydantic schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    has_consented: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SystemMetrics(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    total_appointments: int
    total_feedbacks: int
    average_rating: Optional[float] = None


class ClinicianNoteCreate(BaseModel):
    patient_id: int
    conversation_id: Optional[int] = None
    content: str


class ClinicianNoteResponse(BaseModel):
    id: int
    clinician_id: int
    patient_id: int
    conversation_id: Optional[int]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
