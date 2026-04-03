from __future__ import annotations

import uuid
from decimal import Decimal
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.budget import BudgetEntry
from app.models.financial_data import (
    FinancialLineItem,
    FinancialStatement,
    StatementStatus,
    StatementType,
)
from app.models.site import Site
from app.models.user import User, UserRole
from app.services.auth import hash_password

# ---------------------------------------------------------------------------
# Test database setup (SQLite async for tests)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for tests."""
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with the DB session overridden."""
    from app.api.deps import get_db
    from app.main import app

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Factory fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def sample_admin(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        email="admin@interfinops.test",
        hashed_password=hash_password("Admin1234!"),
        full_name="Test Admin",
        role=UserRole.admin,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_group_cfo(db_session: AsyncSession) -> User:
    """Create a group CFO user."""
    user = User(
        email="groupcfo@interfinops.test",
        hashed_password=hash_password("GroupCFO1!"),
        full_name="Test Group CFO",
        role=UserRole.group_cfo,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_site(db_session: AsyncSession) -> Site:
    """Create a sample site."""
    site = Site(
        name="Berlin Office",
        country="Germany",
        local_currency="EUR",
    )
    db_session.add(site)
    await db_session.flush()
    await db_session.refresh(site)
    return site


@pytest_asyncio.fixture
async def sample_site_gbp(db_session: AsyncSession) -> Site:
    """Create a sample GBP site."""
    site = Site(
        name="London Office",
        country="United Kingdom",
        local_currency="GBP",
    )
    db_session.add(site)
    await db_session.flush()
    await db_session.refresh(site)
    return site


@pytest_asyncio.fixture
async def sample_local_cfo(db_session: AsyncSession, sample_site: Site) -> User:
    """Create a local CFO user assigned to sample_site."""
    user = User(
        email="localcfo@interfinops.test",
        hashed_password=hash_password("LocalCFO1!"),
        full_name="Test Local CFO",
        role=UserRole.local_cfo,
    )
    user.assigned_sites.append(sample_site)
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_income_statement(
    db_session: AsyncSession, sample_site: Site, sample_admin: User
) -> FinancialStatement:
    """Create a sample income statement with common line items."""
    statement = FinancialStatement(
        site_id=sample_site.id,
        statement_type=StatementType.income_statement,
        period_year=2025,
        period_month=12,
        currency="EUR",
        status=StatementStatus.approved,
        uploaded_by=sample_admin.id,
    )
    db_session.add(statement)
    await db_session.flush()

    line_items_data = [
        ("REVENUE", "Revenue", None, Decimal("1000000.00")),
        ("COGS", "Cost of Goods Sold", None, Decimal("600000.00")),
        ("GROSS_PROFIT", "Gross Profit", None, Decimal("400000.00")),
        ("OPERATING_EXPENSES", "Operating Expenses", None, Decimal("200000.00")),
        ("EBITDA", "EBITDA", None, Decimal("250000.00")),
        ("DEPRECIATION_AMORTIZATION", "Depreciation & Amortization", None, Decimal("50000.00")),
        ("EBIT", "EBIT", None, Decimal("200000.00")),
        ("INTEREST_EXPENSE", "Interest Expense", None, Decimal("20000.00")),
        ("TAX_EXPENSE", "Tax Expense", None, Decimal("45000.00")),
        ("NET_INCOME", "Net Income", None, Decimal("135000.00")),
    ]

    for code, name, parent, amount in line_items_data:
        item = FinancialLineItem(
            statement_id=statement.id,
            line_item_code=code,
            line_item_name=name,
            parent_code=parent,
            amount=amount,
        )
        db_session.add(item)

    await db_session.flush()
    await db_session.refresh(statement)
    return statement


@pytest_asyncio.fixture
async def sample_balance_sheet(
    db_session: AsyncSession, sample_site: Site, sample_admin: User
) -> FinancialStatement:
    """Create a sample balance sheet with common line items."""
    statement = FinancialStatement(
        site_id=sample_site.id,
        statement_type=StatementType.balance_sheet,
        period_year=2025,
        period_month=12,
        currency="EUR",
        status=StatementStatus.approved,
        uploaded_by=sample_admin.id,
    )
    db_session.add(statement)
    await db_session.flush()

    line_items_data = [
        ("CASH", "Cash and Equivalents", "CURRENT_ASSETS", Decimal("150000.00")),
        ("SHORT_TERM_INVESTMENTS", "Short-term Investments", "CURRENT_ASSETS", Decimal("50000.00")),
        ("ACCOUNTS_RECEIVABLE", "Accounts Receivable", "CURRENT_ASSETS", Decimal("200000.00")),
        ("INVENTORY", "Inventory", "CURRENT_ASSETS", Decimal("180000.00")),
        ("CURRENT_ASSETS", "Total Current Assets", None, Decimal("580000.00")),
        ("TOTAL_ASSETS", "Total Assets", None, Decimal("1500000.00")),
        ("ACCOUNTS_PAYABLE", "Accounts Payable", "CURRENT_LIABILITIES", Decimal("120000.00")),
        ("CURRENT_LIABILITIES", "Total Current Liabilities", None, Decimal("300000.00")),
        ("LONG_TERM_DEBT", "Long-term Debt", None, Decimal("400000.00")),
        ("SHORT_TERM_DEBT", "Short-term Debt", None, Decimal("100000.00")),
        ("TOTAL_LIABILITIES", "Total Liabilities", None, Decimal("800000.00")),
        ("TOTAL_EQUITY", "Total Equity", None, Decimal("700000.00")),
    ]

    for code, name, parent, amount in line_items_data:
        item = FinancialLineItem(
            statement_id=statement.id,
            line_item_code=code,
            line_item_name=name,
            parent_code=parent,
            amount=amount,
        )
        db_session.add(item)

    await db_session.flush()
    await db_session.refresh(statement)
    return statement
