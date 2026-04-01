"""Common.

Objects which could be useful in the construction of multiple connectors.
"""
# ruff: noqa: DOC201

import enum
from collections.abc import Callable

NAME_REGEX: str = r"^[a-zA-Z0-9\-\_\s\/\.:]+$"


class Operator(str, enum.Enum):
    """The operator to use to compare the reduced evaluation value to a given target threshold."""

    MORE_THAN = ">"
    LESS_THAN = "<"
    MORE_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUAL = "=="


OPERATORS: dict[str, Callable[[int | float, int | float], bool]] = {
    ">": lambda x, y: x > y,
    "<": lambda x, y: x < y,
    ">=": lambda x, y: x >= y,
    "<=": lambda x, y: x <= y,
    "==": lambda x, y: x == y,
}
