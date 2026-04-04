from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, select

from app.api.deps import AuditLogger, CurrentUser, DbSession, require_site_access
from app.models.budget import BudgetEntry
from app.schemas.budget import (
    BudgetEntryCreate,
    BudgetEntryResponse,
    BudgetEntryUpdate,
    BudgetListResponse,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/site/{site_id}", response_model=BudgetListResponse)
async def list_budgets(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    period_year: int | None = Query(None, ge=2000, le=2100),
    period_month: int | None = Query(None, ge=1, le=12),
) -> BudgetListResponse:
    """List budget entries for a site, with optional period filter."""
    await require_site_access(site_id, current_user)

    stmt = select(BudgetEntry).where(BudgetEntry.site_id == site_id)
    if period_year is not None:
        stmt = stmt.where(BudgetEntry.period_year == period_year)
    if period_month is not None:
        stmt = stmt.where(BudgetEntry.period_month == period_month)
    stmt = stmt.order_by(BudgetEntry.period_year.desc(), BudgetEntry.period_month.desc())

    result = await db.execute(stmt)
    entries = result.scalars().all()

    return BudgetListResponse(
        items=[BudgetEntryResponse.model_validate(e) for e in entries],
        total=len(entries),
    )


@router.get("/{budget_id}", response_model=BudgetEntryResponse)
async def get_budget(
    budget_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> BudgetEntryResponse:
    """Get a single budget entry by ID."""
    result = await db.execute(select(BudgetEntry).where(BudgetEntry.id == budget_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget entry not found")

    await require_site_access(entry.site_id, current_user)

    return BudgetEntryResponse.model_validate(entry)


@router.post("", response_model=BudgetEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    body: BudgetEntryCreate,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> BudgetEntryResponse:
    """Create a new budget entry."""
    await require_site_access(body.site_id, current_user)

    entry = BudgetEntry(
        site_id=body.site_id,
        line_item_code=body.line_item_code,
        period_year=body.period_year,
        period_month=body.period_month,
        budget_amount=body.budget_amount,
        created_by=current_user.id,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)

    await audit_log(
        "create",
        "budget_entry",
        str(entry.id),
        site_id=body.site_id,
        details={
            "line_item_code": body.line_item_code,
            "period": f"{body.period_year}-{body.period_month:02d}",
            "amount": str(body.budget_amount),
        },
    )

    return BudgetEntryResponse.model_validate(entry)


@router.post("/bulk", response_model=BudgetListResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_budgets(
    body: list[BudgetEntryCreate],
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> BudgetListResponse:
    """Bulk create/update budget entries."""
    results: list[BudgetEntry] = []
    for entry_data in body:
        await require_site_access(entry_data.site_id, current_user)

        # Upsert: check if exists by (site_id, line_item_code, period_year, period_month)
        existing_result = await db.execute(
            select(BudgetEntry).where(
                and_(
                    BudgetEntry.site_id == entry_data.site_id,
                    BudgetEntry.line_item_code == entry_data.line_item_code,
                    BudgetEntry.period_year == entry_data.period_year,
                    BudgetEntry.period_month == entry_data.period_month,
                )
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing is not None:
            existing.budget_amount = entry_data.budget_amount
            await db.flush()
            await db.refresh(existing)
            results.append(existing)
        else:
            entry = BudgetEntry(
                site_id=entry_data.site_id,
                line_item_code=entry_data.line_item_code,
                period_year=entry_data.period_year,
                period_month=entry_data.period_month,
                budget_amount=entry_data.budget_amount,
                created_by=current_user.id,
            )
            db.add(entry)
            await db.flush()
            await db.refresh(entry)
            results.append(entry)

    await audit_log(
        "bulk_create",
        "budget_entry",
        "",
        details={"count": len(results)},
    )

    return BudgetListResponse(
        items=[BudgetEntryResponse.model_validate(e) for e in results],
        total=len(results),
    )


@router.put("/{budget_id}", response_model=BudgetEntryResponse)
async def update_budget(
    budget_id: uuid.UUID,
    body: BudgetEntryUpdate,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> BudgetEntryResponse:
    """Update a budget entry amount."""
    result = await db.execute(select(BudgetEntry).where(BudgetEntry.id == budget_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget entry not found")

    await require_site_access(entry.site_id, current_user)

    old_amount = entry.budget_amount
    entry.budget_amount = body.budget_amount
    await db.flush()
    await db.refresh(entry)

    await audit_log(
        "update",
        "budget_entry",
        str(entry.id),
        site_id=entry.site_id,
        details={"old_amount": str(old_amount), "new_amount": str(body.budget_amount)},
    )

    return BudgetEntryResponse.model_validate(entry)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> None:
    """Delete a budget entry."""
    result = await db.execute(select(BudgetEntry).where(BudgetEntry.id == budget_id))
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget entry not found")

    await require_site_access(entry.site_id, current_user)

    await audit_log("delete", "budget_entry", str(entry.id), site_id=entry.site_id)

    await db.delete(entry)
    await db.flush()


__all__ = ["router"]
