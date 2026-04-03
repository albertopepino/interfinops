from __future__ import annotations

import io
from decimal import Decimal, InvalidOperation

import pandas as pd
from fastapi import UploadFile

from app.schemas.financial import LineItemUpload

# Expected columns in upload templates
REQUIRED_COLUMNS = {"line_item_code", "line_item_name", "amount"}
OPTIONAL_COLUMNS = {"parent_code"}

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class UploadValidationError(Exception):
    """Raised when an uploaded file fails validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"Upload validation failed: {'; '.join(errors)}")


async def parse_upload_file(file: UploadFile) -> list[LineItemUpload]:
    """Parse an Excel (.xlsx) or CSV upload file into validated line items.

    Validates:
    - File type (xlsx or csv)
    - File size
    - Required columns exist
    - Each row has valid data (non-empty codes/names, valid Decimal amounts)

    Returns a list of validated LineItemUpload objects.
    Raises UploadValidationError on any validation failure.
    """
    errors: list[str] = []

    # Validate content type
    content_type = file.content_type or ""
    filename = file.filename or ""
    is_csv = filename.lower().endswith(".csv") or content_type == "text/csv"
    is_excel = filename.lower().endswith(".xlsx") or content_type in ALLOWED_CONTENT_TYPES - {"text/csv"}

    if not (is_csv or is_excel):
        raise UploadValidationError([f"Unsupported file type: {content_type}. Use .xlsx or .csv"])

    # Read file content
    content = await file.read()

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise UploadValidationError([f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB"])

    if len(content) == 0:
        raise UploadValidationError(["File is empty"])

    # Parse into DataFrame
    try:
        if is_csv:
            df = pd.read_csv(io.BytesIO(content), dtype=str)
        else:
            df = pd.read_excel(io.BytesIO(content), dtype=str, engine="openpyxl")
    except Exception as exc:
        raise UploadValidationError([f"Failed to parse file: {exc}"])

    # Normalize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Check required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise UploadValidationError(
            [f"Missing required columns: {', '.join(sorted(missing_columns))}"]
        )

    # Validate rows
    line_items: list[LineItemUpload] = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed + header row

        code = str(row.get("line_item_code", "")).strip()
        name = str(row.get("line_item_name", "")).strip()
        amount_str = str(row.get("amount", "")).strip()
        parent_code_raw = row.get("parent_code")
        parent_code = str(parent_code_raw).strip() if pd.notna(parent_code_raw) and str(parent_code_raw).strip() else None

        if not code:
            errors.append(f"Row {row_num}: line_item_code is empty")
            continue
        if not name:
            errors.append(f"Row {row_num}: line_item_name is empty")
            continue

        try:
            amount = Decimal(amount_str.replace(",", ""))
        except (InvalidOperation, ValueError):
            errors.append(f"Row {row_num}: invalid amount '{amount_str}'")
            continue

        line_items.append(
            LineItemUpload(
                line_item_code=code,
                line_item_name=name,
                parent_code=parent_code,
                amount=amount,
            )
        )

    if errors:
        raise UploadValidationError(errors)

    if not line_items:
        raise UploadValidationError(["No valid line items found in file"])

    return line_items


__all__ = ["parse_upload_file", "UploadValidationError"]
