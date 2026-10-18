"""Utility functions for timestamping, input validation, and arithmetic calculations."""

from datetime import datetime, timezone
import math
from typing import Any


def get_utc_timestamp() -> str:
    """Return the current UTC timestamp formatted in ISO 8601 with Z indicator."""
    return datetime.now(timezone.utc).isoformat()


def validate_operand(value: Any, field_name: str) -> tuple[float | None, str | None]:
    """Validate that an operand is numeric and not a boolean.

    Returns:
        tuple[float | None, str | None]: (parsed_value, error_message)
    """
    if isinstance(value, bool):
        return None, f"Operand '{field_name}' cannot be a boolean value."

    if value is None:
        return None, f"Operand '{field_name}' cannot be null."

    if isinstance(value, (int, float)):
        if math.isnan(value) or math.isinf(value):
            return None, f"Operand '{field_name}' must be a finite number."
        return float(value), None

    if isinstance(value, str):
        try:
            parsed = float(value.strip())
            if math.isnan(parsed) or math.isinf(parsed):
                return None, f"Operand '{field_name}' must be a finite number."
            return parsed, None
        except ValueError:
            return None, f"Operand '{field_name}' must be a valid number."

    return None, f"Operand '{field_name}' must be numeric, got {type(value).__name__}."


def calculate(operation: str, num1: float, num2: float) -> tuple[float | int | None, str | None]:
    """Perform arithmetic operation safely.

    Returns:
        tuple[float | int | None, str | None]: (result, error_message)
    """
    op = operation.strip().lower()

    if op in ("add", "+", "addition"):
        res = num1 + num2
    elif op in ("subtract", "-", "subtraction"):
        res = num1 - num2
    elif op in ("multiply", "*", "multiplication"):
        res = num1 * num2
    elif op in ("divide", "/", "division"):
        if num2 == 0:
            return None, "Division by zero is not allowed."
        res = num1 / num2
    else:
        return (
            None,
            f"Unsupported operation '{operation}'. Supported operations: add, subtract, multiply, divide.",
        )

    # Return integer if the number has no fractional component
    if isinstance(res, float) and res.is_integer():
        return int(res), None

    return round(res, 6), None
