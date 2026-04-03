from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, select

from app.api.deps import AuditLogger, CurrentUser, DbSession, require_site_access
from app.models.target import KPITarget
from app.models.user import UserRole
from app.schemas.target import (
    TargetCreate,
    TargetListResponse,
    TargetResponse,
    TargetUpdate,
)

router = APIRouter(prefix="/targets", tags=["targets"])


def _can_set_overall(user) -> bool:
    """Only admin and group_cfo can set overall (site_id=null) targets."""
    return user.role in (UserRole.admin, UserRole.group_cfo)


async def _check_target_write_permission(
    site_id: uuid.UUID | None,
    current_user,
) -> None:
    """Verify the user has permission to write a target for the given scope."""
    if site_id is None:
        if not _can_set_overall(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin and group_cfo can set overall targets",
            )
    else:
        # Reuse the existing site access check
        await require_site_access(site_id, current_user)


@router.get("", response_model=TargetListResponse)
async def list_targets(
    db: DbSession,
    current_user: CurrentUser,
    site_id: uuid.UUID | None = Query(None, description="Filter by site; omit for all, use explicit null for overall"),
    period_year: int | None = Query(None, ge=2000, le=2100),
    overall_only: bool = Query(False, description="If true, only return overall targets (site_id IS NULL)"),
) -> TargetListResponse:
    """List KPI targets, filtered by site_id and/or year."""
    stmt = select(KPITarget)

    if overall_only:
        stmt = stmt.where(KPITarget.site_id.is_(None))
    elif site_id is not None:
        stmt = stmt.where(KPITarget.site_id == site_id)

    if period_year is not None:
        stmt = stmt.where(KPITarget.period_year == period_year)

    stmt = stmt.order_by(KPITarget.kpi_category, KPITarget.kpi_name, KPITarget.period_year.desc())

    result = await db.execute(stmt)
    targets = result.scalars().all()

    return TargetListResponse(
        items=[TargetResponse.model_validate(t) for t in targets],
        total=len(targets),
    )


@router.post("", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    body: TargetCreate,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> TargetResponse:
    """Create or upsert a KPI target (upsert on unique constraint)."""
    await _check_target_write_permission(body.site_id, current_user)

    # Check for existing target matching the unique constraint
    filters = [
        KPITarget.kpi_name == body.kpi_name,
        KPITarget.period_year == body.period_year,
    ]
    if body.site_id is None:
        filters.append(KPITarget.site_id.is_(None))
    else:
        filters.append(KPITarget.site_id == body.site_id)
    if body.period_month is None:
        filters.append(KPITarget.period_month.is_(None))
    else:
        filters.append(KPITarget.period_month == body.period_month)

    result = await db.execute(select(KPITarget).where(and_(*filters)))
    existing = result.scalar_one_or_none()

    if existing is not None:
        # Upsert: update the existing target
        existing.target_value = body.target_value
        existing.kpi_category = body.kpi_category
        await db.flush()
        await db.refresh(existing)

        await audit_log(
            "update",
            "kpi_target",
            str(existing.id),
            site_id=body.site_id,
            details={"kpi_name": body.kpi_name, "target_value": str(body.target_value)},
        )
        return TargetResponse.model_validate(existing)

    target = KPITarget(
        site_id=body.site_id,
        kpi_name=body.kpi_name,
        kpi_category=body.kpi_category,
        target_value=body.target_value,
        period_year=body.period_year,
        period_month=body.period_month,
        created_by=current_user.id,
    )
    db.add(target)
    await db.flush()
    await db.refresh(target)

    await audit_log(
        "create",
        "kpi_target",
        str(target.id),
        site_id=body.site_id,
        details={
            "kpi_name": body.kpi_name,
            "target_value": str(body.target_value),
            "period_year": body.period_year,
        },
    )

    return TargetResponse.model_validate(target)


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: uuid.UUID,
    body: TargetUpdate,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> TargetResponse:
    """Update a KPI target value."""
    result = await db.execute(select(KPITarget).where(KPITarget.id == target_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    await _check_target_write_permission(target.site_id, current_user)

    old_value = target.target_value
    target.target_value = body.target_value
    await db.flush()
    await db.refresh(target)

    await audit_log(
        "update",
        "kpi_target",
        str(target.id),
        site_id=target.site_id,
        details={"old_value": str(old_value), "new_value": str(body.target_value)},
    )

    return TargetResponse.model_validate(target)


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> None:
    """Delete a KPI target."""
    result = await db.execute(select(KPITarget).where(KPITarget.id == target_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    await _check_target_write_permission(target.site_id, current_user)

    await audit_log("delete", "kpi_target", str(target.id), site_id=target.site_id)

    await db.delete(target)
    await db.flush()


@router.post("/bulk", response_model=TargetListResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_targets(
    body: list[TargetCreate],
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> TargetListResponse:
    """Bulk create or update KPI targets."""
    results: list[TargetResponse] = []

    for item in body:
        await _check_target_write_permission(item.site_id, current_user)

        # Check for existing target matching the unique constraint
        filters = [
            KPITarget.kpi_name == item.kpi_name,
            KPITarget.period_year == item.period_year,
        ]
        if item.site_id is None:
            filters.append(KPITarget.site_id.is_(None))
        else:
            filters.append(KPITarget.site_id == item.site_id)
        if item.period_month is None:
            filters.append(KPITarget.period_month.is_(None))
        else:
            filters.append(KPITarget.period_month == item.period_month)

        result = await db.execute(select(KPITarget).where(and_(*filters)))
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.target_value = item.target_value
            existing.kpi_category = item.kpi_category
            await db.flush()
            await db.refresh(existing)

            await audit_log(
                "update",
                "kpi_target",
                str(existing.id),
                site_id=item.site_id,
                details={"kpi_name": item.kpi_name, "target_value": str(item.target_value)},
            )
            results.append(TargetResponse.model_validate(existing))
        else:
            target = KPITarget(
                site_id=item.site_id,
                kpi_name=item.kpi_name,
                kpi_category=item.kpi_category,
                target_value=item.target_value,
                period_year=item.period_year,
                period_month=item.period_month,
                created_by=current_user.id,
            )
            db.add(target)
            await db.flush()
            await db.refresh(target)

            await audit_log(
                "create",
                "kpi_target",
                str(target.id),
                site_id=item.site_id,
                details={"kpi_name": item.kpi_name, "target_value": str(item.target_value)},
            )
            results.append(TargetResponse.model_validate(target))

    return TargetListResponse(items=results, total=len(results))


__all__ = ["router"]
