"""
Comprehensive seed script: populates ALL modules with realistic data.

Usage:
    cd backend && source .venv/bin/activate
    PYTHONPATH=. python scripts/seed_all.py
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, engine
from app.models import (
    AccountMapping,
    AccountType,
    Asset,
    AssetCategory,
    AssetStatus,
    BankAccount,
    BankAccountType,
    BudgetEntry,
    CashPosition,
    DebtInstrument,
    DebtStatus,
    Department,
    DepreciationMethod,
    Director,
    Employee,
    EmploymentType,
    EntityType,
    AuditOpinion,
    AuditStatus,
    FilingStatus,
    FilingType,
    FinancialLineItem,
    FinancialStatement,
    FxRate,
    GroupAccount,
    ICInvoice,
    ICInvoiceCategory,
    ICInvoiceStatus,
    ICLoan,
    ICLoanStatus,
    InstrumentType,
    KPITarget,
    LegalEntity,
    Position,
    SalaryRecord,
    Site,
    SiteAccount,
    StatementStatus,
    StatementType,
    StatutoryAudit,
    TaxFiling,
    TaxJurisdiction,
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

PASSWORD = "password123"

SITE_MAP = [
    ("US", SITE_US_ID, "USD", LOCAL_CFO_US_ID),
    ("UK", SITE_UK_ID, "GBP", LOCAL_CFO_UK_ID),
    ("DE", SITE_DE_ID, "EUR", LOCAL_CFO_DE_ID),
]


# ---------------------------------------------------------------------------
# Tables to truncate (order does not matter with CASCADE)
# ---------------------------------------------------------------------------
ALL_TABLES = [
    "account_mappings", "site_accounts", "group_accounts",
    "salary_records", "employees", "positions", "departments",
    "financial_line_items", "financial_statements",
    "budget_entries", "kpi_targets",
    "ic_invoices", "ic_loans",
    "assets",
    "tax_filings", "tax_jurisdictions",
    "cash_positions", "bank_accounts", "debt_instruments",
    "directors", "statutory_audits", "legal_entities",
    "fx_rates",
    "dashboard_configs", "audit_logs",
    "user_site", "users", "sites",
]


# ---------------------------------------------------------------------------
# Financial statement line item builders (from existing seed.py)
# ---------------------------------------------------------------------------
def income_statement_lines(site_key: str, month: int) -> list[dict]:
    mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]
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
    mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]

    def amt(base: float) -> Decimal:
        return (Decimal(str(base)) * mult).quantize(Decimal("0.01"))

    return [
        {"code": "CA", "name": "Current Assets", "parent": None, "amount": amt(8_500_000)},
        {"code": "CA_CASH", "name": "Cash & Bank Balances", "parent": "CA", "amount": amt(2_100_000)},
        {"code": "CA_AR", "name": "Accounts Receivable (Trade)", "parent": "CA", "amount": amt(3_200_000)},
        {"code": "CA_IC_AR", "name": "Intercompany Receivables", "parent": "CA", "amount": amt(800_000)},
        {"code": "CA_INV", "name": "Inventory", "parent": "CA", "amount": amt(1_900_000)},
        {"code": "CA_PREPAID", "name": "Prepaid Expenses", "parent": "CA", "amount": amt(350_000)},
        {"code": "CA_OTHER", "name": "Other Current Assets", "parent": "CA", "amount": amt(150_000)},
        {"code": "NCA", "name": "Non-Current Assets", "parent": None, "amount": amt(12_000_000)},
        {"code": "NCA_PPE", "name": "Property, Plant & Equipment", "parent": "NCA", "amount": amt(9_500_000)},
        {"code": "NCA_INTANG", "name": "Intangible Assets", "parent": "NCA", "amount": amt(1_500_000)},
        {"code": "NCA_INVEST", "name": "Long-term Investments", "parent": "NCA", "amount": amt(700_000)},
        {"code": "NCA_DEP", "name": "Deposits & Advances", "parent": "NCA", "amount": amt(200_000)},
        {"code": "NCA_OTHER", "name": "Other Non-Current Assets", "parent": "NCA", "amount": amt(100_000)},
        {"code": "TA", "name": "Total Assets", "parent": None, "amount": amt(20_500_000)},
        {"code": "CL", "name": "Current Liabilities", "parent": None, "amount": amt(5_200_000)},
        {"code": "CL_AP", "name": "Accounts Payable (Trade)", "parent": "CL", "amount": amt(2_100_000)},
        {"code": "CL_IC_AP", "name": "Intercompany Payables", "parent": "CL", "amount": amt(600_000)},
        {"code": "CL_STD", "name": "Short-term Debt", "parent": "CL", "amount": amt(1_200_000)},
        {"code": "CL_ACCR", "name": "Accrued Expenses", "parent": "CL", "amount": amt(500_000)},
        {"code": "CL_WAGES", "name": "Wages Payable", "parent": "CL", "amount": amt(400_000)},
        {"code": "CL_TAX", "name": "Taxes Payable", "parent": "CL", "amount": amt(300_000)},
        {"code": "CL_OTHER", "name": "Other Current Liabilities", "parent": "CL", "amount": amt(100_000)},
        {"code": "NCL", "name": "Non-Current Liabilities", "parent": None, "amount": amt(5_800_000)},
        {"code": "NCL_LTD", "name": "Long-term Debt", "parent": "NCL", "amount": amt(4_500_000)},
        {"code": "NCL_PROV", "name": "Provisions & Accruals", "parent": "NCL", "amount": amt(900_000)},
        {"code": "NCL_OTHER", "name": "Other Non-Current Liabilities", "parent": "NCL", "amount": amt(400_000)},
        {"code": "TL", "name": "Total Liabilities", "parent": None, "amount": amt(11_000_000)},
        {"code": "EQ", "name": "Total Equity", "parent": None, "amount": amt(9_500_000)},
        {"code": "EQ_SC", "name": "Share Capital", "parent": "EQ", "amount": amt(3_000_000)},
        {"code": "EQ_RE", "name": "Retained Earnings", "parent": "EQ", "amount": amt(5_800_000)},
        {"code": "EQ_RES", "name": "Other Reserves", "parent": "EQ", "amount": amt(500_000)},
        {"code": "EQ_FX", "name": "FX Translation Reserve", "parent": "EQ", "amount": amt(200_000)},
        {"code": "TLE", "name": "Total Liabilities + Equity", "parent": None, "amount": amt(20_500_000)},
    ]


def cash_flow_lines(site_key: str, month: int) -> list[dict]:
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
    {"from": "USD", "to": "EUR", "months": {
        1: (0.92, 0.915), 2: (0.91, 0.912), 3: (0.93, 0.920),
        4: (0.92, 0.918), 5: (0.91, 0.915), 6: (0.90, 0.908),
        7: (0.89, 0.895), 8: (0.90, 0.898), 9: (0.91, 0.905),
        10: (0.92, 0.915), 11: (0.93, 0.925), 12: (0.94, 0.935),
    }},
    {"from": "GBP", "to": "EUR", "months": {
        1: (1.16, 1.155), 2: (1.17, 1.165), 3: (1.16, 1.160),
        4: (1.15, 1.155), 5: (1.16, 1.158), 6: (1.17, 1.165),
        7: (1.18, 1.175), 8: (1.17, 1.170), 9: (1.16, 1.165),
        10: (1.15, 1.155), 11: (1.16, 1.158), 12: (1.17, 1.165),
    }},
    {"from": "EUR", "to": "EUR", "months": {m: (1.0, 1.0) for m in range(1, 13)}},
]


# ---------------------------------------------------------------------------
# Group Chart of Accounts
# ---------------------------------------------------------------------------
GROUP_ACCOUNTS_DATA = [
    # Revenue
    ("1000", "Revenue", AccountType.revenue, None, 100),
    ("1010", "Sales of Goods", AccountType.revenue, "1000", 110),
    ("1020", "Sales of Services", AccountType.revenue, "1000", 120),
    ("1030", "Other Revenue", AccountType.revenue, "1000", 130),
    # COGS
    ("2000", "Cost of Goods Sold", AccountType.expense, None, 200),
    ("2010", "Raw Materials", AccountType.expense, "2000", 210),
    ("2020", "Direct Labor", AccountType.expense, "2000", 220),
    ("2030", "Manufacturing Overhead", AccountType.expense, "2000", 230),
    # Operating Expenses
    ("3000", "Operating Expenses", AccountType.expense, None, 300),
    ("3010", "Salaries & Wages", AccountType.expense, "3000", 310),
    ("3020", "Rent & Utilities", AccountType.expense, "3000", 320),
    ("3030", "Depreciation & Amortization", AccountType.expense, "3000", 330),
    ("3040", "Marketing & Advertising", AccountType.expense, "3000", 340),
    ("3050", "Professional Fees", AccountType.expense, "3000", 350),
    ("3060", "Insurance", AccountType.expense, "3000", 360),
    ("3070", "Other Operating Expenses", AccountType.expense, "3000", 370),
    # Assets
    ("4000", "Current Assets", AccountType.asset, None, 400),
    ("4010", "Cash & Bank Balances", AccountType.asset, "4000", 410),
    ("4020", "Accounts Receivable", AccountType.asset, "4000", 420),
    ("4030", "Inventory", AccountType.asset, "4000", 430),
    ("5000", "Non-Current Assets", AccountType.asset, None, 500),
    ("5010", "Property, Plant & Equipment", AccountType.asset, "5000", 510),
    ("5020", "Intangible Assets", AccountType.asset, "5000", 520),
    # Liabilities
    ("6000", "Current Liabilities", AccountType.liability, None, 600),
    ("6010", "Accounts Payable", AccountType.liability, "6000", 610),
    ("6020", "Short-term Debt", AccountType.liability, "6000", 620),
    ("7000", "Non-Current Liabilities", AccountType.liability, None, 700),
    ("7010", "Long-term Debt", AccountType.liability, "7000", 710),
    # Equity
    ("8000", "Total Equity", AccountType.equity, None, 800),
    ("8010", "Share Capital", AccountType.equity, "8000", 810),
    ("8020", "Retained Earnings", AccountType.equity, "8000", 820),
]

# Site-level accounts: (site_key, local_code, local_name, account_type, parent, display_order, group_code_mapping)
SITE_ACCOUNTS_DATA = {
    "US": [
        ("100", "Revenue", AccountType.revenue, None, 100, "1000"),
        ("110", "Product Sales", AccountType.revenue, "100", 110, "1010"),
        ("120", "Service Revenue", AccountType.revenue, "100", 120, "1020"),
        ("200", "Cost of Sales", AccountType.expense, None, 200, "2000"),
        ("210", "Materials Cost", AccountType.expense, "200", 210, "2010"),
        ("300", "Operating Costs", AccountType.expense, None, 300, "3000"),
        ("310", "Payroll", AccountType.expense, "300", 310, "3010"),
        ("320", "Occupancy", AccountType.expense, "300", 320, "3020"),
        ("400", "Current Assets", AccountType.asset, None, 400, "4000"),
        ("410", "Cash", AccountType.asset, "400", 410, "4010"),
        ("420", "Trade Receivables", AccountType.asset, "400", 420, "4020"),
        ("500", "Fixed Assets", AccountType.asset, None, 500, "5000"),
        ("600", "Current Liabilities", AccountType.liability, None, 600, "6000"),
        ("610", "Trade Payables", AccountType.liability, "600", 610, "6010"),
        ("700", "Long-term Liabilities", AccountType.liability, None, 700, "7000"),
        ("800", "Shareholders Equity", AccountType.equity, None, 800, "8000"),
    ],
    "UK": [
        ("100", "Turnover", AccountType.revenue, None, 100, "1000"),
        ("110", "Goods Sales", AccountType.revenue, "100", 110, "1010"),
        ("120", "Services Income", AccountType.revenue, "100", 120, "1020"),
        ("200", "Cost of Sales", AccountType.expense, None, 200, "2000"),
        ("210", "Materials", AccountType.expense, "200", 210, "2010"),
        ("300", "Overheads", AccountType.expense, None, 300, "3000"),
        ("310", "Staff Costs", AccountType.expense, "300", 310, "3010"),
        ("320", "Premises Costs", AccountType.expense, "300", 320, "3020"),
        ("400", "Current Assets", AccountType.asset, None, 400, "4000"),
        ("410", "Bank & Cash", AccountType.asset, "400", 410, "4010"),
        ("420", "Debtors", AccountType.asset, "400", 420, "4020"),
        ("500", "Fixed Assets", AccountType.asset, None, 500, "5000"),
        ("600", "Creditors < 1yr", AccountType.liability, None, 600, "6000"),
        ("610", "Trade Creditors", AccountType.liability, "600", 610, "6010"),
        ("700", "Creditors > 1yr", AccountType.liability, None, 700, "7000"),
        ("800", "Capital & Reserves", AccountType.equity, None, 800, "8000"),
    ],
    "DE": [
        ("100", "Umsatzerloese", AccountType.revenue, None, 100, "1000"),
        ("110", "Warenverkauf", AccountType.revenue, "100", 110, "1010"),
        ("120", "Dienstleistungen", AccountType.revenue, "100", 120, "1020"),
        ("200", "Herstellungskosten", AccountType.expense, None, 200, "2000"),
        ("210", "Materialaufwand", AccountType.expense, "200", 210, "2010"),
        ("300", "Betriebsaufwand", AccountType.expense, None, 300, "3000"),
        ("310", "Personalaufwand", AccountType.expense, "300", 310, "3010"),
        ("320", "Mietaufwand", AccountType.expense, "300", 320, "3020"),
        ("400", "Umlaufvermoegen", AccountType.asset, None, 400, "4000"),
        ("410", "Kasse & Bank", AccountType.asset, "400", 410, "4010"),
        ("420", "Forderungen", AccountType.asset, "400", 420, "4020"),
        ("500", "Anlagevermoegen", AccountType.asset, None, 500, "5000"),
        ("600", "Kurzfristige Verbindlichkeiten", AccountType.liability, None, 600, "6000"),
        ("610", "Verbindlichkeiten aus LuL", AccountType.liability, "600", 610, "6010"),
        ("700", "Langfristige Verbindlichkeiten", AccountType.liability, None, 700, "7000"),
        ("800", "Eigenkapital", AccountType.equity, None, 800, "8000"),
    ],
}


# ---------------------------------------------------------------------------
# HR data definitions
# ---------------------------------------------------------------------------
DEPARTMENTS_DATA = {
    "US": [
        ("FIN", "Finance"), ("ENG", "Engineering"), ("SAL", "Sales"), ("HR", "Human Resources"),
    ],
    "UK": [
        ("FIN", "Finance"), ("OPS", "Operations"), ("SAL", "Sales"), ("HR", "Human Resources"),
    ],
    "DE": [
        ("FIN", "Finanzen"), ("ENG", "Engineering"), ("SAL", "Vertrieb"), ("HR", "Personal"),
    ],
}

POSITIONS_DATA = {
    "US": [
        ("FIN", "Financial Controller", "senior"),
        ("FIN", "Senior Accountant", "mid"),
        ("FIN", "Accounts Payable Clerk", "junior"),
        ("ENG", "VP Engineering", "executive"),
        ("ENG", "Senior Software Engineer", "senior"),
        ("ENG", "Software Engineer", "mid"),
        ("ENG", "Junior Developer", "junior"),
        ("SAL", "Sales Director", "senior"),
        ("SAL", "Account Executive", "mid"),
        ("SAL", "Sales Development Rep", "junior"),
        ("HR", "HR Manager", "senior"),
        ("HR", "HR Coordinator", "mid"),
    ],
    "UK": [
        ("FIN", "Finance Manager", "senior"),
        ("FIN", "Management Accountant", "mid"),
        ("FIN", "Bookkeeper", "junior"),
        ("OPS", "Operations Director", "executive"),
        ("OPS", "Operations Manager", "senior"),
        ("OPS", "Process Analyst", "mid"),
        ("OPS", "Operations Coordinator", "junior"),
        ("SAL", "Head of Sales", "senior"),
        ("SAL", "Business Development Manager", "mid"),
        ("SAL", "Sales Associate", "junior"),
        ("HR", "People & Culture Lead", "senior"),
        ("HR", "HR Administrator", "junior"),
    ],
    "DE": [
        ("FIN", "Leiter Finanzen", "senior"),
        ("FIN", "Bilanzbuchhalter", "mid"),
        ("FIN", "Buchhalter", "junior"),
        ("ENG", "Leiter Entwicklung", "executive"),
        ("ENG", "Senior Entwickler", "senior"),
        ("ENG", "Entwickler", "mid"),
        ("ENG", "Junior Entwickler", "junior"),
        ("SAL", "Vertriebsleiter", "senior"),
        ("SAL", "Account Manager", "mid"),
        ("SAL", "Vertriebsmitarbeiter", "junior"),
        ("HR", "Personalleiter", "senior"),
        ("HR", "Personalsachbearbeiter", "junior"),
    ],
}

EMPLOYEES_DATA = {
    "US": [
        ("US001", "James", "Wilson", "FIN", "Financial Controller", EmploymentType.full_time, "1.00", "2019-03-15"),
        ("US002", "Emily", "Chen", "FIN", "Senior Accountant", EmploymentType.full_time, "1.00", "2020-06-01"),
        ("US003", "Michael", "Brown", "FIN", "Accounts Payable Clerk", EmploymentType.full_time, "1.00", "2022-01-10"),
        ("US004", "David", "Martinez", "ENG", "VP Engineering", EmploymentType.full_time, "1.00", "2018-09-01"),
        ("US005", "Sarah", "Johnson", "ENG", "Senior Software Engineer", EmploymentType.full_time, "1.00", "2019-11-15"),
        ("US006", "Kevin", "Lee", "ENG", "Software Engineer", EmploymentType.full_time, "1.00", "2021-03-01"),
        ("US007", "Amanda", "Taylor", "ENG", "Software Engineer", EmploymentType.full_time, "1.00", "2021-07-15"),
        ("US008", "Ryan", "Garcia", "ENG", "Junior Developer", EmploymentType.full_time, "1.00", "2023-06-01"),
        ("US009", "Jennifer", "Davis", "SAL", "Sales Director", EmploymentType.full_time, "1.00", "2019-01-15"),
        ("US010", "Christopher", "Anderson", "SAL", "Account Executive", EmploymentType.full_time, "1.00", "2020-09-01"),
        ("US011", "Laura", "Thomas", "SAL", "Account Executive", EmploymentType.full_time, "1.00", "2021-04-15"),
        ("US012", "Brian", "White", "SAL", "Sales Development Rep", EmploymentType.full_time, "1.00", "2023-01-15"),
        ("US013", "Megan", "Harris", "HR", "HR Manager", EmploymentType.full_time, "1.00", "2020-02-01"),
        ("US014", "Daniel", "Clark", "HR", "HR Coordinator", EmploymentType.full_time, "1.00", "2022-08-01"),
        ("US015", "Rachel", "Lewis", "ENG", "Junior Developer", EmploymentType.part_time, "0.60", "2024-01-15"),
        ("US016", "Tom", "Walker", "SAL", "Sales Development Rep", EmploymentType.contractor, "1.00", "2024-06-01"),
        ("US017", "Jessica", "Hall", "FIN", "Senior Accountant", EmploymentType.full_time, "1.00", "2023-03-01"),
    ],
    "UK": [
        ("UK001", "Sarah", "Thompson", "FIN", "Finance Manager", EmploymentType.full_time, "1.00", "2019-04-01"),
        ("UK002", "Oliver", "Wright", "FIN", "Management Accountant", EmploymentType.full_time, "1.00", "2020-08-15"),
        ("UK003", "Charlotte", "Green", "FIN", "Bookkeeper", EmploymentType.full_time, "1.00", "2022-02-01"),
        ("UK004", "William", "Edwards", "OPS", "Operations Director", EmploymentType.full_time, "1.00", "2018-06-01"),
        ("UK005", "Emma", "Baker", "OPS", "Operations Manager", EmploymentType.full_time, "1.00", "2020-01-15"),
        ("UK006", "George", "Turner", "OPS", "Process Analyst", EmploymentType.full_time, "1.00", "2021-05-01"),
        ("UK007", "Sophie", "Collins", "OPS", "Operations Coordinator", EmploymentType.full_time, "1.00", "2022-09-15"),
        ("UK008", "James", "Morgan", "SAL", "Head of Sales", EmploymentType.full_time, "1.00", "2019-07-01"),
        ("UK009", "Hannah", "Phillips", "SAL", "Business Development Manager", EmploymentType.full_time, "1.00", "2021-02-01"),
        ("UK010", "Thomas", "Cooper", "SAL", "Business Development Manager", EmploymentType.full_time, "1.00", "2021-10-15"),
        ("UK011", "Lucy", "Howard", "SAL", "Sales Associate", EmploymentType.full_time, "1.00", "2023-03-01"),
        ("UK012", "Harry", "Bennett", "HR", "People & Culture Lead", EmploymentType.full_time, "1.00", "2020-05-15"),
        ("UK013", "Alice", "Ward", "HR", "HR Administrator", EmploymentType.full_time, "1.00", "2022-11-01"),
        ("UK014", "Freddie", "Cox", "OPS", "Process Analyst", EmploymentType.part_time, "0.80", "2023-07-01"),
        ("UK015", "Isabelle", "Hughes", "SAL", "Sales Associate", EmploymentType.contractor, "1.00", "2024-02-15"),
    ],
    "DE": [
        ("DE001", "Klaus", "Mueller", "FIN", "Leiter Finanzen", EmploymentType.full_time, "1.00", "2019-01-15"),
        ("DE002", "Anna", "Schmidt", "FIN", "Bilanzbuchhalter", EmploymentType.full_time, "1.00", "2020-04-01"),
        ("DE003", "Markus", "Weber", "FIN", "Buchhalter", EmploymentType.full_time, "1.00", "2022-03-15"),
        ("DE004", "Stefan", "Fischer", "ENG", "Leiter Entwicklung", EmploymentType.full_time, "1.00", "2018-10-01"),
        ("DE005", "Julia", "Wagner", "ENG", "Senior Entwickler", EmploymentType.full_time, "1.00", "2019-12-01"),
        ("DE006", "Thomas", "Becker", "ENG", "Entwickler", EmploymentType.full_time, "1.00", "2021-06-15"),
        ("DE007", "Katrin", "Hoffmann", "ENG", "Entwickler", EmploymentType.full_time, "1.00", "2022-01-15"),
        ("DE008", "Lukas", "Schulz", "ENG", "Junior Entwickler", EmploymentType.full_time, "1.00", "2023-09-01"),
        ("DE009", "Sabine", "Koch", "SAL", "Vertriebsleiter", EmploymentType.full_time, "1.00", "2019-05-01"),
        ("DE010", "Andreas", "Braun", "SAL", "Account Manager", EmploymentType.full_time, "1.00", "2020-11-15"),
        ("DE011", "Laura", "Richter", "SAL", "Account Manager", EmploymentType.full_time, "1.00", "2021-08-01"),
        ("DE012", "Felix", "Klein", "SAL", "Vertriebsmitarbeiter", EmploymentType.full_time, "1.00", "2023-02-15"),
        ("DE013", "Lisa", "Wolf", "HR", "Personalleiter", EmploymentType.full_time, "1.00", "2020-03-01"),
        ("DE014", "Martin", "Schaefer", "HR", "Personalsachbearbeiter", EmploymentType.full_time, "1.00", "2022-06-15"),
        ("DE015", "Eva", "Zimmermann", "ENG", "Junior Entwickler", EmploymentType.part_time, "0.50", "2024-03-01"),
        ("DE016", "Patrick", "Kraus", "SAL", "Vertriebsmitarbeiter", EmploymentType.contractor, "1.00", "2024-05-01"),
        ("DE017", "Nadine", "Hartmann", "FIN", "Bilanzbuchhalter", EmploymentType.full_time, "1.00", "2023-04-01"),
        ("DE018", "Christian", "Lange", "ENG", "Senior Entwickler", EmploymentType.full_time, "1.00", "2020-07-01"),
    ],
}

# Salary base amounts by position level and site (monthly gross)
SALARY_BASE = {
    "US": {"executive": 18000, "senior": 12000, "mid": 8500, "junior": 5500},
    "UK": {"executive": 12000, "senior": 8500, "mid": 5800, "junior": 3500},
    "DE": {"executive": 13000, "senior": 9000, "mid": 6500, "junior": 4000},
}

# Tax/benefit rates by site for payroll
PAYROLL_RATES = {
    "US": {"employer_tax": Decimal("0.0765"), "employee_tax": Decimal("0.22"), "benefits": Decimal("0.08")},
    "UK": {"employer_tax": Decimal("0.138"), "employee_tax": Decimal("0.20"), "benefits": Decimal("0.05")},
    "DE": {"employer_tax": Decimal("0.2075"), "employee_tax": Decimal("0.21"), "benefits": Decimal("0.04")},
}


# ---------------------------------------------------------------------------
# Fixed Assets data
# ---------------------------------------------------------------------------
ASSETS_DATA = {
    "US": [
        ("US-BLD-001", "Corporate Headquarters", AssetCategory.buildings, "2015-01-15", 5500000, 480, 500000, "New York, NY"),
        ("US-BLD-002", "Warehouse Facility", AssetCategory.buildings, "2018-06-01", 2200000, 360, 200000, "Newark, NJ"),
        ("US-MCH-001", "CNC Milling Machine", AssetCategory.machinery, "2020-03-15", 450000, 120, 45000, "Newark Plant"),
        ("US-MCH-002", "Packaging Line A", AssetCategory.machinery, "2021-01-10", 280000, 96, 20000, "Newark Plant"),
        ("US-MCH-003", "Industrial Robot Arm", AssetCategory.machinery, "2022-07-01", 350000, 120, 30000, "Newark Plant"),
        ("US-VEH-001", "Delivery Van - Ford Transit", AssetCategory.vehicles, "2021-09-01", 42000, 60, 8000, "Fleet"),
        ("US-VEH-002", "Company Car - Tesla Model 3", AssetCategory.vehicles, "2022-03-15", 55000, 60, 15000, "Executive"),
        ("US-IT-001", "Server Cluster - Primary DC", AssetCategory.it_equipment, "2022-01-01", 180000, 48, 10000, "Data Center"),
        ("US-IT-002", "Network Infrastructure", AssetCategory.it_equipment, "2021-06-15", 95000, 48, 5000, "HQ"),
        ("US-IT-003", "Laptops & Workstations (Batch)", AssetCategory.it_equipment, "2023-01-15", 85000, 36, 5000, "Various"),
        ("US-FUR-001", "Office Furniture - HQ", AssetCategory.furniture, "2019-06-01", 120000, 84, 10000, "HQ"),
        ("US-FUR-002", "Meeting Room AV Equipment", AssetCategory.furniture, "2022-04-01", 45000, 60, 3000, "HQ"),
        ("US-INT-001", "ERP Software License", AssetCategory.intangible, "2021-01-01", 250000, 60, 0, None),
    ],
    "UK": [
        ("UK-BLD-001", "London Office", AssetCategory.buildings, "2016-03-01", 3800000, 480, 350000, "London EC2"),
        ("UK-BLD-002", "Distribution Centre", AssetCategory.buildings, "2019-09-15", 1800000, 360, 150000, "Birmingham"),
        ("UK-MCH-001", "Assembly Line Alpha", AssetCategory.machinery, "2020-07-01", 320000, 120, 25000, "Birmingham"),
        ("UK-MCH-002", "Quality Testing Rig", AssetCategory.machinery, "2022-02-15", 185000, 96, 15000, "Birmingham"),
        ("UK-VEH-001", "Delivery Van - Mercedes Sprinter", AssetCategory.vehicles, "2021-11-01", 38000, 60, 7000, "Fleet"),
        ("UK-VEH-002", "Company Car - BMW 3 Series", AssetCategory.vehicles, "2023-01-15", 48000, 60, 12000, "Executive"),
        ("UK-IT-001", "Cloud Server Infrastructure", AssetCategory.it_equipment, "2022-04-01", 120000, 48, 5000, "Data Center"),
        ("UK-IT-002", "Office IT Equipment", AssetCategory.it_equipment, "2023-03-01", 65000, 36, 3000, "London"),
        ("UK-FUR-001", "Office Fitout - London", AssetCategory.furniture, "2020-01-15", 95000, 84, 8000, "London"),
        ("UK-FUR-002", "Canteen Equipment", AssetCategory.furniture, "2021-08-01", 28000, 60, 2000, "London"),
        ("UK-INT-001", "CRM Software License", AssetCategory.intangible, "2021-06-01", 180000, 60, 0, None),
    ],
    "DE": [
        ("DE-BLD-001", "Frankfurt Office", AssetCategory.buildings, "2017-05-01", 4200000, 480, 400000, "Frankfurt am Main"),
        ("DE-BLD-002", "Production Facility", AssetCategory.buildings, "2018-11-15", 2800000, 360, 250000, "Stuttgart"),
        ("DE-MCH-001", "Precision Laser Cutter", AssetCategory.machinery, "2020-02-01", 520000, 120, 50000, "Stuttgart"),
        ("DE-MCH-002", "Automated Welding System", AssetCategory.machinery, "2021-05-15", 380000, 96, 30000, "Stuttgart"),
        ("DE-MCH-003", "3D Printing Array", AssetCategory.machinery, "2023-01-01", 290000, 84, 20000, "Stuttgart"),
        ("DE-VEH-001", "Delivery Van - VW Crafter", AssetCategory.vehicles, "2021-07-15", 45000, 60, 9000, "Fleet"),
        ("DE-VEH-002", "Company Car - Audi A4", AssetCategory.vehicles, "2022-10-01", 52000, 60, 14000, "Executive"),
        ("DE-VEH-003", "Company Car - BMW 5 Series", AssetCategory.vehicles, "2023-04-01", 62000, 60, 16000, "Executive"),
        ("DE-IT-001", "On-premise Server Farm", AssetCategory.it_equipment, "2021-09-01", 200000, 48, 15000, "Frankfurt DC"),
        ("DE-IT-002", "Workstation Fleet", AssetCategory.it_equipment, "2022-06-15", 110000, 36, 8000, "Various"),
        ("DE-IT-003", "Security & Firewall Appliances", AssetCategory.it_equipment, "2023-02-01", 75000, 48, 5000, "Frankfurt DC"),
        ("DE-FUR-001", "Office Furniture - Frankfurt", AssetCategory.furniture, "2019-08-15", 140000, 84, 12000, "Frankfurt"),
        ("DE-FUR-002", "Standing Desks (Batch)", AssetCategory.furniture, "2022-11-01", 35000, 60, 3000, "Frankfurt"),
        ("DE-INT-001", "SAP License", AssetCategory.intangible, "2020-01-01", 350000, 60, 0, None),
        ("DE-INT-002", "Patent Portfolio", AssetCategory.intangible, "2019-04-01", 180000, 120, 0, None),
    ],
}


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------
async def seed() -> None:
    async with async_session_factory() as session:
        # ===================================================================
        # 1. TRUNCATE all tables
        # ===================================================================
        print("[1/14] Truncating all tables...")
        for tbl in ALL_TABLES:
            try:
                await session.execute(text(f"TRUNCATE TABLE {tbl} CASCADE"))
            except Exception:
                pass  # Table may not exist yet
        await session.commit()

        # ===================================================================
        # 2. SITES
        # ===================================================================
        print("[2/14] Creating sites...")
        sites = [
            Site(id=SITE_US_ID, name="ConsolidaSuite US", country="United States", local_currency="USD"),
            Site(id=SITE_UK_ID, name="ConsolidaSuite UK", country="United Kingdom", local_currency="GBP"),
            Site(id=SITE_DE_ID, name="ConsolidaSuite DE", country="Germany", local_currency="EUR"),
        ]
        session.add_all(sites)
        await session.flush()

        # ===================================================================
        # 3. USERS (re-create admin + new users)
        # ===================================================================
        print("[3/14] Creating users...")
        hashed_pw = hash_password(PASSWORD)
        users = [
            User(id=ADMIN_ID, email="admin@consolidasuite.com", hashed_password=hashed_pw,
                 full_name="System Admin", role=UserRole.admin),
            User(id=GROUP_CFO_ID, email="group.cfo@consolidasuite.com", hashed_password=hashed_pw,
                 full_name="Maria Rossi", role=UserRole.group_cfo),
            User(id=LOCAL_CFO_US_ID, email="cfo.us@consolidasuite.com", hashed_password=hashed_pw,
                 full_name="James Wilson", role=UserRole.local_cfo),
            User(id=LOCAL_CFO_UK_ID, email="cfo.uk@consolidasuite.com", hashed_password=hashed_pw,
                 full_name="Sarah Thompson", role=UserRole.local_cfo),
            User(id=LOCAL_CFO_DE_ID, email="cfo.de@consolidasuite.com", hashed_password=hashed_pw,
                 full_name="Klaus Mueller", role=UserRole.local_cfo),
        ]
        session.add_all(users)
        await session.flush()

        # User-Site assignments
        await session.execute(user_site_association.insert().values([
            {"user_id": LOCAL_CFO_US_ID, "site_id": SITE_US_ID},
            {"user_id": LOCAL_CFO_UK_ID, "site_id": SITE_UK_ID},
            {"user_id": LOCAL_CFO_DE_ID, "site_id": SITE_DE_ID},
        ]))

        # ===================================================================
        # 4. FX RATES
        # ===================================================================
        print("[4/14] Creating FX rates...")
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

        # ===================================================================
        # 5. FINANCIAL STATEMENTS (Jul-Dec 2025)
        # ===================================================================
        print("[5/14] Creating financial statements...")
        stmt_count = 0
        line_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for month in range(7, 13):
                for stype, line_fn in [
                    (StatementType.income_statement, income_statement_lines),
                    (StatementType.balance_sheet, balance_sheet_lines),
                    (StatementType.cash_flow, cash_flow_lines),
                ]:
                    stmt = FinancialStatement(
                        site_id=site_id, statement_type=stype,
                        period_year=2025, period_month=month, currency=currency,
                        status=StatementStatus.approved, uploaded_by=uploader_id,
                        approved_by=GROUP_CFO_ID,
                        approved_at=datetime(2025, month, 28, tzinfo=timezone.utc),
                    )
                    session.add(stmt)
                    await session.flush()
                    for line in line_fn(site_key, month):
                        session.add(FinancialLineItem(
                            statement_id=stmt.id,
                            line_item_code=line["code"],
                            line_item_name=line["name"],
                            parent_code=line["parent"],
                            amount=line["amount"],
                        ))
                        line_count += 1
                    stmt_count += 1
        await session.flush()
        print(f"         {stmt_count} statements, {line_count} line items")

        # ===================================================================
        # 6. BUDGET ENTRIES
        # ===================================================================
        print("[6/14] Creating budget entries...")
        budget_lines = [
            ("REV", 2_600_000), ("COGS", -1_250_000), ("GP", 1_350_000),
            ("OPEX", -870_000), ("EBIT", 480_000), ("NI", 360_000),
        ]
        budget_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            mult = {"US": Decimal("1.0"), "UK": Decimal("0.7"), "DE": Decimal("0.85")}[site_key]
            for month in range(1, 13):
                for code, base_amount in budget_lines:
                    session.add(BudgetEntry(
                        site_id=site_id, line_item_code=code,
                        period_year=2025, period_month=month,
                        budget_amount=(Decimal(str(base_amount)) * mult).quantize(Decimal("0.01")),
                        created_by=uploader_id,
                    ))
                    budget_count += 1
        await session.flush()
        print(f"         {budget_count} budget entries")

        # ===================================================================
        # 7. KPI TARGETS
        # ===================================================================
        print("[7/14] Creating KPI targets...")
        kpi_count = 0
        # Group-level (consolidated) targets - no site
        group_targets = [
            ("Revenue Growth", "financial", Decimal("12.5000")),
            ("EBIT Margin", "financial", Decimal("18.0000")),
            ("Net Income Margin", "financial", Decimal("13.5000")),
            ("Employee Turnover Rate", "hr", Decimal("8.0000")),
            ("Debt-to-Equity Ratio", "treasury", Decimal("1.2000")),
            ("Tax Compliance Rate", "tax", Decimal("100.0000")),
        ]
        for kpi_name, kpi_cat, target_val in group_targets:
            session.add(KPITarget(
                site_id=None, kpi_name=kpi_name, kpi_category=kpi_cat,
                target_value=target_val, period_year=2025, period_month=None,
                created_by=GROUP_CFO_ID,
            ))
            kpi_count += 1

        # Per-site targets
        site_targets = {
            "US": [
                ("Revenue Growth", "financial", Decimal("15.0000")),
                ("EBIT Margin", "financial", Decimal("20.0000")),
                ("Headcount", "hr", Decimal("17.0000")),
            ],
            "UK": [
                ("Revenue Growth", "financial", Decimal("10.0000")),
                ("EBIT Margin", "financial", Decimal("16.0000")),
                ("Headcount", "hr", Decimal("15.0000")),
            ],
            "DE": [
                ("Revenue Growth", "financial", Decimal("11.0000")),
                ("EBIT Margin", "financial", Decimal("17.0000")),
                ("Headcount", "hr", Decimal("18.0000")),
            ],
        }
        site_id_map = {"US": SITE_US_ID, "UK": SITE_UK_ID, "DE": SITE_DE_ID}
        for site_key, targets in site_targets.items():
            for kpi_name, kpi_cat, target_val in targets:
                session.add(KPITarget(
                    site_id=site_id_map[site_key], kpi_name=kpi_name, kpi_category=kpi_cat,
                    target_value=target_val, period_year=2025, period_month=None,
                    created_by=GROUP_CFO_ID,
                ))
                kpi_count += 1
        await session.flush()
        print(f"         {kpi_count} KPI targets")

        # ===================================================================
        # 8. CHART OF ACCOUNTS
        # ===================================================================
        print("[8/14] Creating chart of accounts...")
        # Group accounts
        group_account_objs = {}
        for code, name, acct_type, parent, order in GROUP_ACCOUNTS_DATA:
            ga = GroupAccount(
                code=code, name=name, account_type=acct_type,
                parent_code=parent, display_order=order,
            )
            session.add(ga)
            group_account_objs[code] = ga
        await session.flush()

        # Site accounts + mappings
        sa_count = 0
        mapping_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for local_code, local_name, acct_type, parent, order, group_code in SITE_ACCOUNTS_DATA[site_key]:
                sa = SiteAccount(
                    site_id=site_id, code=local_code, name=local_name,
                    account_type=acct_type, parent_code=parent, display_order=order,
                )
                session.add(sa)
                await session.flush()
                # Create mapping to group account
                if group_code in group_account_objs:
                    session.add(AccountMapping(
                        site_account_id=sa.id,
                        group_account_id=group_account_objs[group_code].id,
                        created_by=ADMIN_ID,
                    ))
                    mapping_count += 1
                sa_count += 1
        await session.flush()
        print(f"         {len(GROUP_ACCOUNTS_DATA)} group accounts, {sa_count} site accounts, {mapping_count} mappings")

        # ===================================================================
        # 9. HR & PAYROLL
        # ===================================================================
        print("[9/14] Creating HR data (departments, positions, employees, salaries)...")

        # Departments
        dept_objs = {}  # (site_key, code) -> Department
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for code, name in DEPARTMENTS_DATA[site_key]:
                dept = Department(site_id=site_id, name=name, code=code)
                session.add(dept)
                dept_objs[(site_key, code)] = dept
        await session.flush()

        # Positions
        pos_objs = {}  # (site_key, title) -> Position
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for dept_code, title, level in POSITIONS_DATA[site_key]:
                pos = Position(
                    site_id=site_id, title=title,
                    department_id=dept_objs[(site_key, dept_code)].id, level=level,
                )
                session.add(pos)
                pos_objs[(site_key, title)] = pos
        await session.flush()

        # Employees
        emp_objs = {}  # employee_code -> Employee
        emp_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for emp_code, first, last, dept_code, pos_title, emp_type, fte, start in EMPLOYEES_DATA[site_key]:
                emp = Employee(
                    site_id=site_id,
                    employee_code=emp_code,
                    first_name=first,
                    last_name=last,
                    email=f"{first.lower()}.{last.lower()}@consolidasuite.com",
                    position_id=pos_objs[(site_key, pos_title)].id,
                    department_id=dept_objs[(site_key, dept_code)].id,
                    employment_type=emp_type,
                    fte_ratio=Decimal(fte),
                    start_date=date.fromisoformat(start),
                )
                session.add(emp)
                emp_objs[emp_code] = emp
                emp_count += 1
        await session.flush()

        # Salary records (Oct-Dec 2025)
        salary_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            rates = PAYROLL_RATES[site_key]
            for emp_data in EMPLOYEES_DATA[site_key]:
                emp_code = emp_data[0]
                pos_title = emp_data[4]
                emp_type = emp_data[5]
                fte = Decimal(emp_data[6])
                emp = emp_objs[emp_code]

                # Find level for this position
                level = "mid"
                for dept_code, title, lvl in POSITIONS_DATA[site_key]:
                    if title == pos_title:
                        level = lvl
                        break

                base_gross = Decimal(str(SALARY_BASE[site_key][level])) * fte
                if emp_type == EmploymentType.contractor:
                    # Contractors get higher gross but no benefits/employer taxes
                    base_gross = base_gross * Decimal("1.3")

                for month in [10, 11, 12]:
                    gross = base_gross.quantize(Decimal("0.01"))
                    if emp_type == EmploymentType.contractor:
                        employer_taxes = Decimal("0.00")
                        employee_taxes = (gross * Decimal("0.15")).quantize(Decimal("0.01"))
                        benefits = Decimal("0.00")
                    else:
                        employer_taxes = (gross * rates["employer_tax"]).quantize(Decimal("0.01"))
                        employee_taxes = (gross * rates["employee_tax"]).quantize(Decimal("0.01"))
                        benefits = (gross * rates["benefits"]).quantize(Decimal("0.01"))

                    net = gross - employee_taxes
                    total_cost = gross + employer_taxes + benefits
                    bonus = Decimal("0.00")
                    if month == 12:
                        bonus = (gross * Decimal("0.10")).quantize(Decimal("0.01"))

                    session.add(SalaryRecord(
                        employee_id=emp.id,
                        period_year=2025, period_month=month,
                        currency=currency,
                        gross_salary=gross,
                        net_salary=net,
                        employer_taxes=employer_taxes,
                        employee_taxes=employee_taxes,
                        benefits=benefits,
                        total_cost=total_cost,
                        overtime_hours=Decimal("0.00"),
                        bonus=bonus,
                    ))
                    salary_count += 1
        await session.flush()
        print(f"         {len(dept_objs)} departments, {len(pos_objs)} positions, {emp_count} employees, {salary_count} salary records")

        # ===================================================================
        # 10. INTERCOMPANY
        # ===================================================================
        print("[10/14] Creating intercompany transactions...")

        ic_invoices_data = [
            # (invoice_number, sender, receiver, date, due, currency, amount, desc, category, status)
            ("IC-2025-001", SITE_US_ID, SITE_UK_ID, "2025-07-15", "2025-08-15", "USD", 125000, "IT shared services Q3 2025", ICInvoiceCategory.services, ICInvoiceStatus.matched),
            ("IC-2025-002", SITE_UK_ID, SITE_US_ID, "2025-07-15", "2025-08-15", "USD", 125000, "IT shared services Q3 2025 (mirror)", ICInvoiceCategory.services, ICInvoiceStatus.matched),
            ("IC-2025-003", SITE_US_ID, SITE_DE_ID, "2025-08-01", "2025-09-01", "EUR", 85000, "Management fee Aug 2025", ICInvoiceCategory.management_fee, ICInvoiceStatus.matched),
            ("IC-2025-004", SITE_DE_ID, SITE_US_ID, "2025-08-01", "2025-09-01", "EUR", 85000, "Management fee Aug 2025 (mirror)", ICInvoiceCategory.management_fee, ICInvoiceStatus.matched),
            ("IC-2025-005", SITE_DE_ID, SITE_UK_ID, "2025-09-15", "2025-10-15", "EUR", 210000, "Component supply - Batch 42", ICInvoiceCategory.goods, ICInvoiceStatus.matched),
            ("IC-2025-006", SITE_UK_ID, SITE_DE_ID, "2025-09-15", "2025-10-15", "EUR", 210000, "Component supply - Batch 42 (mirror)", ICInvoiceCategory.goods, ICInvoiceStatus.matched),
            ("IC-2025-007", SITE_US_ID, SITE_UK_ID, "2025-10-01", "2025-11-01", "USD", 95000, "Royalty payment Q3 2025", ICInvoiceCategory.royalty, ICInvoiceStatus.sent),
            ("IC-2025-008", SITE_UK_ID, SITE_US_ID, "2025-10-01", "2025-11-01", "USD", 93500, "Royalty payment Q3 2025 (mirror - difference)", ICInvoiceCategory.royalty, ICInvoiceStatus.disputed),
            ("IC-2025-009", SITE_DE_ID, SITE_US_ID, "2025-11-01", "2025-12-01", "EUR", 175000, "Engineering services Nov 2025", ICInvoiceCategory.services, ICInvoiceStatus.sent),
            ("IC-2025-010", SITE_US_ID, SITE_DE_ID, "2025-11-15", "2025-12-15", "USD", 60000, "Management fee Nov 2025", ICInvoiceCategory.management_fee, ICInvoiceStatus.draft),
        ]

        ic_inv_objs = {}
        for inv_data in ic_invoices_data:
            inv_num, sender, receiver, inv_date, due, curr, amount, desc, cat, status = inv_data
            inv = ICInvoice(
                invoice_number=inv_num,
                sender_site_id=sender, receiver_site_id=receiver,
                invoice_date=date.fromisoformat(inv_date),
                due_date=date.fromisoformat(due),
                currency=curr, amount=Decimal(str(amount)),
                description=desc, category=cat, status=status,
                created_by=ADMIN_ID,
            )
            session.add(inv)
            ic_inv_objs[inv_num] = inv
        await session.flush()

        # Set matched_with for matched pairs
        matched_pairs = [
            ("IC-2025-001", "IC-2025-002"),
            ("IC-2025-003", "IC-2025-004"),
            ("IC-2025-005", "IC-2025-006"),
        ]
        for a, b in matched_pairs:
            ic_inv_objs[a].matched_with_id = ic_inv_objs[b].id
            ic_inv_objs[b].matched_with_id = ic_inv_objs[a].id
        await session.flush()

        # IC Loans
        ic_loans_data = [
            (SITE_US_ID, SITE_UK_ID, "USD", 2000000, "0.0450", "2024-01-01", "2027-01-01", 1650000, ICLoanStatus.active),
            (SITE_US_ID, SITE_DE_ID, "EUR", 1500000, "0.0380", "2024-06-01", "2028-06-01", 1400000, ICLoanStatus.active),
            (SITE_DE_ID, SITE_UK_ID, "EUR", 500000, "0.0400", "2023-01-01", "2025-12-31", 50000, ICLoanStatus.active),
        ]
        for lender, borrower, curr, principal, rate, start, maturity, outstanding, status in ic_loans_data:
            session.add(ICLoan(
                lender_site_id=lender, borrower_site_id=borrower,
                currency=curr, principal_amount=Decimal(str(principal)),
                interest_rate=Decimal(rate),
                start_date=date.fromisoformat(start),
                maturity_date=date.fromisoformat(maturity),
                outstanding_balance=Decimal(str(outstanding)),
                status=status, created_by=ADMIN_ID,
            ))
        await session.flush()
        print(f"         {len(ic_invoices_data)} IC invoices, {len(ic_loans_data)} IC loans")

        # ===================================================================
        # 11. FIXED ASSETS
        # ===================================================================
        print("[11/14] Creating fixed assets...")
        asset_count = 0
        for site_key, site_id, currency, uploader_id in SITE_MAP:
            for asset_data in ASSETS_DATA[site_key]:
                code, name, category, acq_date_str, acq_cost, useful_life, residual, location = asset_data
                acq_date = date.fromisoformat(acq_date_str)
                acq_cost_d = Decimal(str(acq_cost))
                residual_d = Decimal(str(residual))
                # Calculate depreciation based on months elapsed to Dec 2025
                ref_date = date(2025, 12, 31)
                months_elapsed = (ref_date.year - acq_date.year) * 12 + (ref_date.month - acq_date.month)
                months_elapsed = min(months_elapsed, useful_life)
                monthly_dep = ((acq_cost_d - residual_d) / Decimal(str(useful_life))).quantize(Decimal("0.01"))
                accum_dep = (monthly_dep * months_elapsed).quantize(Decimal("0.01"))
                nbv = (acq_cost_d - accum_dep).quantize(Decimal("0.01"))

                status = AssetStatus.active
                if months_elapsed >= useful_life:
                    status = AssetStatus.fully_depreciated
                    nbv = residual_d

                session.add(Asset(
                    site_id=site_id, asset_code=code, name=name, category=category,
                    acquisition_date=acq_date, acquisition_cost=acq_cost_d,
                    currency=currency, useful_life_months=useful_life,
                    depreciation_method=DepreciationMethod.straight_line,
                    residual_value=residual_d, accumulated_depreciation=accum_dep,
                    net_book_value=nbv, status=status, location=location,
                    created_by=uploader_id,
                ))
                asset_count += 1
        await session.flush()
        print(f"         {asset_count} assets")

        # ===================================================================
        # 12. TAX & COMPLIANCE
        # ===================================================================
        print("[12/14] Creating tax jurisdictions and filings...")

        # Tax jurisdictions
        tax_jurisdictions_data = [
            (SITE_US_ID, Decimal("0.2100"), Decimal("0.0000"), Decimal("0.3000"), Decimal("0.0765"), Decimal("0.0765"), 1,
             "Federal corporate tax rate 21%. No federal VAT/sales tax.", "2025-01-01"),
            (SITE_UK_ID, Decimal("0.2500"), Decimal("0.2000"), Decimal("0.2000"), Decimal("0.1380"), Decimal("0.1200"), 4,
             "UK corporation tax 25%. Standard VAT 20%.", "2025-01-01"),
            (SITE_DE_ID, Decimal("0.2983"), Decimal("0.1900"), Decimal("0.2500"), Decimal("0.2075"), Decimal("0.2025"), 1,
             "Corporate tax ~30% (15% KSt + ~15% GewSt + Soli). VAT 19%.", "2025-01-01"),
        ]
        for site_id, corp, vat, wht, ss_er, ss_ee, fy_start, notes, eff in tax_jurisdictions_data:
            session.add(TaxJurisdiction(
                site_id=site_id, corporate_tax_rate=corp, vat_rate=vat,
                withholding_tax_rate=wht, social_security_employer_rate=ss_er,
                social_security_employee_rate=ss_ee, fiscal_year_start_month=fy_start,
                notes=notes, effective_from=date.fromisoformat(eff),
            ))
        await session.flush()

        # Tax filings
        filing_count = 0
        tax_filings_data = [
            # US filings
            (SITE_US_ID, FilingType.corporate_tax, 2025, None, "2026-03-15", "2025-09-30", FilingStatus.filed, 1850000, "USD", "Q1-Q3 estimated payments"),
            (SITE_US_ID, FilingType.corporate_tax, 2025, None, "2026-03-15", None, FilingStatus.pending, None, "USD", "Annual corporate tax return"),
            (SITE_US_ID, FilingType.withholding_tax, 2025, 1, "2025-04-30", "2025-04-15", FilingStatus.filed, 125000, "USD", "Q1 withholding"),
            (SITE_US_ID, FilingType.withholding_tax, 2025, 2, "2025-07-31", "2025-07-20", FilingStatus.filed, 130000, "USD", "Q2 withholding"),
            (SITE_US_ID, FilingType.withholding_tax, 2025, 3, "2025-10-31", "2025-10-28", FilingStatus.filed, 128000, "USD", "Q3 withholding"),
            (SITE_US_ID, FilingType.withholding_tax, 2025, 4, "2026-01-31", None, FilingStatus.pending, None, "USD", "Q4 withholding"),
            (SITE_US_ID, FilingType.transfer_pricing, 2025, None, "2026-06-15", None, FilingStatus.in_progress, None, "USD", "TP documentation"),
            (SITE_US_ID, FilingType.annual_accounts, 2025, None, "2026-04-15", None, FilingStatus.in_progress, None, "USD", "Annual statutory accounts"),
            # UK filings
            (SITE_UK_ID, FilingType.corporate_tax, 2025, None, "2026-04-01", None, FilingStatus.pending, None, "GBP", "CT600 return"),
            (SITE_UK_ID, FilingType.vat_return, 2025, 1, "2025-05-07", "2025-05-01", FilingStatus.filed, 95000, "GBP", "Q1 VAT return"),
            (SITE_UK_ID, FilingType.vat_return, 2025, 2, "2025-08-07", "2025-08-03", FilingStatus.filed, 102000, "GBP", "Q2 VAT return"),
            (SITE_UK_ID, FilingType.vat_return, 2025, 3, "2025-11-07", "2025-11-05", FilingStatus.filed, 98000, "GBP", "Q3 VAT return"),
            (SITE_UK_ID, FilingType.vat_return, 2025, 4, "2026-02-07", None, FilingStatus.pending, None, "GBP", "Q4 VAT return"),
            (SITE_UK_ID, FilingType.annual_accounts, 2025, None, "2026-06-30", None, FilingStatus.pending, None, "GBP", "Companies House filing"),
            (SITE_UK_ID, FilingType.transfer_pricing, 2025, None, "2026-04-01", None, FilingStatus.pending, None, "GBP", "TP documentation"),
            # DE filings
            (SITE_DE_ID, FilingType.corporate_tax, 2025, None, "2026-07-31", None, FilingStatus.pending, None, "EUR", "KSt + GewSt return"),
            (SITE_DE_ID, FilingType.vat_return, 2025, 1, "2025-04-10", "2025-04-08", FilingStatus.filed, 145000, "EUR", "Q1 USt-Voranmeldung"),
            (SITE_DE_ID, FilingType.vat_return, 2025, 2, "2025-07-10", "2025-07-09", FilingStatus.filed, 152000, "EUR", "Q2 USt-Voranmeldung"),
            (SITE_DE_ID, FilingType.vat_return, 2025, 3, "2025-10-10", "2025-10-08", FilingStatus.filed, 148000, "EUR", "Q3 USt-Voranmeldung"),
            (SITE_DE_ID, FilingType.vat_return, 2025, 4, "2026-01-10", None, FilingStatus.overdue, None, "EUR", "Q4 USt-Voranmeldung - OVERDUE"),
            (SITE_DE_ID, FilingType.annual_accounts, 2025, None, "2026-12-31", None, FilingStatus.pending, None, "EUR", "Bundesanzeiger filing"),
            (SITE_DE_ID, FilingType.transfer_pricing, 2025, None, "2026-07-31", None, FilingStatus.pending, None, "EUR", "Verrechnungspreisdokumentation"),
        ]
        for fd in tax_filings_data:
            site_id, ftype, year, quarter, due, filed, status, amount, curr, notes = fd
            session.add(TaxFiling(
                site_id=site_id, filing_type=ftype, period_year=year, period_quarter=quarter,
                due_date=date.fromisoformat(due),
                filed_date=date.fromisoformat(filed) if filed else None,
                status=status,
                amount=Decimal(str(amount)) if amount else None,
                currency=curr, notes=notes, created_by=ADMIN_ID,
            ))
            filing_count += 1
        await session.flush()
        print(f"         3 jurisdictions, {filing_count} filings")

        # ===================================================================
        # 13. TREASURY
        # ===================================================================
        print("[13/14] Creating treasury data...")

        # Bank accounts
        bank_accounts_data = [
            # US
            (SITE_US_ID, "JPMorgan Chase", "****4521", None, "CHASUS33", "USD", BankAccountType.current, True),
            (SITE_US_ID, "Bank of America", "****8833", None, "BOFAUS3N", "USD", BankAccountType.savings, False),
            (SITE_US_ID, "Citibank", "****2290", None, "CITIUS33", "USD", BankAccountType.credit_line, False),
            # UK
            (SITE_UK_ID, "Barclays", "****6712", "GB29BARC20000012345678", "BARCGB22", "GBP", BankAccountType.current, True),
            (SITE_UK_ID, "HSBC", "****9041", "GB82HSBC40000087654321", "HSBCGB2L", "GBP", BankAccountType.savings, False),
            (SITE_UK_ID, "NatWest", "****3377", "GB15NWBK60000011223344", "NWBKGB2L", "GBP", BankAccountType.current, False),
            # DE
            (SITE_DE_ID, "Deutsche Bank", "****1155", "DE89370400440532013000", "DEUTDEFF", "EUR", BankAccountType.current, True),
            (SITE_DE_ID, "Commerzbank", "****7744", "DE27100400000532013001", "COBADEFF", "EUR", BankAccountType.savings, False),
            (SITE_DE_ID, "KfW", "****5588", "DE12300500000001234567", "KFWIDEFF", "EUR", BankAccountType.deposit, False),
        ]
        ba_objs = []
        for bd in bank_accounts_data:
            site_id, bank, acct, iban, swift, curr, atype, primary = bd
            ba = BankAccount(
                site_id=site_id, bank_name=bank, account_number=acct,
                iban=iban, swift_bic=swift, currency=curr,
                account_type=atype, is_primary=primary,
            )
            session.add(ba)
            ba_objs.append(ba)
        await session.flush()

        # Cash positions (Oct-Dec 2025, end of month)
        cash_balances = [
            # US - JPMorgan
            (ba_objs[0], [("2025-10-31", 2150000), ("2025-11-30", 2280000), ("2025-12-31", 2100000)]),
            # US - BoA savings
            (ba_objs[1], [("2025-10-31", 1500000), ("2025-11-30", 1520000), ("2025-12-31", 1550000)]),
            # UK - Barclays
            (ba_objs[3], [("2025-10-31", 1420000), ("2025-11-30", 1380000), ("2025-12-31", 1470000)]),
            # UK - HSBC savings
            (ba_objs[4], [("2025-10-31", 800000), ("2025-11-30", 810000), ("2025-12-31", 820000)]),
            # DE - Deutsche Bank
            (ba_objs[6], [("2025-10-31", 1650000), ("2025-11-30", 1720000), ("2025-12-31", 1785000)]),
            # DE - Commerzbank
            (ba_objs[7], [("2025-10-31", 950000), ("2025-11-30", 960000), ("2025-12-31", 980000)]),
        ]
        cp_count = 0
        for ba, positions in cash_balances:
            for bal_date, balance in positions:
                session.add(CashPosition(
                    bank_account_id=ba.id,
                    balance_date=date.fromisoformat(bal_date),
                    balance=Decimal(str(balance)),
                    currency=ba.currency,
                ))
                cp_count += 1
        await session.flush()

        # Debt instruments
        debt_data = [
            # US
            (SITE_US_ID, InstrumentType.term_loan, "JPMorgan Chase", "USD", 5000000, 3800000, "0.0525", "2022-01-01", "2027-01-01", "quarterly"),
            (SITE_US_ID, InstrumentType.revolving_credit, "Bank of America", "USD", 3000000, 800000, "0.0600", "2023-06-01", "2026-06-01", "monthly"),
            # UK
            (SITE_UK_ID, InstrumentType.term_loan, "Barclays", "GBP", 3000000, 2400000, "0.0480", "2022-06-01", "2027-06-01", "quarterly"),
            (SITE_UK_ID, InstrumentType.overdraft, "HSBC", "GBP", 500000, 150000, "0.0700", "2025-01-01", "2026-01-01", None),
            (SITE_UK_ID, InstrumentType.lease, "Lloyds Leasing", "GBP", 800000, 520000, "0.0420", "2023-01-01", "2028-01-01", "monthly"),
            # DE
            (SITE_DE_ID, InstrumentType.term_loan, "Deutsche Bank", "EUR", 4000000, 3200000, "0.0390", "2022-03-01", "2028-03-01", "quarterly"),
            (SITE_DE_ID, InstrumentType.bond, "Corporate Bond 2025", "EUR", 2000000, 2000000, "0.0350", "2025-06-01", "2030-06-01", "semi-annual"),
            (SITE_DE_ID, InstrumentType.revolving_credit, "Commerzbank", "EUR", 1500000, 400000, "0.0450", "2024-01-01", "2027-01-01", "monthly"),
        ]
        for dd in debt_data:
            site_id, itype, lender, curr, principal, outstanding, rate, start, maturity, schedule = dd
            session.add(DebtInstrument(
                site_id=site_id, instrument_type=itype, lender=lender,
                currency=curr, principal_amount=Decimal(str(principal)),
                outstanding_amount=Decimal(str(outstanding)),
                interest_rate=Decimal(rate),
                start_date=date.fromisoformat(start),
                maturity_date=date.fromisoformat(maturity),
                repayment_schedule=schedule, status=DebtStatus.active,
            ))
        await session.flush()
        print(f"         {len(bank_accounts_data)} bank accounts, {cp_count} cash positions, {len(debt_data)} debt instruments")

        # ===================================================================
        # 14. LEGAL ENTITIES
        # ===================================================================
        print("[14/14] Creating legal entities...")

        # Parent holding entity (use US site)
        holding = LegalEntity(
            site_id=SITE_US_ID,
            entity_name="ConsolidaSuite Holdings Inc.",
            registration_number="DE-HRB-123456",
            tax_id="US-EIN-12-3456789",
            jurisdiction="Delaware, United States",
            entity_type=EntityType.corporation,
            incorporation_date=date(2015, 1, 15),
            share_capital=Decimal("10000000.00"),
            share_capital_currency="USD",
            parent_entity_id=None,
            ownership_percentage=None,
            registered_address="1209 Orange Street, Wilmington, DE 19801, USA",
        )
        session.add(holding)
        await session.flush()

        # Subsidiary entities
        sub_us = LegalEntity(
            site_id=SITE_US_ID,
            entity_name="ConsolidaSuite US Inc.",
            registration_number="NY-LLC-789012",
            tax_id="US-EIN-98-7654321",
            jurisdiction="New York, United States",
            entity_type=EntityType.corporation,
            incorporation_date=date(2015, 3, 1),
            share_capital=Decimal("5000000.00"),
            share_capital_currency="USD",
            parent_entity_id=holding.id,
            ownership_percentage=Decimal("100.00"),
            registered_address="350 Fifth Avenue, New York, NY 10118, USA",
        )
        sub_uk = LegalEntity(
            site_id=SITE_UK_ID,
            entity_name="ConsolidaSuite UK Ltd.",
            registration_number="UK-CH-12345678",
            tax_id="GB-UTR-1234567890",
            jurisdiction="England & Wales",
            entity_type=EntityType.llc,
            incorporation_date=date(2016, 6, 15),
            share_capital=Decimal("3000000.00"),
            share_capital_currency="GBP",
            parent_entity_id=holding.id,
            ownership_percentage=Decimal("100.00"),
            registered_address="100 Bishopsgate, London EC2N 4AG, UK",
        )
        sub_de = LegalEntity(
            site_id=SITE_DE_ID,
            entity_name="ConsolidaSuite DE GmbH",
            registration_number="DE-HRB-654321",
            tax_id="DE-STID-123/456/78901",
            jurisdiction="Frankfurt, Germany",
            entity_type=EntityType.llc,
            incorporation_date=date(2017, 1, 10),
            share_capital=Decimal("4000000.00"),
            share_capital_currency="EUR",
            parent_entity_id=holding.id,
            ownership_percentage=Decimal("100.00"),
            registered_address="Taunusanlage 12, 60325 Frankfurt am Main, Germany",
        )
        session.add_all([sub_us, sub_uk, sub_de])
        await session.flush()

        # Directors
        directors_data = [
            # Holding
            (holding.id, "Maria Rossi", "Chairperson & Group CFO", "2015-01-15", "Italian"),
            (holding.id, "Robert Chen", "Non-Executive Director", "2016-03-01", "American"),
            (holding.id, "Helena Johansson", "Non-Executive Director", "2018-09-15", "Swedish"),
            # US
            (sub_us.id, "James Wilson", "Managing Director", "2019-03-15", "American"),
            (sub_us.id, "Maria Rossi", "Director", "2015-03-01", "Italian"),
            # UK
            (sub_uk.id, "Sarah Thompson", "Managing Director", "2019-04-01", "British"),
            (sub_uk.id, "Maria Rossi", "Director", "2016-06-15", "Italian"),
            (sub_uk.id, "William Edwards", "Company Secretary", "2018-06-01", "British"),
            # DE
            (sub_de.id, "Klaus Mueller", "Geschaeftsfuehrer", "2019-01-15", "German"),
            (sub_de.id, "Maria Rossi", "Geschaeftsfuehrerin", "2017-01-10", "Italian"),
        ]
        for entity_id, name, role, appt_date, nationality in directors_data:
            session.add(Director(
                entity_id=entity_id, full_name=name, role=role,
                appointment_date=date.fromisoformat(appt_date),
                nationality=nationality,
            ))
        await session.flush()

        # Statutory audits
        audits_data = [
            (holding.id, "KPMG", 2025, AuditStatus.in_progress, "2026-04-30", None, None, "Group consolidation audit"),
            (sub_us.id, "Deloitte", 2025, AuditStatus.in_progress, "2026-03-31", None, None, "US statutory audit"),
            (sub_uk.id, "PwC", 2025, AuditStatus.not_started, "2026-06-30", None, None, "UK Companies Act audit"),
            (sub_de.id, "EY", 2025, AuditStatus.not_started, "2026-07-31", None, None, "HGB/IFRS audit"),
            # Prior year - completed
            (holding.id, "KPMG", 2024, AuditStatus.final_report, "2025-04-30", "2025-04-15", AuditOpinion.unqualified, "Clean opinion"),
            (sub_us.id, "Deloitte", 2024, AuditStatus.filed, "2025-03-31", "2025-03-20", AuditOpinion.unqualified, "Clean opinion"),
            (sub_uk.id, "PwC", 2024, AuditStatus.filed, "2025-06-30", "2025-06-10", AuditOpinion.unqualified, "Clean opinion"),
            (sub_de.id, "EY", 2024, AuditStatus.filed, "2025-07-31", "2025-07-15", AuditOpinion.unqualified, "Uneingeschraenkter Bestaetigungsvermerk"),
        ]
        for entity_id, firm, year, status, due, completion, opinion, notes in audits_data:
            session.add(StatutoryAudit(
                entity_id=entity_id, audit_firm=firm, fiscal_year=year,
                status=status, due_date=date.fromisoformat(due),
                completion_date=date.fromisoformat(completion) if completion else None,
                opinion=opinion, notes=notes,
            ))
        await session.flush()
        print(f"         4 legal entities, {len(directors_data)} directors, {len(audits_data)} audits")

        # ===================================================================
        # COMMIT
        # ===================================================================
        await session.commit()
        print("\n" + "=" * 60)
        print("SEED COMPLETE!")
        print("=" * 60)
        print(f"  Sites:                3 (US, UK, DE)")
        print(f"  Users:                5 (admin + group_cfo + 3x local_cfo)")
        print(f"  Password for all:     {PASSWORD}")
        print(f"  FX rates:             36 (3 pairs x 12 months)")
        print(f"  Financial statements: {stmt_count}")
        print(f"  Financial line items: {line_count}")
        print(f"  Budget entries:       {budget_count}")
        print(f"  KPI targets:          {kpi_count}")
        print(f"  Group accounts:       {len(GROUP_ACCOUNTS_DATA)}")
        print(f"  Site accounts:        {sa_count}")
        print(f"  Account mappings:     {mapping_count}")
        print(f"  Departments:          {len(dept_objs)}")
        print(f"  Positions:            {len(pos_objs)}")
        print(f"  Employees:            {emp_count}")
        print(f"  Salary records:       {salary_count}")
        print(f"  IC invoices:          {len(ic_invoices_data)}")
        print(f"  IC loans:             {len(ic_loans_data)}")
        print(f"  Fixed assets:         {asset_count}")
        print(f"  Tax jurisdictions:    3")
        print(f"  Tax filings:          {filing_count}")
        print(f"  Bank accounts:        {len(bank_accounts_data)}")
        print(f"  Cash positions:       {cp_count}")
        print(f"  Debt instruments:     {len(debt_data)}")
        print(f"  Legal entities:       4 (1 holding + 3 subsidiaries)")
        print(f"  Directors:            {len(directors_data)}")
        print(f"  Statutory audits:     {len(audits_data)}")


if __name__ == "__main__":
    asyncio.run(seed())
