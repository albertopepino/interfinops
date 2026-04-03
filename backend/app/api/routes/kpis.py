from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, require_site_access
from app.models.site import Site
from app.models.user import UserRole
from app.schemas.financial import KPIResponse
from app.services.consolidation import consolidate_financial_data, get_site_financial_data
from app.services.kpi import calculate_all_kpis

router = APIRouter(prefix="/kpis", tags=["kpis"])


def _merge_line_items(data: dict[str, dict[str, Decimal]]) -> dict[str, Decimal]:
    """Flatten all statement-type dicts into one code->amount dict for KPI calculation."""
    merged: dict[str, Decimal] = {}
    for items in data.values():
        merged.update(items)
    return merged


@router.get("/site/{site_id}", response_model=KPIResponse)
async def get_site_kpis(
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    db: DbSession,
    current_user: CurrentUser,
    target_currency: str | None = Query(None, min_length=3, max_length=3),
) -> KPIResponse:
    """Calculate KPIs for a single site for the given period."""
    await require_site_access(site_id, current_user)

    # Get site info
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()

    data = await get_site_financial_data(
        db, site_id, period_year, period_month, target_currency
    )

    merged = _merge_line_items(data)
    kpis = calculate_all_kpis(merged)

    currency = target_currency or (site.local_currency if site else "EUR")

    return KPIResponse(
        site_id=site_id,
        site_name=site.name if site else None,
        period_year=period_year,
        period_month=period_month,
        currency=currency,
        profitability=kpis["profitability"],
        liquidity=kpis["liquidity"],
        efficiency=kpis["efficiency"],
        leverage=kpis["leverage"],
    )


@router.get("/consolidated", response_model=KPIResponse)
async def get_consolidated_kpis(
    period_year: int,
    period_month: int,
    db: DbSession,
    current_user: CurrentUser,
    target_currency: str = Query("EUR", min_length=3, max_length=3),
) -> KPIResponse:
    """Calculate consolidated KPIs across all accessible sites."""
    if current_user.role == UserRole.local_cfo:
        site_ids = [s.id for s in current_user.assigned_sites]
    else:
        result = await db.execute(select(Site.id).where(Site.is_active == True))
        site_ids = list(result.scalars().all())

    data = await consolidate_financial_data(
        db, site_ids, period_year, period_month, target_currency
    )

    merged = _merge_line_items(data)
    kpis = calculate_all_kpis(merged)

    return KPIResponse(
        site_id=None,
        site_name="Consolidated",
        period_year=period_year,
        period_month=period_month,
        currency=target_currency,
        profitability=kpis["profitability"],
        liquidity=kpis["liquidity"],
        efficiency=kpis["efficiency"],
        leverage=kpis["leverage"],
    )


__all__ = ["router"]
