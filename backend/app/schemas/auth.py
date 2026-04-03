from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.local_cfo


class TokenResponse(BaseModel):
    """Returned in body only to confirm success; actual tokens are in HTTP-only cookies."""
    message: str = "Authentication successful"
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    assigned_site_ids: list[uuid.UUID] = Field(default_factory=list)

    model_config = {"from_attributes": True}


__all__ = ["LoginRequest", "RegisterRequest", "TokenResponse", "UserResponse"]
