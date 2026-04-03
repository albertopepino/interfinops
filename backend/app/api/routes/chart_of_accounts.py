from __future__ import annotations

import io
import uuid
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import AuditLogger, CurrentUser, DbSession, require_role
from app.models.chart_of_accounts import AccountMapping, AccountType, GroupAccount, SiteAccount
from app.models.user import User, UserRole
from app.schemas.chart_of_accounts import (
    BulkMappingUpdate,
    CoAUploadResponse,
    GroupAccountCreate,
    GroupAccountListResponse,
    GroupAccountResponse,
    MappingMatrixEntry,
    MappingMatrixResponse,
    SiteAccountCreate,
    SiteAccountListResponse,
    SiteAccountResponse,
)

router = APIRouter(prefix="/chart-of-accounts", tags=["chart-of-accounts"])


# ─── Group Accounts ─────────────────────────────────────────────────────────

@router.get("/group", response_model=GroupAccountListResponse)
async def list_group_accounts(
    db: DbSession,
    current_user: CurrentUser,
) -> GroupAccountListResponse:
    """List all group (master) accounts ordered by display_order."""
    stmt = select(GroupAccount).order_by(GroupAccount.display_order, GroupAccount.code)
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return GroupAccountListResponse(
        items=[GroupAccountResponse.model_validate(a) for a in accounts],
        total=len(accounts),
    )


