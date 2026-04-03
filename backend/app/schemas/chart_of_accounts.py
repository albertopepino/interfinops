from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ─── Group Account ──────────────────────────────────────────────────────────

class GroupAccountCreate(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=255)
    account_type: str  # "asset", "liability", "equity", "revenue", "expense"
    parent_code: str | None = None
    display_order: int = 0
    is_active: bool = True


class GroupAccountResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    account_type: str
    parent_code: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GroupAccountListResponse(BaseModel):
    items: list[GroupAccountResponse]
    total: int


# ─── Site Account ───────────────────────────────────────────────────────────

class SiteAccountCreate(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=255)
    account_type: str
    parent_code: str | None = None
    display_order: int = 0
    is_active: bool = True


class SiteAccountResponse(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    code: str
    name: str
    account_type: str
    parent_code: str | None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SiteAccountListResponse(BaseModel):
    items: list[SiteAccountResponse]
    total: int


# ─── Account Mapping ────────────────────────────────────────────────────────

class AccountMappingCreate(BaseModel):
    site_account_id: uuid.UUID
    group_account_id: uuid.UUID


class AccountMappingResponse(BaseModel):
    id: uuid.UUID
    site_account_id: uuid.UUID
    group_account_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class BulkMappingUpdate(BaseModel):
    mappings: list[AccountMappingCreate]


# ─── Mapping Matrix ─────────────────────────────────────────────────────────

class MappingMatrixEntry(BaseModel):
    site_account: SiteAccountResponse
    group_account: GroupAccountResponse | None = None


class MappingMatrixResponse(BaseModel):
    site_id: uuid.UUID
    entries: list[MappingMatrixEntry]
    total: int


class CoAUploadResponse(BaseModel):
    created: int
    updated: int
    total: int
    errors: list[str] = []


__all__ = [
    "GroupAccountCreate",
    "GroupAccountResponse",
    "GroupAccountListResponse",
    "SiteAccountCreate",
    "SiteAccountResponse",
    "SiteAccountListResponse",
    "AccountMappingCreate",
    "AccountMappingResponse",
    "BulkMappingUpdate",
    "MappingMatrixEntry",
    "MappingMatrixResponse",
    "CoAUploadResponse",
]
