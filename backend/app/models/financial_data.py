from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatementType(str, enum.Enum):
    income_statement = "income_statement"
    balance_sheet = "balance_sheet"
    cash_flow = "cash_flow"


class StatementStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement_type: Mapped[StatementType] = mapped_column(Enum(StatementType), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[StatementStatus] = mapped_column(
        Enum(StatementStatus), nullable=False, default=StatementStatus.draft
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    site = relationship("Site", back_populates="financial_statements", lazy="selectin")
    line_items = relationship("FinancialLineItem", back_populates="statement", lazy="selectin", cascade="all, delete-orphan")
    uploader = relationship("User", foreign_keys=[uploaded_by], lazy="selectin")
    approver = relationship("User", foreign_keys=[approved_by], lazy="selectin")


class FinancialLineItem(Base):
    __tablename__ = "financial_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    statement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_statements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    line_item_code: Mapped[str] = mapped_column(String(50), nullable=False)
    line_item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    statement = relationship("FinancialStatement", back_populates="line_items")


__all__ = [
    "StatementType",
    "StatementStatus",
    "FinancialStatement",
    "FinancialLineItem",
]
