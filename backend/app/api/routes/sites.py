from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import AuditLogger, CurrentUser, DbSession, require_role
from app.models.site import Site
from app.models.user import User, UserRole
from app.schemas.site import SiteCreate, SiteListResponse, SiteResponse, SiteUpdate

router = APIRouter(prefix="/sites", tags=["sites"])


def _site_query_for_user(current_user):
    """Return a base select query filtered by user role.

    admin/group_cfo see all active sites; local_cfo sees only assigned sites.
    """
    stmt = select(Site).where(Site.is_active == True)
    if current_user.role == UserRole.local_cfo:
        allowed_ids = [s.id for s in current_user.assigned_sites]
        stmt = stmt.where(Site.id.in_(allowed_ids))
    return stmt


@router.get("", response_model=SiteListResponse)
async def list_sites(
    db: DbSession,
    current_user: CurrentUser,
) -> SiteListResponse:
    """List all sites accessible to the current user."""
    stmt = _site_query_for_user(current_user)
    result = await db.execute(stmt)
    sites = result.scalars().all()

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    return SiteListResponse(
        items=[SiteResponse.model_validate(s) for s in sites],
        total=total,
    )


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    """Get a single site by ID, subject to role-based access."""
    stmt = _site_query_for_user(current_user).where(Site.id == site_id)
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    return SiteResponse.model_validate(site)


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    body: SiteCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    audit_log: AuditLogger,
) -> SiteResponse:
    """Create a new site (admin only)."""
    existing = await db.execute(select(Site).where(Site.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Site name already exists")

    site = Site(
        name=body.name,
        country=body.country,
        local_currency=body.local_currency,
    )
    db.add(site)
    await db.flush()
    await db.refresh(site)

    if audit_log:
        await audit_log("create", "site", str(site.id), site_id=site.id)

    return SiteResponse.model_validate(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: uuid.UUID,
    body: SiteUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    audit_log: AuditLogger,
) -> SiteResponse:
    """Update a site (admin only)."""
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    await db.flush()
    await db.refresh(site)

    if audit_log:
        await audit_log("update", "site", str(site.id), site_id=site.id, details=update_data)

    return SiteResponse.model_validate(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: uuid.UUID,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    audit_log: AuditLogger,
) -> None:
    """Soft-delete a site by marking it inactive (admin only)."""
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    site.is_active = False
    await db.flush()

    if audit_log:
        await audit_log("soft_delete", "site", str(site.id), site_id=site.id)


__all__ = ["router"]
