"""
Seed script: creates KPI target data for local development.

Usage:
    cd backend && source .venv/bin/activate
    PYTHONPATH=. python scripts/seed_targets.py
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, and_

from app.database import async_session_factory, engine
from app.models.target import KPITarget

# ---------------------------------------------------------------------------
# Fixed UUIDs (must match seed.py)
# ---------------------------------------------------------------------------
ADMIN_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
SITE_US_ID = uuid.UUID("00000000-0000-4000-8000-000000000010")
SITE_UK_ID = uuid.UUID("00000000-0000-4000-8000-000000000011")
SITE_DE_ID = uuid.UUID("00000000-0000-4000-8000-000000000012")

YEAR = 2025


# ---------------------------------------------------------------------------
# Target definitions
# ---------------------------------------------------------------------------
# Overall (consolidated) targets
OVERALL_TARGETS = [
    # (kpi_name, kpi_category, target_value)
    ("Revenue", "profitability", Decimal("6500000.0000")),
    ("Gross Margin", "profitability", Decimal("0.5500")),
    ("EBITDA Margin", "profitability", Decimal("0.2500")),
    ("Net Profit Margin", "profitability", Decimal("0.1500")),
    ("Current Ratio", "liquidity", Decimal("2.0000")),
    ("Debt-to-Equity", "leverage", Decimal("1.0000")),
]

# Per-site targets: US gets higher revenue, UK and DE proportional
SITE_TARGETS = {
    SITE_US_ID: [
        ("Revenue", "profitability", Decimal("3000000.0000")),
        ("Gross Margin", "profitability", Decimal("0.5800")),
        ("EBITDA Margin", "profitability", Decimal("0.2700")),
        ("Net Profit Margin", "profitability", Decimal("0.1700")),
        ("Current Ratio", "liquidity", Decimal("2.2000")),
        ("Debt-to-Equity", "leverage", Decimal("0.9000")),
    ],
    SITE_UK_ID: [
        ("Revenue", "profitability", Decimal("1800000.0000")),
        ("Gross Margin", "profitability", Decimal("0.5200")),
        ("EBITDA Margin", "profitability", Decimal("0.2300")),
        ("Net Profit Margin", "profitability", Decimal("0.1300")),
        ("Current Ratio", "liquidity", Decimal("1.9000")),
        ("Debt-to-Equity", "leverage", Decimal("1.1000")),
    ],
    SITE_DE_ID: [
        ("Revenue", "profitability", Decimal("1700000.0000")),
        ("Gross Margin", "profitability", Decimal("0.5400")),
        ("EBITDA Margin", "profitability", Decimal("0.2400")),
        ("Net Profit Margin", "profitability", Decimal("0.1400")),
        ("Current Ratio", "liquidity", Decimal("2.0000")),
        ("Debt-to-Equity", "leverage", Decimal("1.0000")),
    ],
}


async def upsert_target(
    session,
    site_id: uuid.UUID | None,
    kpi_name: str,
    kpi_category: str,
    target_value: Decimal,
) -> None:
    """Insert a target or update if it already exists."""
    filters = [
        KPITarget.kpi_name == kpi_name,
        KPITarget.period_year == YEAR,
        KPITarget.period_month.is_(None),
    ]
    if site_id is None:
        filters.append(KPITarget.site_id.is_(None))
    else:
        filters.append(KPITarget.site_id == site_id)

    result = await session.execute(select(KPITarget).where(and_(*filters)))
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.target_value = target_value
        existing.kpi_category = kpi_category
    else:
        session.add(
            KPITarget(
                site_id=site_id,
                kpi_name=kpi_name,
                kpi_category=kpi_category,
                target_value=target_value,
                period_year=YEAR,
                period_month=None,
                created_by=ADMIN_ID,
            )
        )


async def main() -> None:
    async with async_session_factory() as session:
        # Overall targets
        for kpi_name, kpi_category, target_value in OVERALL_TARGETS:
            await upsert_target(session, None, kpi_name, kpi_category, target_value)
        print(f"Seeded {len(OVERALL_TARGETS)} overall targets for {YEAR}")

        # Per-site targets
        for site_id, targets in SITE_TARGETS.items():
            for kpi_name, kpi_category, target_value in targets:
                await upsert_target(session, site_id, kpi_name, kpi_category, target_value)
            print(f"Seeded {len(targets)} targets for site {site_id}")

        await session.commit()
        print("Done.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
