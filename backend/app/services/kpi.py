from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.schemas.financial import KPIValue

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ZERO = Decimal("0")


def _safe_divide(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    """Return numerator / denominator rounded to 4dp, or None if denominator is zero."""
    if denominator == ZERO:
        return None
    try:
        return (numerator / denominator).quantize(Decimal("0.0001"))
    except InvalidOperation:
        return None


def _get(items: dict[str, Decimal], code: str) -> Decimal:
    """Look up a line-item code and return its Decimal amount (default 0)."""
    return items.get(code, ZERO)


def _abs(val: Decimal) -> Decimal:
    """Absolute value helper for expense items stored as negatives."""
    return abs(val)


# ---------------------------------------------------------------------------
# KPI calculation engine
#
# Line-item codes match the financial statement templates:
#   Income Statement: REV, COGS, GP, OPEX, EBIT, EBT, TAX, NI,
#                     OPEX_DA (depreciation), OTH_EXP (interest expense)
#   Balance Sheet:    CA, CA_CASH, CA_AR, CA_INV, CL, CL_AP, CL_STD,
#                     NCA, TA, TL, NCL_LTD, EQ
#   Cash Flow:        CFO, CFI, CFF, NET_CASH, CLOSE_CASH
# ---------------------------------------------------------------------------


def calculate_profitability_kpis(items: dict[str, Decimal]) -> list[KPIValue]:
    revenue = _get(items, "REV")
    gp = _get(items, "GP")
    ebit = _get(items, "EBIT")
    ni = _get(items, "NI")
    da = _abs(_get(items, "OPEX_DA"))

    # Derive EBITDA = EBIT + D&A
    ebitda = ebit + da if ebit != ZERO else ZERO

    return [
        KPIValue(name="Revenue", value=revenue, unit="currency", description="Total Revenue / Net Sales"),
        KPIValue(name="Gross Margin", value=_safe_divide(gp, revenue), unit="percentage", description="Gross Profit / Revenue"),
        KPIValue(name="Operating Margin", value=_safe_divide(ebit, revenue), unit="percentage", description="EBIT / Revenue"),
        KPIValue(name="EBITDA", value=ebitda, unit="currency", description="EBIT + Depreciation & Amortization"),
        KPIValue(name="EBITDA Margin", value=_safe_divide(ebitda, revenue), unit="percentage", description="EBITDA / Revenue"),
        KPIValue(name="Net Profit Margin", value=_safe_divide(ni, revenue), unit="percentage", description="Net Income / Revenue"),
        KPIValue(name="Net Income", value=ni, unit="currency", description="Bottom-line Net Income"),
    ]


def calculate_liquidity_kpis(items: dict[str, Decimal]) -> list[KPIValue]:
    ca = _get(items, "CA")
    cl = _get(items, "CL")
    cash = _get(items, "CA_CASH")
    inventory = _get(items, "CA_INV")
    ar = _get(items, "CA_AR")

    quick_assets = ca - inventory
    working_capital = ca - cl

    return [
        KPIValue(name="Current Ratio", value=_safe_divide(ca, cl), unit="ratio", description="Current Assets / Current Liabilities"),
        KPIValue(name="Quick Ratio", value=_safe_divide(quick_assets, cl), unit="ratio", description="(Current Assets - Inventory) / Current Liabilities"),
        KPIValue(name="Cash Ratio", value=_safe_divide(cash, cl), unit="ratio", description="Cash / Current Liabilities"),
        KPIValue(name="Working Capital", value=working_capital, unit="currency", description="Current Assets - Current Liabilities"),
        KPIValue(name="Cash & Bank", value=cash, unit="currency", description="Cash & Bank Balances"),
    ]


def calculate_efficiency_kpis(items: dict[str, Decimal]) -> list[KPIValue]:
    revenue = _get(items, "REV")
    ar = _get(items, "CA_AR")
    inventory = _get(items, "CA_INV")
    cogs = _abs(_get(items, "COGS"))
    ap = _get(items, "CL_AP")
    ta = _get(items, "TA")

    days = Decimal("365")

    dso = _safe_divide(ar * days, revenue) if revenue != ZERO else None
    dio = _safe_divide(inventory * days, cogs) if cogs != ZERO else None
    dpo = _safe_divide(ap * days, cogs) if cogs != ZERO else None

    ccc = None
    if dso is not None and dio is not None and dpo is not None:
        ccc = dso + dio - dpo

    return [
        KPIValue(name="Asset Turnover", value=_safe_divide(revenue, ta), unit="ratio", description="Revenue / Total Assets"),
        KPIValue(name="AR Turnover", value=_safe_divide(revenue, ar), unit="ratio", description="Revenue / Accounts Receivable"),
        KPIValue(name="Days Sales Outstanding", value=dso, unit="days", description="(AR x 365) / Revenue"),
        KPIValue(name="Inventory Turnover", value=_safe_divide(cogs, inventory), unit="ratio", description="COGS / Inventory"),
        KPIValue(name="Days Inventory Outstanding", value=dio, unit="days", description="(Inventory x 365) / COGS"),
        KPIValue(name="AP Turnover", value=_safe_divide(cogs, ap), unit="ratio", description="COGS / Accounts Payable"),
        KPIValue(name="Days Payable Outstanding", value=dpo, unit="days", description="(AP x 365) / COGS"),
        KPIValue(name="Cash Conversion Cycle", value=ccc, unit="days", description="DSO + DIO - DPO"),
    ]


def calculate_leverage_kpis(items: dict[str, Decimal]) -> list[KPIValue]:
    ta = _get(items, "TA")
    tl = _get(items, "TL")
    eq = _get(items, "EQ")
    ltd = _get(items, "NCL_LTD")
    std = _get(items, "CL_STD")
    cash = _get(items, "CA_CASH")
    ebit = _get(items, "EBIT")
    da = _abs(_get(items, "OPEX_DA"))
    interest = _abs(_get(items, "OTH_EXP"))

    ebitda = ebit + da
    total_debt = ltd + std
    net_debt = total_debt - cash

    return [
        KPIValue(name="Debt-to-Equity", value=_safe_divide(tl, eq), unit="ratio", description="Total Liabilities / Total Equity"),
        KPIValue(name="Debt-to-Assets", value=_safe_divide(tl, ta), unit="ratio", description="Total Liabilities / Total Assets"),
        KPIValue(name="Equity Ratio", value=_safe_divide(eq, ta), unit="percentage", description="Total Equity / Total Assets"),
        KPIValue(name="Net Debt", value=net_debt, unit="currency", description="Total Debt - Cash"),
        KPIValue(name="Net Debt / EBITDA", value=_safe_divide(net_debt, ebitda), unit="ratio", description="(Total Debt - Cash) / EBITDA"),
        KPIValue(name="Interest Coverage", value=_safe_divide(ebitda, interest), unit="ratio", description="EBITDA / Interest Expense"),
    ]


def calculate_all_kpis(line_items: dict[str, Decimal]) -> dict[str, list[KPIValue]]:
    """Calculate every KPI category and return as a dict keyed by category."""
    return {
        "profitability": calculate_profitability_kpis(line_items),
        "liquidity": calculate_liquidity_kpis(line_items),
        "efficiency": calculate_efficiency_kpis(line_items),
        "leverage": calculate_leverage_kpis(line_items),
    }


__all__ = [
    "calculate_profitability_kpis",
    "calculate_liquidity_kpis",
    "calculate_efficiency_kpis",
    "calculate_leverage_kpis",
    "calculate_all_kpis",
]
