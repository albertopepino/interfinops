"""
Seed script: creates demo data for local development.

Usage:
    cd backend && source .venv/bin/activate
    PYTHONPATH=. python scripts/seed.py
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, engine
from app.models import (
    BudgetEntry,
    FinancialLineItem,
    FinancialStatement,
    FxRate,
    Site,
    StatementStatus,
    StatementType,
    User,
    UserRole,
    user_site_association,
)
from app.services.auth import hash_password

# ---------------------------------------------------------------------------
# Fixed UUIDs for reproducibility
# ---------------------------------------------------------------------------
ADMIN_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
GROUP_CFO_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")
LOCAL_CFO_US_ID = uuid.UUID("00000000-0000-4000-8000-000000000003")
LOCAL_CFO_UK_ID = uuid.UUID("00000000-0000-4000-8000-000000000004")
LOCAL_CFO_DE_ID = uuid.UUID("00000000-0000-4000-8000-000000000005")

SITE_US_ID = uuid.UUID("00000000-0000-4000-8000-000000000010")
SITE_UK_ID = uuid.UUID("00000000-0000-4000-8000-000000000011")
SITE_DE_ID = uuid.UUID("00000000-0000-4000-8000-000000000012")

PASSWORD = "Demo1234!@#$"  # All demo users share this password


# ---------------------------------------------------------------------------
# Income statement line items per site (monthly figures)
# ---------------------------------------------------------------------------
def income_statement_lines(site_key: str, month: int) -> list[dict]:
    """Return realistic income statement line items. Amounts vary by site and month."""
    # Base multipliers per site
    mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]
    # Slight monthly variation
    seasonal = Decimal("1.0") + Decimal(str((month % 3) * 0.05))

    def amt(base: float) -> Decimal:
        return (Decimal(str(base)) * mult * seasonal).quantize(Decimal("0.01"))

    return [
        {"code": "REV", "name": "Revenue / Net Sales", "parent": None, "amount": amt(2_500_000)},
        {"code": "REV_GOODS", "name": "Sales of Goods", "parent": "REV", "amount": amt(1_800_000)},
        {"code": "REV_SERVICES", "name": "Sales of Services", "parent": "REV", "amount": amt(600_000)},
        {"code": "REV_OTHER", "name": "Other Revenue", "parent": "REV", "amount": amt(100_000)},
        {"code": "COGS", "name": "Cost of Goods Sold", "parent": None, "amount": amt(-1_200_000)},
        {"code": "COGS_RAW", "name": "Raw Materials", "parent": "COGS", "amount": amt(-700_000)},
        {"code": "COGS_LABOR", "name": "Direct Labor", "parent": "COGS", "amount": amt(-350_000)},
        {"code": "COGS_OH", "name": "Manufacturing Overhead", "parent": "COGS", "amount": amt(-150_000)},
        {"code": "GP", "name": "Gross Profit", "parent": None, "amount": amt(1_300_000)},
        {"code": "OPEX", "name": "Operating Expenses", "parent": None, "amount": amt(-850_000)},
        {"code": "OPEX_SAL", "name": "Salaries & Wages", "parent": "OPEX", "amount": amt(-450_000)},
        {"code": "OPEX_RENT", "name": "Rent & Utilities", "parent": "OPEX", "amount": amt(-120_000)},
        {"code": "OPEX_DA", "name": "Depreciation & Amortization", "parent": "OPEX", "amount": amt(-80_000)},
        {"code": "OPEX_MKT", "name": "Marketing & Advertising", "parent": "OPEX", "amount": amt(-90_000)},
        {"code": "OPEX_PROF", "name": "Professional Fees", "parent": "OPEX", "amount": amt(-40_000)},
        {"code": "OPEX_TRAVEL", "name": "Travel & Entertainment", "parent": "OPEX", "amount": amt(-30_000)},
        {"code": "OPEX_INS", "name": "Insurance", "parent": "OPEX", "amount": amt(-25_000)},
        {"code": "OPEX_OTHER", "name": "Other Operating Expenses", "parent": "OPEX", "amount": amt(-15_000)},
        {"code": "EBIT", "name": "Operating Income (EBIT)", "parent": None, "amount": amt(450_000)},
        {"code": "OTH_INC", "name": "Interest Income", "parent": None, "amount": amt(5_000)},
        {"code": "OTH_EXP", "name": "Interest Expense", "parent": None, "amount": amt(-25_000)},
        {"code": "OTH_FX", "name": "FX Gains / Losses", "parent": None, "amount": amt(-3_000)},
        {"code": "IC_INC", "name": "Intercompany Income", "parent": None, "amount": amt(50_000)},
        {"code": "IC_EXP", "name": "Intercompany Expenses", "parent": None, "amount": amt(-30_000)},
        {"code": "EBT", "name": "Earnings Before Tax", "parent": None, "amount": amt(447_000)},
        {"code": "TAX", "name": "Income Tax", "parent": None, "amount": amt(-112_000)},
        {"code": "NI", "name": "Net Income", "parent": None, "amount": amt(335_000)},
    ]


def balance_sheet_lines(site_key: str, month: int) -> list[dict]:
    """Return realistic balance sheet line items."""
    mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]

    def amt(base: float) -> Decimal:
        return (Decimal(str(base)) * mult).quantize(Decimal("0.01"))

    return [
        # Current Assets
        {"code": "CA", "name": "Current Assets", "parent": None, "amount": amt(8_500_000)},
        {"code": "CA_CASH", "name": "Cash & Bank Balances", "parent": "CA", "amount": amt(2_100_000)},
        {"code": "CA_AR", "name": "Accounts Receivable (Trade)", "parent": "CA", "amount": amt(3_200_000)},
        {"code": "CA_IC_AR", "name": "Intercompany Receivables", "parent": "CA", "amount": amt(800_000)},
        {"code": "CA_INV", "name": "Inventory", "parent": "CA", "amount": amt(1_900_000)},
        {"code": "CA_PREPAID", "name": "Prepaid Expenses", "parent": "CA", "amount": amt(350_000)},
        {"code": "CA_OTHER", "name": "Other Current Assets", "parent": "CA", "amount": amt(150_000)},
        # Non-Current Assets
        {"code": "NCA", "name": "Non-Current Assets", "parent": None, "amount": amt(12_000_000)},
        {"code": "NCA_PPE", "name": "Property, Plant & Equipment", "parent": "NCA", "amount": amt(9_500_000)},
        {"code": "NCA_INTANG", "name": "Intangible Assets", "parent": "NCA", "amount": amt(1_500_000)},
        {"code": "NCA_INVEST", "name": "Long-term Investments", "parent": "NCA", "amount": amt(700_000)},
        {"code": "NCA_DEP", "name": "Deposits & Advances", "parent": "NCA", "amount": amt(200_000)},
        {"code": "NCA_OTHER", "name": "Other Non-Current Assets", "parent": "NCA", "amount": amt(100_000)},
        {"code": "TA", "name": "Total Assets", "parent": None, "amount": amt(20_500_000)},
        # Current Liabilities
        {"code": "CL", "name": "Current Liabilities", "parent": None, "amount": amt(5_200_000)},
        {"code": "CL_AP", "name": "Accounts Payable (Trade)", "parent": "CL", "amount": amt(2_100_000)},
        {"code": "CL_IC_AP", "name": "Intercompany Payables", "parent": "CL", "amount": amt(600_000)},
        {"code": "CL_STD", "name": "Short-term Debt", "parent": "CL", "amount": amt(1_200_000)},
        {"code": "CL_ACCR", "name": "Accrued Expenses", "parent": "CL", "amount": amt(500_000)},
        {"code": "CL_WAGES", "name": "Wages Payable", "parent": "CL", "amount": amt(400_000)},
        {"code": "CL_TAX", "name": "Taxes Payable", "parent": "CL", "amount": amt(300_000)},
        {"code": "CL_OTHER", "name": "Other Current Liabilities", "parent": "CL", "amount": amt(100_000)},
        # Non-Current Liabilities
        {"code": "NCL", "name": "Non-Current Liabilities", "parent": None, "amount": amt(5_800_000)},
        {"code": "NCL_LTD", "name": "Long-term Debt", "parent": "NCL", "amount": amt(4_500_000)},
        {"code": "NCL_PROV", "name": "Provisions & Accruals", "parent": "NCL", "amount": amt(900_000)},
        {"code": "NCL_OTHER", "name": "Other Non-Current Liabilities", "parent": "NCL", "amount": amt(400_000)},
        {"code": "TL", "name": "Total Liabilities", "parent": None, "amount": amt(11_000_000)},
        # Equity
        {"code": "EQ", "name": "Total Equity", "parent": None, "amount": amt(9_500_000)},
        {"code": "EQ_SC", "name": "Share Capital", "parent": "EQ", "amount": amt(3_000_000)},
        {"code": "EQ_RE", "name": "Retained Earnings", "parent": "EQ", "amount": amt(5_800_000)},
        {"code": "EQ_RES", "name": "Other Reserves", "parent": "EQ", "amount": amt(500_000)},
        {"code": "EQ_FX", "name": "FX Translation Reserve", "parent": "EQ", "amount": amt(200_000)},
        {"code": "TLE", "name": "Total Liabilities + Equity", "parent": None, "amount": amt(20_500_000)},
    ]


def cash_flow_lines(site_key: str, month: int) -> list[dict]:
    """Return realistic cash flow statement line items."""
    mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]

    def amt(base: float) -> Decimal:
        return (Decimal(str(base)) * mult).quantize(Decimal("0.01"))

    return [
        {"code": "CFO", "name": "Net Cash from Operations", "parent": None, "amount": amt(520_000)},
        {"code": "CFO_NI", "name": "Net Income", "parent": "CFO", "amount": amt(335_000)},
        {"code": "CFO_DA", "name": "Depreciation & Amortization", "parent": "CFO", "amount": amt(80_000)},
        {"code": "CFO_AR", "name": "Change in Accounts Receivable", "parent": "CFO", "amount": amt(-45_000)},
        {"code": "CFO_INV", "name": "Change in Inventory", "parent": "CFO", "amount": amt(-30_000)},
        {"code": "CFO_AP", "name": "Change in Accounts Payable", "parent": "CFO", "amount": amt(60_000)},
        {"code": "CFO_OTHER", "name": "Change in Other Current Items", "parent": "CFO", "amount": amt(120_000)},
        {"code": "CFI", "name": "Net Cash from Investing", "parent": None, "amount": amt(-200_000)},
        {"code": "CFI_CAPEX", "name": "Capital Expenditures", "parent": "CFI", "amount": amt(-250_000)},
        {"code": "CFI_INVEST", "name": "Acquisition of Investments", "parent": "CFI", "amount": amt(-20_000)},
        {"code": "CFI_SALE", "name": "Proceeds from Asset Sales", "parent": "CFI", "amount": amt(70_000)},
        {"code": "CFF", "name": "Net Cash from Financing", "parent": None, "amount": amt(-150_000)},
        {"code": "CFF_DEBT_IN", "name": "Proceeds from Debt", "parent": "CFF", "amount": amt(100_000)},
        {"code": "CFF_DEBT_OUT", "name": "Repayment of Debt", "parent": "CFF", "amount": amt(-180_000)},
        {"code": "CFF_DIV", "name": "Dividends Paid", "parent": "CFF", "amount": amt(-50_000)},
        {"code": "CFF_IC", "name": "Intercompany Loans (Net)", "parent": "CFF", "amount": amt(-20_000)},
        {"code": "NET_CASH", "name": "Net Change in Cash", "parent": None, "amount": amt(170_000)},
        {"code": "OPEN_CASH", "name": "Opening Cash Balance", "parent": None, "amount": amt(1_930_000)},
        {"code": "CLOSE_CASH", "name": "Closing Cash Balance", "parent": None, "amount": amt(2_100_000)},
    ]


# ---------------------------------------------------------------------------
# FX rates (monthly, to EUR)
# ---------------------------------------------------------------------------
FX_RATES = [
    # USD to EUR
    {"from": "USD", "to": "EUR", "months": {
        1: (0.92, 0.915), 2: (0.91, 0.912), 3: (0.93, 0.920),
        4: (0.92, 0.918), 5: (0.91, 0.915), 6: (0.90, 0.908),
        7: (0.89, 0.895), 8: (0.90, 0.898), 9: (0.91, 0.905),
        10: (0.92, 0.915), 11: (0.93, 0.925), 12: (0.94, 0.935),
    }},
    # GBP to EUR
    {"from": "GBP", "to": "EUR", "months": {
        1: (1.16, 1.155), 2: (1.17, 1.165), 3: (1.16, 1.160),
        4: (1.15, 1.155), 5: (1.16, 1.158), 6: (1.17, 1.165),
        7: (1.18, 1.175), 8: (1.17, 1.170), 9: (1.16, 1.165),
        10: (1.15, 1.155), 11: (1.16, 1.158), 12: (1.17, 1.165),
    }},
    # EUR to EUR (identity)
    {"from": "EUR", "to": "EUR", "months": {m: (1.0, 1.0) for m in range(1, 13)}},
]


async def seed() -> None:
    async with async_session_factory() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT count(*) FROM users"))
        count = result.scalar()
        if count and count > 0:
            print("Database already seeded. Truncating and re-seeding...")
            for tbl in [
                "financial_line_items", "financial_statements", "budget_entries",
                "dashboard_configs", "audit_logs", "fx_rates", "user_site", "users", "sites",
            ]:
                await session.execute(text(f"TRUNCATE TABLE {tbl} CASCADE"))
            await session.commit()

        # ----- Sites -----
        sites = [
            Site(id=SITE_US_ID, name="InterFinOps US", country="United States", local_currency="USD", is_active=True),
            Site(id=SITE_UK_ID, name="InterFinOps UK", country="United Kingdom", local_currency="GBP", is_active=True),
            Site(id=SITE_DE_ID, name="InterFinOps DE", country="Germany", local_currency="EUR", is_active=True),
        ]
        session.add_all(sites)
        await session.flush()

        # ----- Users -----
        hashed_pw = hash_password(PASSWORD)
        users = [
            User(id=ADMIN_ID, email="admin@interfinops.com", hashed_password=hashed_pw,
                 full_name="System Admin", role=UserRole.admin),
            User(id=GROUP_CFO_ID, email="group.cfo@interfinops.com", hashed_password=hashed_pw,
                 full_name="Maria Rossi", role=UserRole.group_cfo),
            User(id=LOCAL_CFO_US_ID, email="cfo.us@interfinops.com", hashed_password=hashed_pw,
                 full_name="James Wilson", role=UserRole.local_cfo),
            User(id=LOCAL_CFO_UK_ID, email="cfo.uk@interfinops.com", hashed_password=hashed_pw,
                 full_name="Sarah Thompson", role=UserRole.local_cfo),
            User(id=LOCAL_CFO_DE_ID, email="cfo.de@interfinops.com", hashed_password=hashed_pw,
                 full_name="Klaus Mueller", role=UserRole.local_cfo),
        ]
        session.add_all(users)
        await session.flush()

        # ----- User-Site assignments -----
        await session.execute(user_site_association.insert().values([
            {"user_id": LOCAL_CFO_US_ID, "site_id": SITE_US_ID},
            {"user_id": LOCAL_CFO_UK_ID, "site_id": SITE_UK_ID},
            {"user_id": LOCAL_CFO_DE_ID, "site_id": SITE_DE_ID},
        ]))

        # ----- FX Rates (2025) -----
        for rate_def in FX_RATES:
            for month, (closing, average) in rate_def["months"].items():
                session.add(FxRate(
                    from_currency=rate_def["from"],
                    to_currency=rate_def["to"],
                    period_year=2025,
                    period_month=month,
                    closing_rate=Decimal(str(closing)),
                    average_rate=Decimal(str(average)),
                ))
        await session.flush()

        # ----- Financial Statements (6 months: Jul-Dec 2025) -----
        site_map = [
            ("US", SITE_US_ID, "USD", LOCAL_CFO_US_ID),
            ("UK", SITE_UK_ID, "GBP", LOCAL_CFO_UK_ID),
            ("DE", SITE_DE_ID, "EUR", LOCAL_CFO_DE_ID),
        ]

        for site_key, site_id, currency, uploader_id in site_map:
            for month in range(7, 13):  # Jul through Dec
                # Income Statement
                is_stmt = FinancialStatement(
                    site_id=site_id, statement_type=StatementType.income_statement,
                    period_year=2025, period_month=month, currency=currency,
                    status=StatementStatus.approved, uploaded_by=uploader_id,
                    approved_by=GROUP_CFO_ID,
                    approved_at=datetime(2025, month, 28, tzinfo=timezone.utc),
                )
                session.add(is_stmt)
                await session.flush()
                for line in income_statement_lines(site_key, month):
                    session.add(FinancialLineItem(
                        statement_id=is_stmt.id,
                        line_item_code=line["code"],
                        line_item_name=line["name"],
                        parent_code=line["parent"],
                        amount=line["amount"],
                    ))

                # Balance Sheet
                bs_stmt = FinancialStatement(
                    site_id=site_id, statement_type=StatementType.balance_sheet,
                    period_year=2025, period_month=month, currency=currency,
                    status=StatementStatus.approved, uploaded_by=uploader_id,
                    approved_by=GROUP_CFO_ID,
                    approved_at=datetime(2025, month, 28, tzinfo=timezone.utc),
                )
                session.add(bs_stmt)
                await session.flush()
                for line in balance_sheet_lines(site_key, month):
                    session.add(FinancialLineItem(
                        statement_id=bs_stmt.id,
                        line_item_code=line["code"],
                        line_item_name=line["name"],
                        parent_code=line["parent"],
                        amount=line["amount"],
                    ))

                # Cash Flow
                cf_stmt = FinancialStatement(
                    site_id=site_id, statement_type=StatementType.cash_flow,
                    period_year=2025, period_month=month, currency=currency,
                    status=StatementStatus.approved, uploaded_by=uploader_id,
                    approved_by=GROUP_CFO_ID,
                    approved_at=datetime(2025, month, 28, tzinfo=timezone.utc),
                )
                session.add(cf_stmt)
                await session.flush()
                for line in cash_flow_lines(site_key, month):
                    session.add(FinancialLineItem(
                        statement_id=cf_stmt.id,
                        line_item_code=line["code"],
                        line_item_name=line["name"],
                        parent_code=line["parent"],
                        amount=line["amount"],
                    ))

        # ----- Budget Entries (2025, all months) -----
        budget_lines = [
            ("REV", 2_600_000), ("COGS", -1_250_000), ("GP", 1_350_000),
            ("OPEX", -870_000), ("EBIT", 480_000), ("NI", 360_000),
        ]
        for site_key, site_id, currency, uploader_id in site_map:
            mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]
            for month in range(1, 13):
                for code, base_amount in budget_lines:
                    session.add(BudgetEntry(
                        site_id=site_id,
                        line_item_code=code,
                        period_year=2025,
                        period_month=month,
                        budget_amount=(Decimal(str(base_amount)) * mult).quantize(Decimal("0.01")),
                        created_by=uploader_id,
                    ))

        await session.commit()
        print("Seed complete!")
        print(f"  Sites: 3 (US, UK, DE)")
        print(f"  Users: 5 (admin, group_cfo, 3x local_cfo)")
        print(f"  Password for all: {PASSWORD}")
        print(f"  Financial statements: 54 (3 sites x 6 months x 3 types)")
        print(f"  FX rates: 36 (3 pairs x 12 months)")
        print(f"  Budget entries: 216 (3 sites x 12 months x 6 lines)")


if __name__ == "__main__":
    asyncio.run(seed())
