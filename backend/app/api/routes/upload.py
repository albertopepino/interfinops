from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select

from app.api.deps import AuditLogger, CurrentUser, DbSession, require_site_access
from app.models.financial_data import (
    FinancialLineItem,
    FinancialStatement,
    StatementStatus,
    StatementType,
)
from app.models.site import Site
from app.schemas.financial import FinancialStatementResponse, FinancialStatementUpload
from app.services.upload import UploadValidationError, parse_upload_file

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/upload", tags=["upload"])


async def _create_statement_from_upload(
    db: DbSession,
    current_user: CurrentUser,
    site_id: uuid.UUID,
    statement_type: StatementType,
    period_year: int,
    period_month: int,
    file: UploadFile,
    audit_log: AuditLogger,
) -> FinancialStatementResponse:
    """Shared logic: parse file, create statement + line items."""
    # Verify site exists
    result = await db.execute(select(Site).where(Site.id == site_id, Site.is_active == True))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    # Verify site access
    await require_site_access(site_id, current_user)

    # Parse the uploaded file
    try:
        line_items = await parse_upload_file(file)
    except UploadValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "File validation failed", "errors": exc.errors},
        )

    # Create financial statement
    statement = FinancialStatement(
        site_id=site_id,
        statement_type=statement_type,
        period_year=period_year,
        period_month=period_month,
        currency=site.local_currency,
        status=StatementStatus.draft,
        uploaded_by=current_user.id,
    )
    db.add(statement)
    await db.flush()

    # Create line items
    for item in line_items:
        db_item = FinancialLineItem(
            statement_id=statement.id,
            line_item_code=item.line_item_code,
            line_item_name=item.line_item_name,
            parent_code=item.parent_code,
            amount=item.amount,
        )
        db.add(db_item)

    await db.flush()
    await db.refresh(statement)

    await audit_log(
        "upload",
        "financial_statement",
        str(statement.id),
        site_id=site_id,
        details={
            "statement_type": statement_type.value,
            "period": f"{period_year}-{period_month:02d}",
            "line_items_count": len(line_items),
            "filename": file.filename,
        },
    )

    return FinancialStatementResponse.model_validate(statement)


@router.post("/income-statement", response_model=FinancialStatementResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_income_statement(
    request: Request,
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    file: UploadFile,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> FinancialStatementResponse:
    """Upload an income statement from an Excel or CSV file."""
    return await _create_statement_from_upload(
        db, current_user, site_id, StatementType.income_statement,
        period_year, period_month, file, audit_log,
    )


@router.post("/balance-sheet", response_model=FinancialStatementResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_balance_sheet(
    request: Request,
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    file: UploadFile,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> FinancialStatementResponse:
    """Upload a balance sheet from an Excel or CSV file."""
    return await _create_statement_from_upload(
        db, current_user, site_id, StatementType.balance_sheet,
        period_year, period_month, file, audit_log,
    )


@router.post("/cash-flow", response_model=FinancialStatementResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_cash_flow(
    request: Request,
    site_id: uuid.UUID,
    period_year: int,
    period_month: int,
    file: UploadFile,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> FinancialStatementResponse:
    """Upload a cash flow statement from an Excel or CSV file."""
    return await _create_statement_from_upload(
        db, current_user, site_id, StatementType.cash_flow,
        period_year, period_month, file, audit_log,
    )


@router.post("/manual", response_model=FinancialStatementResponse, status_code=status.HTTP_201_CREATED)
async def upload_manual(
    body: FinancialStatementUpload,
    db: DbSession,
    current_user: CurrentUser,
    audit_log: AuditLogger,
) -> FinancialStatementResponse:
    """Upload financial data via JSON body (manual entry)."""
    result = await db.execute(select(Site).where(Site.id == body.site_id, Site.is_active == True))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    await require_site_access(body.site_id, current_user)

    statement = FinancialStatement(
        site_id=body.site_id,
        statement_type=body.statement_type,
        period_year=body.period_year,
        period_month=body.period_month,
        currency=body.currency,
        status=StatementStatus.draft,
        uploaded_by=current_user.id,
    )
    db.add(statement)
    await db.flush()

    for item in body.line_items:
        db_item = FinancialLineItem(
            statement_id=statement.id,
            line_item_code=item.line_item_code,
            line_item_name=item.line_item_name,
            parent_code=item.parent_code,
            amount=item.amount,
        )
        db.add(db_item)

    await db.flush()
    await db.refresh(statement)

    await audit_log(
        "upload_manual",
        "financial_statement",
        str(statement.id),
        site_id=body.site_id,
        details={
            "statement_type": body.statement_type.value,
            "period": f"{body.period_year}-{body.period_month:02d}",
            "line_items_count": len(body.line_items),
        },
    )

    return FinancialStatementResponse.model_validate(statement)


__all__ = ["router"]
