from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    country: str = Field(min_length=1, max_length=100)
    local_currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    country: str | None = Field(None, min_length=1, max_length=100)
    local_currency: str | None = Field(None, min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    is_active: bool | None = None


class SiteResponse(BaseModel):
    id: uuid.UUID
    name: str
    country: str
    local_currency: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SiteListResponse(BaseModel):
    items: list[SiteResponse]
    total: int


__all__ = ["SiteCreate", "SiteUpdate", "SiteResponse", "SiteListResponse"]
