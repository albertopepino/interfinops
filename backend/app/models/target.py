from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KPITarget(Base):
    """KPI targets per site or consolidated (site_id=null)."""

    __tablename__ = "kpi_targets"
    __table_args__ = (
        UniqueConstraint("site_id", "kpi_name", "period_year", "period_month", name="uq_kpi_target"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=True, index=True
    )
    kpi_name: Mapped[str] = mapped_column(String(100), nullable=False)
    kpi_category: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    site = relationship("Site", lazy="selectin")
    creator = relationship("User", lazy="selectin")


__all__ = ["KPITarget"]
