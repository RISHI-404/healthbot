"""Authentication Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.PATIENT


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    has_consented: bool
    is_active: bool

    class Config:
        from_attributes = True


class ConsentRequest(BaseModel):
    accepted: bool = Field(..., description="User must accept the medical disclaimer")
