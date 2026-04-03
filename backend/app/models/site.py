from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.user import user_site_association


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    local_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    assigned_users = relationship("User", secondary=user_site_association, back_populates="assigned_sites", lazy="noload")
    financial_statements = relationship("FinancialStatement", back_populates="site", lazy="noload")
    budget_entries = relationship("BudgetEntry", back_populates="site", lazy="noload")


__all__ = ["Site"]
