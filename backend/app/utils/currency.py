from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal("0")

# Currency display metadata
CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$",
    "EUR": "\u20ac",
    "GBP": "\u00a3",
    "JPY": "\u00a5",
    "CHF": "CHF",
    "CAD": "C$",
    "AUD": "A$",
    "SEK": "kr",
    "NOK": "kr",
    "DKK": "kr",
    "PLN": "z\u0142",
    "CZK": "K\u010d",
    "HUF": "Ft",
    "RON": "lei",
    "BGN": "\u043b\u0432.",
}

# Currencies that typically display without decimal places
ZERO_DECIMAL_CURRENCIES = {"JPY", "KRW", "VND"}


def convert_amount(amount: Decimal, fx_rate: Decimal) -> Decimal:
    """Convert a Decimal amount using a given FX rate.

    Result is rounded to 2 decimal places using banker's rounding.
    """
    return (amount * fx_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_currency(amount: Decimal, currency: str) -> str:
    """Format a Decimal amount for display with the appropriate currency symbol.

    Examples:
        format_currency(Decimal("1234567.89"), "USD") -> "$1,234,567.89"
        format_currency(Decimal("1000"), "JPY") -> "\\u00a51,000"
    """
    symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")

    if currency in ZERO_DECIMAL_CURRENCIES:
        formatted = f"{amount:,.0f}"
    else:
        formatted = f"{amount:,.2f}"

    return f"{symbol}{formatted}"


def round_financial(amount: Decimal, decimal_places: int = 2) -> Decimal:
    """Round a financial Decimal to the specified number of places using banker's rounding."""
    quantizer = Decimal(10) ** -decimal_places
    return amount.quantize(quantizer, rounding=ROUND_HALF_UP)


__all__ = [
    "convert_amount",
    "format_currency",
    "round_financial",
    "CURRENCY_SYMBOLS",
    "ZERO_DECIMAL_CURRENCIES",
]
