from __future__ import annotations

import uuid
from typing import Annotated, AsyncGenerator, Callable

from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.user import User, UserRole
from app.services.audit import create_audit_log
from app.services.auth import verify_access_token


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, rolling back on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """Extract and verify the JWT from the HTTP-only access_token cookie.

    Returns the authenticated User object. Raises 401 if token is missing/invalid
    or the user is inactive.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = verify_access_token(access_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """Return a dependency that enforces the user has one of the allowed roles."""

    async def _check_role(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role


async def require_site_access(
    site_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Verify the current user can access the given site.

    - admin and group_cfo have access to all sites.
    - local_cfo only has access to their assigned sites.
    """
    if current_user.role in (UserRole.admin, UserRole.group_cfo):
        return current_user

    assigned_ids = {s.id for s in current_user.assigned_sites}
    if site_id not in assigned_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this site",
        )
    return current_user


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, respecting X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def get_audit_logger(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Callable:
    """Return a callable that creates audit log entries pre-filled with request context."""
    ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "")

    async def _log(
        action: str,
        resource_type: str,
        resource_id: str,
        site_id: uuid.UUID | None = None,
        details: dict | None = None,
    ) -> None:
        await create_audit_log(
            db,
            user_id=current_user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            site_id=site_id,
            ip_address=ip,
            user_agent=ua,
            details=details,
        )

    return _log


# Convenience type aliases for use in route signatures
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AuditLogger = Annotated[Callable, Depends(get_audit_logger)]

__all__ = [
    "get_db",
    "get_current_user",
    "require_role",
    "require_site_access",
    "get_audit_logger",
    "get_client_ip",
    "DbSession",
    "CurrentUser",
    "AuditLogger",
]
