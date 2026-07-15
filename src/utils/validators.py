"""Input validators used across models, services, and GUI forms."""

import re
from datetime import date


def validate_email(email: str) -> bool:
    """Return True if email matches a basic RFC-5322-like pattern.

    Args:
        email: The email string to test.

    Returns:
        True if valid, False otherwise.
    """
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip().lower()))


def validate_phone(phone: str) -> bool:
    """Return True if phone is empty or matches a valid international/national pattern.

    Args:
        phone: The phone number string to test.

    Returns:
        True if valid or empty, False otherwise.
    """
    val = phone.strip()
    if not val:
        return True
    return bool(re.match(r"^(\+?[\d\s\-().]{7,20})$", val))



def validate_positive_number(value) -> bool:
    """Return True if value can be converted to a non-negative float.

    Args:
        value: Value to check (string or numeric).

    Returns:
        True if float(value) >= 0, False otherwise.
    """
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def validate_date_string(date_str: str) -> bool:
    """Return True if date_str is a valid ISO 8601 date (YYYY-MM-DD).

    Args:
        date_str: The date string to validate.

    Returns:
        True if valid ISO date, False otherwise.
    """
    try:
        date.fromisoformat(date_str.strip())
        return True
    except (ValueError, AttributeError):
        return False


def validate_future_date(date_str: str) -> bool:
    """Return True if date_str is today or a future date.

    Args:
        date_str: The ISO 8601 date string to check.

    Returns:
        True if the date is >= today, False otherwise.
    """
    try:
        d = date.fromisoformat(date_str.strip())
        return d >= date.today()
    except (ValueError, AttributeError):
        return False


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Strip whitespace and truncate to max_length.

    Args:
        value: Input string.
        max_length: Maximum allowed length.

    Returns:
        Sanitised string.
    """
    return value.strip()[:max_length]


def format_currency(amount: float, symbol: str = "$") -> str:
    """Format a float as a currency string.

    Args:
        amount: Monetary value.
        symbol: Currency symbol prefix.

    Returns:
        Formatted string such as '$1,234.56'.
    """
    return f"{symbol}{amount:,.2f}"


def format_hours(hours: float) -> str:
    """Format hours as a readable string.

    Args:
        hours: Number of hours.

    Returns:
        String such as '3h 30m' or '0h 45m'.
    """
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m:02d}m"
