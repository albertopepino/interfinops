from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_log(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: str,
    site_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Write an append-only audit log entry.

    This should be called for every security-relevant or data-mutating action.
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        site_id=site_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )
    db.add(entry)
    await db.flush()
    return entry


__all__ = ["create_audit_log"]
