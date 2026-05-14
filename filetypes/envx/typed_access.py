import json
from typing import Any

from . import core_access


# ============================================================
# Constants
# ============================================================

# Canonical truthy/falsy tokens used when parsing booleans.
# Matching is case-insensitive after whitespace trimming.
_TRUTHY_VALUES = {"1", "true", "t", "yes", "y", "on"}
_FALSY_VALUES = {"0", "false", "f", "no", "n", "off"}


# ============================================================
# Internal helper functions
# ============================================================

def _read_optional_raw(key: str) -> str | None:
    """
    Read an environment variable value as a raw string.

    Unlike ``core_access.require``, this helper does not raise
    when the variable is missing; it simply returns ``None``.
    """

    value = core_access.get(key)

    if value is None:
        return None

    return str(value).strip()


# ============================================================
# Public API
# ============================================================

def get_int(key: str, default: int | None = None) -> int | None:
    """
    Read and parse an environment variable as an integer.

    Example:
        >>> get_int("PORT", 8000)
        8000

    Args:
        key (str):
            Environment variable name.

        default (int | None):
            Value returned when ``key`` does not exist.

    Returns:
        int | None:
            Parsed integer value, or default for missing keys.

    Raises:
        ValueError:
            If a value exists but cannot be parsed as ``int``.
    """

    raw = _read_optional_raw(key)

    if raw is None:
        return default

    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{key}' cannot be parsed as int: {raw!r}"
        ) from exc


def get_float(key: str, default: float | None = None) -> float | None:
    """
    Read and parse an environment variable as a float.

    Args:
        key (str):
            Environment variable name.

        default (float | None):
            Value returned when ``key`` does not exist.

    Returns:
        float | None:
            Parsed float value, or default for missing keys.

    Raises:
        ValueError:
            If a value exists but cannot be parsed as ``float``.
    """

    raw = _read_optional_raw(key)

    if raw is None:
        return default

    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{key}' cannot be parsed as float: {raw!r}"
        ) from exc


def get_bool(key: str, default: bool | None = None) -> bool | None:
    """
    Read and parse an environment variable as a boolean.

    Accepted truthy values:
        1, true, t, yes, y, on

    Accepted falsy values:
        0, false, f, no, n, off

    Args:
        key (str):
            Environment variable name.

        default (bool | None):
            Value returned when ``key`` does not exist.

    Returns:
        bool | None:
            Parsed boolean value, or default for missing keys.

    Raises:
        ValueError:
            If a value exists but is not a supported boolean token.
    """

    raw = _read_optional_raw(key)

    if raw is None:
        return default

    lowered = raw.lower()

    if lowered in _TRUTHY_VALUES:
        return True

    if lowered in _FALSY_VALUES:
        return False

    raise ValueError(
        f"Environment variable '{key}' cannot be parsed as bool: {raw!r}"
    )


def get_list(key: str, sep: str = ",", default: list[str] | None = None) -> list[str] | None:
    """
    Read and parse an environment variable as a delimited string list.

    Behavior:
        - Missing key -> returns ``default``
        - Empty value -> returns ``[]``
        - Non-empty -> split by ``sep``, trim each item, drop empty items

    Args:
        key (str):
            Environment variable name.

        sep (str):
            Delimiter used to split list values.

        default (list[str] | None):
            Value returned when ``key`` does not exist.

    Returns:
        list[str] | None:
            Parsed list, or default for missing keys.

    Raises:
        ValueError:
            If ``sep`` is empty.
    """

    if sep == "":
        raise ValueError("sep must not be empty")

    raw = _read_optional_raw(key)

    if raw is None:
        return default

    if raw == "":
        return []

    items = [item.strip() for item in raw.split(sep)]
    return [item for item in items if item != ""]


def get_json(key: str, default: Any | None = None) -> Any:
    """
    Read and parse an environment variable as JSON.

    Args:
        key (str):
            Environment variable name.

        default (Any | None):
            Value returned when ``key`` does not exist.

    Returns:
        Any:
            Deserialized JSON value, or default for missing keys.

    Raises:
        ValueError:
            If a value exists but is not valid JSON.
    """

    raw = _read_optional_raw(key)

    if raw is None:
        return default

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Environment variable '{key}' cannot be parsed as JSON: {raw!r}"
        ) from exc
