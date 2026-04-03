from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TargetCreate(BaseModel):
    site_id: uuid.UUID | None = None  # null = overall/consolidated target
    kpi_name: str = Field(max_length=100)
    kpi_category: str = Field(max_length=50)
    target_value: Decimal
    period_year: int = Field(ge=2000, le=2100)
    period_month: int | None = Field(default=None, ge=1, le=12)


class TargetUpdate(BaseModel):
    target_value: Decimal


class TargetResponse(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID | None
    kpi_name: str
    kpi_category: str
    target_value: Decimal
    period_year: int
    period_month: int | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TargetListResponse(BaseModel):
    items: list[TargetResponse]
    total: int


__all__ = ["TargetCreate", "TargetUpdate", "TargetResponse", "TargetListResponse"]
