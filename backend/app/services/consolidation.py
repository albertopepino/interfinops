from __future__ import annotations

import uuid
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_data import FinancialLineItem, FinancialStatement, StatementType
from app.models.fx_rate import FxRate
from app.models.site import Site
from app.utils.currency import convert_amount

ZERO = Decimal("0")


async def get_fx_rate(
    db: AsyncSession,
    from_currency: str,
    to_currency: str,
    period_year: int,
    period_month: int,
) -> tuple[Decimal, Decimal]:
    """Retrieve closing and average FX rates for a given currency pair and period.

    Returns (closing_rate, average_rate). If from_currency == to_currency, returns (1, 1).
    Raises ValueError if rate not found.
    """
    if from_currency == to_currency:
        return Decimal("1"), Decimal("1")

    stmt = select(FxRate).where(
        FxRate.from_currency == from_currency,
        FxRate.to_currency == to_currency,
        FxRate.period_year == period_year,
        FxRate.period_month == period_month,
    )
    result = await db.execute(stmt)
    rate = result.scalar_one_or_none()

    if rate is None:
        raise ValueError(
            f"FX rate not found for {from_currency}->{to_currency} "
            f"({period_year}-{period_month:02d})"
        )
    return rate.closing_rate, rate.average_rate


def _select_fx_rate_for_statement_type(
    statement_type: StatementType,
    closing_rate: Decimal,
    average_rate: Decimal,
) -> Decimal:
    """Balance sheet uses closing rate; income statement and cash flow use average rate."""
    if statement_type == StatementType.balance_sheet:
        return closing_rate
    return average_rate


async def consolidate_financial_data(
    db: AsyncSession,
    site_ids: list[uuid.UUID],
    period_year: int,
    period_month: int,
    target_currency: str = "EUR",
    eliminate_intercompany: bool = True,
) -> dict[str, dict[str, Decimal]]:
    """Consolidate financial line items across multiple sites into target currency.

    Returns a dict keyed by statement_type -> {line_item_code: aggregated_amount}.
    Applies FX conversion: closing rate for balance sheet, average rate for P&L / cash flow.
    Optionally eliminates intercompany items (codes prefixed with 'IC_').
    """
    stmt = (
        select(FinancialStatement)
        .where(
            FinancialStatement.site_id.in_(site_ids),
            FinancialStatement.period_year == period_year,
            FinancialStatement.period_month == period_month,
        )
    )
    result = await db.execute(stmt)
    statements = result.scalars().all()

    consolidated: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(lambda: ZERO))

    for statement in statements:
        site = statement.site
        from_currency = statement.currency

        closing_rate, average_rate = await get_fx_rate(
            db, from_currency, target_currency, period_year, period_month
        )
        fx_rate = _select_fx_rate_for_statement_type(
            statement.statement_type, closing_rate, average_rate
        )

        for item in statement.line_items:
            if eliminate_intercompany and item.line_item_code.startswith("IC_"):
                continue

            converted = convert_amount(item.amount, fx_rate)
            consolidated[statement.statement_type.value][item.line_item_code] += converted

    return {k: dict(v) for k, v in consolidated.items()}


async def get_site_financial_data(
    db: AsyncSession,
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    target_currency: str | None = None,
) -> dict[str, dict[str, Decimal]]:
    """Get financial data for a single site, optionally converted to a target currency.

    Returns dict keyed by statement_type -> {line_item_code: amount}.
    """
    stmt = (
        select(FinancialStatement)
        .where(
            FinancialStatement.site_id == site_id,
            FinancialStatement.period_year == period_year,
            FinancialStatement.period_month == period_month,
        )
    )
    result = await db.execute(stmt)
    statements = result.scalars().all()

    data: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(lambda: ZERO))

    for statement in statements:
        fx_rate = Decimal("1")
        if target_currency and statement.currency != target_currency:
            closing_rate, average_rate = await get_fx_rate(
                db, statement.currency, target_currency, period_year, period_month
            )
            fx_rate = _select_fx_rate_for_statement_type(
                statement.statement_type, closing_rate, average_rate
            )

        for item in statement.line_items:
            converted = convert_amount(item.amount, fx_rate)
            data[statement.statement_type.value][item.line_item_code] += converted

    return {k: dict(v) for k, v in data.items()}


__all__ = [
    "get_fx_rate",
    "consolidate_financial_data",
    "get_site_financial_data",
]
