from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetEntryCreate(BaseModel):
    site_id: uuid.UUID
    line_item_code: str = Field(max_length=50)
    period_year: int = Field(ge=2000, le=2100)
    period_month: int = Field(ge=1, le=12)
    budget_amount: Decimal


class BudgetEntryUpdate(BaseModel):
    budget_amount: Decimal


class BudgetEntryResponse(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    line_item_code: str
    period_year: int
    period_month: int
    budget_amount: Decimal
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetListResponse(BaseModel):
    items: list[BudgetEntryResponse]
    total: int


__all__ = ["BudgetEntryCreate", "BudgetEntryUpdate", "BudgetEntryResponse", "BudgetListResponse"]
