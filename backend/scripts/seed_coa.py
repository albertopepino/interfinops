"""
Seed script: creates Chart of Accounts demo data.

Usage:
    cd backend && source .venv/bin/activate
    PYTHONPATH=. python scripts/seed_coa.py
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.chart_of_accounts import AccountMapping, AccountType, GroupAccount, SiteAccount
from app.models.site import Site

# Fixed UUIDs from seed.py
SITE_US_ID = uuid.UUID("00000000-0000-4000-8000-000000000010")
SITE_UK_ID = uuid.UUID("00000000-0000-4000-8000-000000000011")
SITE_DE_ID = uuid.UUID("00000000-0000-4000-8000-000000000012")
ADMIN_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")

# ---------------------------------------------------------------------------
# Group (Master) Chart of Accounts
# ---------------------------------------------------------------------------
GROUP_ACCOUNTS: list[dict] = [
    # Assets
    {"code": "1000", "name": "Cash & Bank Balances", "type": "asset", "parent": None, "order": 10},
    {"code": "1100", "name": "Accounts Receivable", "type": "asset", "parent": None, "order": 20},
    {"code": "1200", "name": "Inventory", "type": "asset", "parent": None, "order": 30},
    {"code": "1300", "name": "Prepaid Expenses", "type": "asset", "parent": None, "order": 40},
    {"code": "1400", "name": "Intercompany Receivables", "type": "asset", "parent": None, "order": 50},
    {"code": "1500", "name": "Property, Plant & Equipment", "type": "asset", "parent": None, "order": 60},
    {"code": "1600", "name": "Intangible Assets", "type": "asset", "parent": None, "order": 70},
    {"code": "1700", "name": "Other Non-Current Assets", "type": "asset", "parent": None, "order": 80},
    # Liabilities
    {"code": "2000", "name": "Accounts Payable", "type": "liability", "parent": None, "order": 100},
    {"code": "2100", "name": "Short-term Debt", "type": "liability", "parent": None, "order": 110},
    {"code": "2200", "name": "Accrued Expenses", "type": "liability", "parent": None, "order": 120},
    {"code": "2300", "name": "Intercompany Payables", "type": "liability", "parent": None, "order": 130},
    {"code": "2400", "name": "Taxes Payable", "type": "liability", "parent": None, "order": 140},
    {"code": "2500", "name": "Long-term Debt", "type": "liability", "parent": None, "order": 150},
    {"code": "2600", "name": "Provisions", "type": "liability", "parent": None, "order": 160},
    # Equity
    {"code": "3000", "name": "Share Capital", "type": "equity", "parent": None, "order": 200},
    {"code": "3100", "name": "Retained Earnings", "type": "equity", "parent": None, "order": 210},
    {"code": "3200", "name": "Other Reserves", "type": "equity", "parent": None, "order": 220},
    # Revenue
    {"code": "4000", "name": "Revenue", "type": "revenue", "parent": None, "order": 300},
    {"code": "4100", "name": "Other Income", "type": "revenue", "parent": None, "order": 310},
    {"code": "4200", "name": "Intercompany Revenue", "type": "revenue", "parent": None, "order": 320},
    # Expenses
    {"code": "5000", "name": "Cost of Goods Sold", "type": "expense", "parent": None, "order": 400},
    {"code": "5100", "name": "Salaries & Wages", "type": "expense", "parent": None, "order": 410},
    {"code": "5200", "name": "Depreciation & Amortization", "type": "expense", "parent": None, "order": 420},
    {"code": "5300", "name": "Operating Expenses", "type": "expense", "parent": None, "order": 430},
    {"code": "5400", "name": "Interest Expense", "type": "expense", "parent": None, "order": 440},
    {"code": "5500", "name": "Income Tax Expense", "type": "expense", "parent": None, "order": 450},
]


# ---------------------------------------------------------------------------
# Site-specific accounts (localized names/codes)
# ---------------------------------------------------------------------------

def us_accounts() -> list[dict]:
    """US site accounts - English names, standard US GAAP style."""
    return [
        {"code": "1000", "name": "Cash and Cash Equivalents", "type": "asset", "parent": None, "order": 10, "group_code": "1000"},
        {"code": "1100", "name": "Trade Receivables", "type": "asset", "parent": None, "order": 20, "group_code": "1100"},
        {"code": "1200", "name": "Inventories", "type": "asset", "parent": None, "order": 30, "group_code": "1200"},
        {"code": "1300", "name": "Prepaid Expenses & Other", "type": "asset", "parent": None, "order": 40, "group_code": "1300"},
        {"code": "1400", "name": "Intercompany Receivables", "type": "asset", "parent": None, "order": 50, "group_code": "1400"},
        {"code": "1500", "name": "Fixed Assets (Net)", "type": "asset", "parent": None, "order": 60, "group_code": "1500"},
        {"code": "1600", "name": "Goodwill & Intangibles", "type": "asset", "parent": None, "order": 70, "group_code": "1600"},
        {"code": "1700", "name": "Other Long-term Assets", "type": "asset", "parent": None, "order": 80, "group_code": "1700"},
        {"code": "2000", "name": "Accounts Payable", "type": "liability", "parent": None, "order": 100, "group_code": "2000"},
        {"code": "2100", "name": "Current Portion of Debt", "type": "liability", "parent": None, "order": 110, "group_code": "2100"},
        {"code": "2200", "name": "Accrued Liabilities", "type": "liability", "parent": None, "order": 120, "group_code": "2200"},
        {"code": "2300", "name": "Intercompany Payables", "type": "liability", "parent": None, "order": 130, "group_code": "2300"},
        {"code": "2400", "name": "Income Taxes Payable", "type": "liability", "parent": None, "order": 140, "group_code": "2400"},
        {"code": "2500", "name": "Long-term Debt", "type": "liability", "parent": None, "order": 150, "group_code": "2500"},
        {"code": "2600", "name": "Provisions & Contingencies", "type": "liability", "parent": None, "order": 160, "group_code": "2600"},
        {"code": "3000", "name": "Common Stock", "type": "equity", "parent": None, "order": 200, "group_code": "3000"},
        {"code": "3100", "name": "Retained Earnings", "type": "equity", "parent": None, "order": 210, "group_code": "3100"},
        {"code": "3200", "name": "AOCI", "type": "equity", "parent": None, "order": 220, "group_code": "3200"},
        {"code": "4000", "name": "Net Revenue", "type": "revenue", "parent": None, "order": 300, "group_code": "4000"},
        {"code": "4100", "name": "Other Income", "type": "revenue", "parent": None, "order": 310, "group_code": "4100"},
        {"code": "4200", "name": "Intercompany Revenue", "type": "revenue", "parent": None, "order": 320, "group_code": "4200"},
        {"code": "5000", "name": "Cost of Sales", "type": "expense", "parent": None, "order": 400, "group_code": "5000"},
        {"code": "5100", "name": "Compensation & Benefits", "type": "expense", "parent": None, "order": 410, "group_code": "5100"},
        {"code": "5200", "name": "Depreciation & Amortization", "type": "expense", "parent": None, "order": 420, "group_code": "5200"},
        {"code": "5300", "name": "SG&A Expenses", "type": "expense", "parent": None, "order": 430, "group_code": "5300"},
        {"code": "5400", "name": "Interest Expense", "type": "expense", "parent": None, "order": 440, "group_code": "5400"},
        {"code": "5500", "name": "Provision for Income Taxes", "type": "expense", "parent": None, "order": 450, "group_code": "5500"},
    ]


def uk_accounts() -> list[dict]:
    """UK site accounts - British naming conventions."""
    return [
        {"code": "1000", "name": "Cash at Bank", "type": "asset", "parent": None, "order": 10, "group_code": "1000"},
        {"code": "1100", "name": "Trade Debtors", "type": "asset", "parent": None, "order": 20, "group_code": "1100"},
        {"code": "1200", "name": "Stock", "type": "asset", "parent": None, "order": 30, "group_code": "1200"},
        {"code": "1300", "name": "Prepayments", "type": "asset", "parent": None, "order": 40, "group_code": "1300"},
        {"code": "1400", "name": "Amounts Due from Group Companies", "type": "asset", "parent": None, "order": 50, "group_code": "1400"},
        {"code": "1500", "name": "Tangible Fixed Assets", "type": "asset", "parent": None, "order": 60, "group_code": "1500"},
        {"code": "1600", "name": "Intangible Fixed Assets", "type": "asset", "parent": None, "order": 70, "group_code": "1600"},
        {"code": "1700", "name": "Other Fixed Assets", "type": "asset", "parent": None, "order": 80, "group_code": "1700"},
        {"code": "2000", "name": "Trade Creditors", "type": "liability", "parent": None, "order": 100, "group_code": "2000"},
        {"code": "2100", "name": "Bank Overdraft & Short-term Loans", "type": "liability", "parent": None, "order": 110, "group_code": "2100"},
        {"code": "2200", "name": "Accruals", "type": "liability", "parent": None, "order": 120, "group_code": "2200"},
        {"code": "2300", "name": "Amounts Due to Group Companies", "type": "liability", "parent": None, "order": 130, "group_code": "2300"},
        {"code": "2400", "name": "Corporation Tax", "type": "liability", "parent": None, "order": 140, "group_code": "2400"},
        {"code": "2500", "name": "Long-term Borrowings", "type": "liability", "parent": None, "order": 150, "group_code": "2500"},
        {"code": "2600", "name": "Provisions for Liabilities", "type": "liability", "parent": None, "order": 160, "group_code": "2600"},
        {"code": "3000", "name": "Called Up Share Capital", "type": "equity", "parent": None, "order": 200, "group_code": "3000"},
        {"code": "3100", "name": "Profit & Loss Account", "type": "equity", "parent": None, "order": 210, "group_code": "3100"},
        {"code": "3200", "name": "Other Reserves", "type": "equity", "parent": None, "order": 220, "group_code": "3200"},
        {"code": "4000", "name": "Turnover", "type": "revenue", "parent": None, "order": 300, "group_code": "4000"},
        {"code": "4100", "name": "Other Operating Income", "type": "revenue", "parent": None, "order": 310, "group_code": "4100"},
        {"code": "4200", "name": "Intercompany Turnover", "type": "revenue", "parent": None, "order": 320, "group_code": "4200"},
        {"code": "5000", "name": "Cost of Sales", "type": "expense", "parent": None, "order": 400, "group_code": "5000"},
        {"code": "5100", "name": "Staff Costs", "type": "expense", "parent": None, "order": 410, "group_code": "5100"},
        {"code": "5200", "name": "Depreciation", "type": "expense", "parent": None, "order": 420, "group_code": "5200"},
        {"code": "5300", "name": "Administrative Expenses", "type": "expense", "parent": None, "order": 430, "group_code": "5300"},
        {"code": "5400", "name": "Interest Payable", "type": "expense", "parent": None, "order": 440, "group_code": "5400"},
        {"code": "5500", "name": "Tax on Profit", "type": "expense", "parent": None, "order": 450, "group_code": "5500"},
    ]


def de_accounts() -> list[dict]:
    """DE site accounts - German naming conventions (SKR04 style)."""
    return [
        {"code": "1000", "name": "Kassenbestand & Bankguthaben", "type": "asset", "parent": None, "order": 10, "group_code": "1000"},
        {"code": "1100", "name": "Forderungen aus Lieferungen", "type": "asset", "parent": None, "order": 20, "group_code": "1100"},
        {"code": "1200", "name": "Vorraete", "type": "asset", "parent": None, "order": 30, "group_code": "1200"},
        {"code": "1300", "name": "Rechnungsabgrenzungsposten", "type": "asset", "parent": None, "order": 40, "group_code": "1300"},
        {"code": "1400", "name": "Forderungen gegen verbundene Unternehmen", "type": "asset", "parent": None, "order": 50, "group_code": "1400"},
        {"code": "1500", "name": "Sachanlagen", "type": "asset", "parent": None, "order": 60, "group_code": "1500"},
        {"code": "1600", "name": "Immaterielle Vermoegensgegenstaende", "type": "asset", "parent": None, "order": 70, "group_code": "1600"},
        {"code": "1700", "name": "Sonstige Vermoegenswerte", "type": "asset", "parent": None, "order": 80, "group_code": "1700"},
        {"code": "2000", "name": "Verbindlichkeiten aus Lieferungen", "type": "liability", "parent": None, "order": 100, "group_code": "2000"},
        {"code": "2100", "name": "Kurzfristige Bankverbindlichkeiten", "type": "liability", "parent": None, "order": 110, "group_code": "2100"},
        {"code": "2200", "name": "Sonstige Rueckstellungen", "type": "liability", "parent": None, "order": 120, "group_code": "2200"},
        {"code": "2300", "name": "Verbindlichkeiten gegen verbundene Unternehmen", "type": "liability", "parent": None, "order": 130, "group_code": "2300"},
        {"code": "2400", "name": "Steuerrueckstellungen", "type": "liability", "parent": None, "order": 140, "group_code": "2400"},
        {"code": "2500", "name": "Langfristige Verbindlichkeiten", "type": "liability", "parent": None, "order": 150, "group_code": "2500"},
        {"code": "2600", "name": "Rueckstellungen", "type": "liability", "parent": None, "order": 160, "group_code": "2600"},
        {"code": "3000", "name": "Gezeichnetes Kapital", "type": "equity", "parent": None, "order": 200, "group_code": "3000"},
        {"code": "3100", "name": "Gewinnvortrag", "type": "equity", "parent": None, "order": 210, "group_code": "3100"},
        {"code": "3200", "name": "Sonstige Ruecklagen", "type": "equity", "parent": None, "order": 220, "group_code": "3200"},
        {"code": "4000", "name": "Umsatzerloese", "type": "revenue", "parent": None, "order": 300, "group_code": "4000"},
        {"code": "4100", "name": "Sonstige betriebliche Ertraege", "type": "revenue", "parent": None, "order": 310, "group_code": "4100"},
        {"code": "4200", "name": "Innenumsaetze", "type": "revenue", "parent": None, "order": 320, "group_code": "4200"},
        {"code": "5000", "name": "Herstellungskosten", "type": "expense", "parent": None, "order": 400, "group_code": "5000"},
        {"code": "5100", "name": "Personalaufwand", "type": "expense", "parent": None, "order": 410, "group_code": "5100"},
        {"code": "5200", "name": "Abschreibungen", "type": "expense", "parent": None, "order": 420, "group_code": "5200"},
        {"code": "5300", "name": "Sonstige betriebliche Aufwendungen", "type": "expense", "parent": None, "order": 430, "group_code": "5300"},
        {"code": "5400", "name": "Zinsaufwand", "type": "expense", "parent": None, "order": 440, "group_code": "5400"},
        {"code": "5500", "name": "Steueraufwand", "type": "expense", "parent": None, "order": 450, "group_code": "5500"},
    ]


async def seed_coa() -> None:
    async with async_session_factory() as session:
        # Clean existing CoA data
        for tbl in ["account_mappings", "site_accounts", "group_accounts"]:
            await session.execute(text(f"TRUNCATE TABLE {tbl} CASCADE"))
        await session.commit()

    async with async_session_factory() as session:
        # ----- Group Accounts -----
        group_account_map: dict[str, GroupAccount] = {}
        for ga in GROUP_ACCOUNTS:
            acct = GroupAccount(
                code=ga["code"],
                name=ga["name"],
                account_type=AccountType(ga["type"]),
                parent_code=ga["parent"],
                display_order=ga["order"],
            )
            session.add(acct)
            group_account_map[ga["code"]] = acct
        await session.flush()

        print(f"  Group accounts: {len(GROUP_ACCOUNTS)}")

        # ----- Site Accounts + Mappings -----
        site_configs = [
            ("US", SITE_US_ID, us_accounts()),
            ("UK", SITE_UK_ID, uk_accounts()),
            ("DE", SITE_DE_ID, de_accounts()),
        ]

        total_site_accounts = 0
        total_mappings = 0

        for site_key, site_id, accounts in site_configs:
            for sa_def in accounts:
                site_acct = SiteAccount(
                    site_id=site_id,
                    code=sa_def["code"],
                    name=sa_def["name"],
                    account_type=AccountType(sa_def["type"]),
                    parent_code=sa_def["parent"],
                    display_order=sa_def["order"],
                )
                session.add(site_acct)
                await session.flush()

                # Create mapping
                group_code = sa_def["group_code"]
                if group_code in group_account_map:
                    mapping = AccountMapping(
                        site_account_id=site_acct.id,
                        group_account_id=group_account_map[group_code].id,
                        created_by=ADMIN_ID,
                    )
                    session.add(mapping)
                    total_mappings += 1

                total_site_accounts += 1

            print(f"  {site_key} site accounts: {len(accounts)}")

        await session.commit()
        print(f"\nSeed complete!")
        print(f"  Group accounts: {len(GROUP_ACCOUNTS)}")
        print(f"  Site accounts: {total_site_accounts}")
        print(f"  Mappings: {total_mappings}")


if __name__ == "__main__":
    asyncio.run(seed_coa())