@router.post(
    "/group",
    response_model=GroupAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_account(
    body: GroupAccountCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(UserRole.admin, UserRole.group_cfo))],
) -> GroupAccountResponse:
    """Create a new group account (admin/group_cfo only)."""
    # Validate account_type
    try:
        acct_type = AccountType(body.account_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid account_type: {body.account_type}",
        )

    account = GroupAccount(
        code=body.code,
        name=body.name,
        account_type=acct_type,
        parent_code=body.parent_code,
        display_order=body.display_order,
        is_active=body.is_active,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return GroupAccountResponse.model_validate(account)


# ─── Helpers ───────────────────────────────────────────────────────────────

VALID_ACCOUNT_TYPES = {t.value for t in AccountType}


async def _parse_upload_file(file: UploadFile) -> pd.DataFrame:
    """Read a CSV or XLSX upload into a DataFrame."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    contents = await file.read()
    if ext == "csv":
        df = pd.read_csv(io.BytesIO(contents), dtype=str, keep_default_na=False)
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(contents), dtype=str, keep_default_na=False)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a .csv or .xlsx file.")
    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    required = {"code", "name", "account_type"}
    missing = required - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(sorted(missing))}")
    return df


# ─── Group Upload ──────────────────────────────────────────────────────────

@router.post("/group/upload", response_model=CoAUploadResponse)
async def upload_group_accounts(
    file: UploadFile,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(UserRole.admin, UserRole.group_cfo))],
) -> CoAUploadResponse:
    """Bulk upload/upsert group accounts from a CSV or Excel file."""
    df = await _parse_upload_file(file)
    created = 0
    updated = 0
    errors: list[str] = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed header + data
        code = str(row.get("code", "")).strip()
        name = str(row.get("name", "")).strip()
        account_type = str(row.get("account_type", "")).strip().lower()
        parent_code = str(row.get("parent_code", "")).strip() or None
        display_order_raw = str(row.get("display_order", "0")).strip()

        if not code or not name:
            errors.append(f"Row {row_num}: code and name are required.")
            continue
        if account_type not in VALID_ACCOUNT_TYPES:
            errors.append(f"Row {row_num}: invalid account_type '{account_type}'. Must be one of: {', '.join(sorted(VALID_ACCOUNT_TYPES))}.")
            continue
        try:
            display_order = int(display_order_raw) if display_order_raw else 0
        except ValueError:
            display_order = 0

        stmt = select(GroupAccount).where(GroupAccount.code == code)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = name
            existing.account_type = AccountType(account_type)
            existing.parent_code = parent_code
            existing.display_order = display_order
            updated += 1
        else:
            account = GroupAccount(
                code=code,
                name=name,
                account_type=AccountType(account_type),
                parent_code=parent_code,
                display_order=display_order,
            )
            db.add(account)
            created += 1

    await db.flush()
    return CoAUploadResponse(created=created, updated=updated, total=created + updated, errors=errors)


# ─── Site Upload ───────────────────────────────────────────────────────────

@router.post("/site/{site_id}/upload", response_model=CoAUploadResponse)
async def upload_site_accounts(
    site_id: uuid.UUID,
    file: UploadFile,
    db: DbSession,
    current_user: CurrentUser,
) -> CoAUploadResponse:
    """Bulk upload/upsert site accounts from a CSV or Excel file."""
    df = await _parse_upload_file(file)
    created = 0
    updated = 0
    errors: list[str] = []

    for idx, row in df.iterrows():
        row_num = idx + 2
        code = str(row.get("code", "")).strip()
        name = str(row.get("name", "")).strip()
        account_type = str(row.get("account_type", "")).strip().lower()
        parent_code = str(row.get("parent_code", "")).strip() or None
        display_order_raw = str(row.get("display_order", "0")).strip()

        if not code or not name:
            errors.append(f"Row {row_num}: code and name are required.")
            continue
        if account_type not in VALID_ACCOUNT_TYPES:
            errors.append(f"Row {row_num}: invalid account_type '{account_type}'. Must be one of: {', '.join(sorted(VALID_ACCOUNT_TYPES))}.")
            continue
        try:
            display_order = int(display_order_raw) if display_order_raw else 0
        except ValueError:
            display_order = 0

        stmt = select(SiteAccount).where(
            SiteAccount.site_id == site_id,
            SiteAccount.code == code,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = name
            existing.account_type = AccountType(account_type)
            existing.parent_code = parent_code
            existing.display_order = display_order
            updated += 1
        else:
            account = SiteAccount(
                site_id=site_id,
                code=code,
                name=name,
                account_type=AccountType(account_type),
                parent_code=parent_code,
                display_order=display_order,
            )
            db.add(account)
            created += 1

    await db.flush()
    return CoAUploadResponse(created=created, updated=updated, total=created + updated, errors=errors)


# ─── Site Accounts ──────────────────────────────────────────────────────────

@router.get("/site/{site_id}", response_model=SiteAccountListResponse)
async def list_site_accounts(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteAccountListResponse:
    """List all accounts for a specific site ordered by display_order."""
    stmt = (
        select(SiteAccount)
        .where(SiteAccount.site_id == site_id)
        .order_by(SiteAccount.display_order, SiteAccount.code)
    )
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return SiteAccountListResponse(
        items=[SiteAccountResponse.model_validate(a) for a in accounts],
        total=len(accounts),
    )


@router.post(
    "/site/{site_id}",
    response_model=SiteAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_site_account(
    site_id: uuid.UUID,
    body: SiteAccountCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteAccountResponse:
    """Create a new site account."""
    try:
        acct_type = AccountType(body.account_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid account_type: {body.account_type}",
        )

    account = SiteAccount(
        site_id=site_id,
        code=body.code,
        name=body.name,
        account_type=acct_type,
        parent_code=body.parent_code,
        display_order=body.display_order,
        is_active=body.is_active,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return SiteAccountResponse.model_validate(account)


# ─── Mapping Matrix ─────────────────────────────────────────────────────────

@router.get("/mapping/{site_id}", response_model=MappingMatrixResponse)
async def get_mapping_matrix(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MappingMatrixResponse:
    """Get the mapping matrix for a site: each site account with its mapped group account (or null)."""
    # Fetch site accounts with their mappings eagerly loaded
    stmt = (
        select(SiteAccount)
        .where(SiteAccount.site_id == site_id)
        .options(
            selectinload(SiteAccount.account_mapping).selectinload(AccountMapping.group_account)
        )
        .order_by(SiteAccount.display_order, SiteAccount.code)
    )
    result = await db.execute(stmt)
    site_accounts = result.scalars().all()

    entries = []
    for sa in site_accounts:
        group_acct = None
        if sa.account_mapping and sa.account_mapping.group_account:
            group_acct = GroupAccountResponse.model_validate(sa.account_mapping.group_account)
        entries.append(
            MappingMatrixEntry(
                site_account=SiteAccountResponse.model_validate(sa),
                group_account=group_acct,
            )
        )

    return MappingMatrixResponse(
        site_id=site_id,
        entries=entries,
        total=len(entries),
    )


@router.put("/mapping/{site_id}", response_model=MappingMatrixResponse)
async def update_mappings(
    site_id: uuid.UUID,
    body: BulkMappingUpdate,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> MappingMatrixResponse:
    """Bulk update account mappings for a site."""
    for mapping_input in body.mappings:
        # Look up existing mapping for this site_account
        stmt = select(AccountMapping).where(
            AccountMapping.site_account_id == mapping_input.site_account_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.group_account_id = mapping_input.group_account_id
        else:
            new_mapping = AccountMapping(
                site_account_id=mapping_input.site_account_id,
                group_account_id=mapping_input.group_account_id,
                created_by=current_user.id,
            )
            db.add(new_mapping)

    await db.flush()

    await audit_log(
        "update",
        "account_mappings",
        str(site_id),
        site_id=site_id,
        details={"mappings_count": len(body.mappings)},
    )

    # Return the updated mapping matrix
    return await get_mapping_matrix(site_id, db, current_user)


__all__ = ["router"]
