from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.financial_data import StatementStatus, StatementType


class LineItemUpload(BaseModel):
    line_item_code: str = Field(max_length=50)
    line_item_name: str = Field(max_length=255)
    parent_code: str | None = None
    amount: Decimal


class FinancialStatementUpload(BaseModel):
    site_id: uuid.UUID
    statement_type: StatementType
    period_year: int = Field(ge=2000, le=2100)
    period_month: int = Field(ge=1, le=12)
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    line_items: list[LineItemUpload]


class LineItemResponse(BaseModel):
    id: uuid.UUID
    line_item_code: str
    line_item_name: str
    parent_code: str | None
    amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class FinancialStatementResponse(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    statement_type: StatementType
    period_year: int
    period_month: int
    currency: str
    status: StatementStatus
    uploaded_by: uuid.UUID
    uploaded_at: datetime
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    line_items: list[LineItemResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class FinancialStatementListResponse(BaseModel):
    items: list[FinancialStatementResponse]
    total: int


class KPIValue(BaseModel):
    """A single KPI value with metadata."""
    name: str
    value: Decimal | None
    unit: str = "ratio"
    description: str = ""


class KPIResponse(BaseModel):
    site_id: uuid.UUID | None = None
    site_name: str | None = None
    period_year: int
    period_month: int
    currency: str
    profitability: list[KPIValue] = Field(default_factory=list)
    liquidity: list[KPIValue] = Field(default_factory=list)
    efficiency: list[KPIValue] = Field(default_factory=list)
    leverage: list[KPIValue] = Field(default_factory=list)


__all__ = [
    "LineItemUpload",
    "FinancialStatementUpload",
    "LineItemResponse",
    "FinancialStatementResponse",
    "FinancialStatementListResponse",
    "KPIValue",
    "KPIResponse",
]
