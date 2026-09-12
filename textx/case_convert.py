"""Small, dependency-free helpers for converting human text to common cases."""

from __future__ import annotations

import re
from typing import Iterable


_ACRONYM_BOUNDARY = re.compile(r"([A-Z]+)([A-Z][a-z])")
_CAMEL_BOUNDARY = re.compile(r"([a-z\d])([A-Z])")
_NON_ALNUM = re.compile(r"[^\w]+", re.UNICODE)


def words(value: str | Iterable[str]) -> list[str]:
    """Split text into normalized words while preserving Unicode letters."""
    if not isinstance(value, str):
        value = " ".join(str(part) for part in value)
    value = _ACRONYM_BOUNDARY.sub(r"\1 \2", value)
    value = _CAMEL_BOUNDARY.sub(r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    value = _NON_ALNUM.sub(" ", value)
    return [part.casefold() for part in value.split() if part]


def to_snake_case(value: str | Iterable[str]) -> str:
    """Convert text to ``snake_case``."""
    return "_".join(words(value))


def to_kebab_case(value: str | Iterable[str]) -> str:
    """Convert text to ``kebab-case``."""
    return "-".join(words(value))


def to_camel_case(value: str | Iterable[str]) -> str:
    """Convert text to lower camel case."""
    parts = words(value)
    return (parts[0] if parts else "") + "".join(
        part.capitalize() for part in parts[1:]
    )


def to_pascal_case(value: str | Iterable[str]) -> str:
    """Convert text to upper camel case."""
    return "".join(part.capitalize() for part in words(value))


def to_constant_case(value: str | Iterable[str]) -> str:
    """Convert text to ``CONSTANT_CASE``."""
    return to_snake_case(value).upper()


def to_title_case(value: str | Iterable[str]) -> str:
    """Convert text to title case."""
    return " ".join(part.capitalize() for part in words(value))


def to_sentence_case(value: str | Iterable[str]) -> str:
    """Capitalize the first word and lowercase the remainder."""
    result = " ".join(words(value))
    return result[:1].upper() + result[1:] if result else result


def to_upper_case(value: str) -> str:
    """Return text in uppercase."""
    return value.upper()


def to_lower_case(value: str) -> str:
    """Return text in lowercase."""
    return value.lower()


# Aliases for those who perfer short names
snake_case = to_snake_case
kebab_case = to_kebab_case
camel_case = to_camel_case
pascal_case = to_pascal_case
constant_case = to_constant_case
title_case = to_title_case
sentence_case = to_sentence_case
camel_to_snake = to_snake_case
snake_to_camel = to_camel_case
pascal_to_snake = to_snake_case

