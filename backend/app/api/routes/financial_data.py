from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession, require_site_access
from app.models.financial_data import FinancialStatement, StatementType
from app.models.site import Site
from app.models.user import UserRole
from app.schemas.financial import (
    FinancialStatementListResponse,
    FinancialStatementResponse,
)
from app.services.consolidation import consolidate_financial_data, get_site_financial_data

router = APIRouter(prefix="/financial-data", tags=["financial-data"])


def _accessible_site_ids(current_user) -> list[uuid.UUID] | None:
    """Return a list of site IDs the user can access, or None for unrestricted."""
    if current_user.role == UserRole.local_cfo:
        return [s.id for s in current_user.assigned_sites]
    return None


@router.get("/site/{site_id}", response_model=FinancialStatementListResponse)
async def get_site_statements(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    period_year: int | None = Query(None, ge=2000, le=2100),
    period_month: int | None = Query(None, ge=1, le=12),
    statement_type: StatementType | None = Query(None),
) -> FinancialStatementListResponse:
    """Get financial statements for a specific site, with optional period/type filters."""
    await require_site_access(site_id, current_user)

    stmt = select(FinancialStatement).where(FinancialStatement.site_id == site_id)

    if period_year is not None:
        stmt = stmt.where(FinancialStatement.period_year == period_year)
    if period_month is not None:
        stmt = stmt.where(FinancialStatement.period_month == period_month)
    if statement_type is not None:
        stmt = stmt.where(FinancialStatement.statement_type == statement_type)

    stmt = stmt.order_by(
        FinancialStatement.period_year.desc(),
        FinancialStatement.period_month.desc(),
    )

    result = await db.execute(stmt)
    statements = result.scalars().all()

    return FinancialStatementListResponse(
        items=[FinancialStatementResponse.model_validate(s) for s in statements],
        total=len(statements),
    )


@router.get("/statement/{statement_id}", response_model=FinancialStatementResponse)
async def get_statement(
    statement_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> FinancialStatementResponse:
    """Get a single financial statement by ID."""
    result = await db.execute(
        select(FinancialStatement).where(FinancialStatement.id == statement_id)
    )
    statement = result.scalar_one_or_none()

    if statement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    await require_site_access(statement.site_id, current_user)

    return FinancialStatementResponse.model_validate(statement)


@router.get("/site/{site_id}/data")
async def get_site_data(
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    db: DbSession,
    current_user: CurrentUser,
    target_currency: str | None = Query(None, min_length=3, max_length=3),
) -> dict[str, dict[str, str]]:
    """Get aggregated financial line item data for a site.

    Optionally convert to a target currency. Returns
    {statement_type: {line_item_code: amount_string}}.
    """
    await require_site_access(site_id, current_user)

    data = await get_site_financial_data(
        db, site_id, period_year, period_month, target_currency
    )

    # Serialize Decimal values to strings to preserve precision
    return {
        st: {code: str(amt) for code, amt in items.items()}
        for st, items in data.items()
    }


@router.get("/consolidated")
async def get_consolidated_data(
    period_year: int,
    period_month: int,
    db: DbSession,
    current_user: CurrentUser,
    target_currency: str = Query("EUR", min_length=3, max_length=3),
) -> dict[str, dict[str, str]]:
    """Get consolidated financial data across all accessible sites.

    Applies FX conversion (closing rate for BS, average rate for P&L).
    Intercompany items (IC_ prefix) are eliminated.
    """
    allowed_ids = _accessible_site_ids(current_user)

    if allowed_ids is not None:
        site_ids = allowed_ids
    else:
        result = await db.execute(select(Site.id).where(Site.is_active == True))
        site_ids = list(result.scalars().all())

    if not site_ids:
        return {}

    data = await consolidate_financial_data(
        db, site_ids, period_year, period_month, target_currency
    )

    return {
        st: {code: str(amt) for code, amt in items.items()}
        for st, items in data.items()
    }


@router.post("/statement/{statement_id}/approve", response_model=FinancialStatementResponse)
async def approve_statement(
    statement_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> FinancialStatementResponse:
    """Approve a financial statement (admin/group_cfo only)."""
    from datetime import datetime, timezone

    from app.models.financial_data import StatementStatus

    if current_user.role not in (UserRole.admin, UserRole.group_cfo):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or group_cfo can approve statements",
        )

    result = await db.execute(
        select(FinancialStatement).where(FinancialStatement.id == statement_id)
    )
    statement = result.scalar_one_or_none()
    if statement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    statement.status = StatementStatus.approved
    statement.approved_by = current_user.id
    statement.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(statement)

    return FinancialStatementResponse.model_validate(statement)


__all__ = ["router"]
