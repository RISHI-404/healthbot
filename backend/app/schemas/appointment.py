"""Appointment Pydantic schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AppointmentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    doctor_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: datetime


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    doctor_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class AppointmentResponse(BaseModel):
    id: int
    title: str
    doctor_name: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    scheduled_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
