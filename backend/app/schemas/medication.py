"""Medication Pydantic schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MedicationCreate(BaseModel):
    medication_name: str = Field(..., min_length=2, max_length=255)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    time_of_day: Optional[str] = None
    notes: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None


class MedicationUpdate(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    time_of_day: Optional[str] = None
    notes: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MedicationResponse(BaseModel):
    id: int
    medication_name: str
    dosage: str
    frequency: str
    time_of_day: Optional[str]
    notes: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
