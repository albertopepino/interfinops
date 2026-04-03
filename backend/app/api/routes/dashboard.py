from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.dashboard_config import DashboardConfig
from app.schemas.dashboard import DashboardConfigResponse, DashboardConfigUpdate

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/config", response_model=DashboardConfigResponse)
async def get_dashboard_config(
    db: DbSession,
    current_user: CurrentUser,
) -> DashboardConfigResponse:
    """Get the dashboard configuration for the current user.

    Creates a default empty config if none exists.
    """
    result = await db.execute(
        select(DashboardConfig).where(DashboardConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if config is None:
        config = DashboardConfig(
            user_id=current_user.id,
            config_json={},
        )
        db.add(config)
        await db.flush()
        await db.refresh(config)

    return DashboardConfigResponse.model_validate(config)


@router.put("/config", response_model=DashboardConfigResponse)
async def update_dashboard_config(
    body: DashboardConfigUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> DashboardConfigResponse:
    """Update the dashboard configuration for the current user.

    Creates a new config if none exists, otherwise updates the existing one.
    """
    result = await db.execute(
        select(DashboardConfig).where(DashboardConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if config is None:
        config = DashboardConfig(
            user_id=current_user.id,
            config_json=body.config_json,
        )
        db.add(config)
    else:
        config.config_json = body.config_json

    await db.flush()
    await db.refresh(config)

    return DashboardConfigResponse.model_validate(config)


__all__ = ["router"]
