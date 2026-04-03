from __future__ import annotations

import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession, get_client_ip, get_db
from app.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.audit import create_audit_log
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set HTTP-only secure cookies for access and refresh tokens."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth",
    )


def _clear_auth_cookies(response: Response) -> None:
    """Clear authentication cookies."""
    response.delete_cookie("access_token", path="/", domain=settings.COOKIE_DOMAIN)
    response.delete_cookie("refresh_token", path="/api/auth", domain=settings.COOKIE_DOMAIN)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    """Authenticate user with email/password and set HTTP-only auth cookies."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    _set_auth_cookies(response, access_token, refresh_token)

    await create_audit_log(
        db,
        user_id=user.id,
        action="login",
        resource_type="auth",
        resource_id=str(user.id),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
    )

    return TokenResponse()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: DbSession,
) -> UserResponse:
    """Register a new user. Only admins should call this in production (enforced by middleware/policy)."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    await create_audit_log(
        db,
        user_id=user.id,
        action="register",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        assigned_site_ids=[s.id for s in user.assigned_sites],
    )


@router.post("/logout", response_model=TokenResponse)
async def logout(
    request: Request,
    response: Response,
    db: DbSession,
    current_user: CurrentUser,
) -> TokenResponse:
    """Clear auth cookies to log out."""
    _clear_auth_cookies(response)

    await create_audit_log(
        db,
        user_id=current_user.id,
        action="logout",
        resource_type="auth",
        resource_id=str(current_user.id),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
    )

    return TokenResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: DbSession,
    refresh_token: str | None = Cookie(None),
) -> TokenResponse:
    """Rotate tokens using the refresh token cookie."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )

    try:
        payload = verify_refresh_token(refresh_token)
    except JWTError:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access = create_access_token(user.id, user.role.value)
    new_refresh = create_refresh_token(user.id)
    _set_auth_cookies(response, new_access, new_refresh)

    return TokenResponse(message="Tokens refreshed")


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        assigned_site_ids=[s.id for s in current_user.assigned_sites],
    )


__all__ = ["router"]
