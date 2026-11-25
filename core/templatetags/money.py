"""Template tags for formatting UK pounds and cleaning related values."""

from decimal import Decimal, InvalidOperation

from django.template import Library

register = Library()

SYMBOLS = {"GBP": "£", "USD": "$", "EUR": "€"}


@register.simple_tag(takes_context=True)
def money(context, value):
    """Render an amount as e.g. £1,250.50."""
    code = context.get("currency", "GBP")
    symbol = SYMBOLS.get(code, "£")
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0.00")

    sign = "-" if amount < 0 else ""
    return f"{sign}{symbol}{abs(amount):,.2f}"


@register.filter
def money2(value):
    """Filter variant: format a value as pounds."""
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0.00")
    return f"{amount:,.2f}"


@register.filter
def hours(value):
    """Format hours with one decimal, e.g. 7.5."""
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0")
    return f"{amount:.1f}"
