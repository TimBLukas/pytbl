from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from . import core_access
from . import typed_access


# ============================================================
# Exceptions
# ============================================================

class EnvValidationError(ValueError):
    """
    Raised when environment configuration validation fails.

    This custom exception exists so callers can distinguish:
        - parse/type/constraint errors from environment configuration
        - generic runtime ``ValueError`` raised elsewhere

    In production systems this makes startup diagnostics easier
    to classify and route (for example, in health checks or boot logs).
    """


# ============================================================
# Internal helper functions
# ============================================================

def _parse_declared_type(
    key: str,
    raw_value: str,
    declared_type: str,
    sep: str,
) -> Any:
    """
    Parse a raw string value according to a schema ``type`` declaration.

    Supported types:
        - "str"
        - "int"
        - "float"
        - "bool"
        - "list"
        - "json"
        - "path"
        - "url"

    Design notes:
        - ``typed_access`` is reused for primitive parsing to ensure
          consistent behavior between direct typed reads and schema-based
          validation.
        - For URL/path types, dedicated validation is applied in this
          function so schema users get one coherent failure message.

    Args:
        key (str):
            Environment variable name being validated.

        raw_value (str):
            Raw value read from environment.

        declared_type (str):
            Target schema type.

        sep (str):
            List delimiter when ``declared_type == "list"``.

    Returns:
        Any:
            Parsed/coerced value.

    Raises:
        ValueError:
            If coercion fails or the declared type is unsupported.
    """

    if declared_type == "str":
        return raw_value

    if declared_type == "int":
        value = typed_access.get_int(key)
        assert value is not None
        return value

    if declared_type == "float":
        value = typed_access.get_float(key)
        assert value is not None
        return value

    if declared_type == "bool":
        value = typed_access.get_bool(key)
        assert value is not None
        return value

    if declared_type == "list":
        value = typed_access.get_list(key, sep=sep)
        return [] if value is None else value

    if declared_type == "json":
        return typed_access.get_json(key)

    if declared_type == "path":
        return Path(raw_value)

    if declared_type == "url":
        parsed = urlparse(raw_value)

        # Require an absolute URL with explicit scheme and authority.
        # This avoids accepting ambiguous values like "localhost:8000".
        if not (parsed.scheme and parsed.netloc):
            raise ValueError(
                f"Environment variable '{key}' is not a valid URL: {raw_value!r}"
            )

        return raw_value

    raise ValueError(f"Unsupported schema type for '{key}': {declared_type!r}")


# ============================================================
# Public API
# ============================================================

def require_one_of(keys: Sequence[str]) -> tuple[str, str]:
    """
    Require that at least one variable from a candidate list exists.

    Existence criteria:
        - Key resolves from environment sources
        - Value is not empty after ``strip()``

    The first matching key in input order is returned. This allows
    callers to provide fallback names while preserving deterministic
    preference order.

    Example:
        >>> require_one_of(["DATABASE_URL", "DB_URL", "POSTGRES_DSN"])
        ('DATABASE_URL', 'postgres://localhost/app')

    Args:
        keys (Sequence[str]):
            Ordered list of candidate variable names.

    Returns:
        tuple[str, str]:
            ``(matched_key, matched_value)``

    Raises:
        ValueError:
            If ``keys`` is empty.

        EnvValidationError:
            If none of the provided keys are set.
    """

    if not keys:
        raise ValueError("keys must not be empty")

    for key in keys:
        value = core_access.get(key)

        if value is None:
            continue

        normalized = str(value).strip()

        if normalized != "":
            return key, normalized

    joined = ", ".join(repr(key) for key in keys)
    raise EnvValidationError(
        f"At least one environment variable is required, but none were set: {joined}"
    )


def validate(schema: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """
    Validate environment variables against a declarative schema.

    Schema shape:
        {
            "PORT": {
                "required": True,
                "type": "int",
                "min": 1,
                "max": 65535
            },
            "APP_ENV": {
                "required": True,
                "choices": ["dev", "staging", "prod"]
            },
            "FEATURE_FLAGS": {
                "type": "list",
                "sep": ","
            }
        }

    Supported rule fields per variable:
        - required: bool (default False)
        - allow_empty: bool (default True)
        - type: str (default "str")
        - sep: str (default ",", only used for list parsing)
        - choices: sequence of allowed values
        - min / max: numeric bounds (for int/float values)
        - validator: callable receiving parsed value and returning bool

    Behavior:
        - Missing optional keys are skipped.
        - Present values are parsed/coerced according to ``type``.
        - All failures are aggregated and raised together to improve
          startup diagnostics for multi-variable configurations.

    Args:
        schema (Mapping[str, Mapping[str, Any]]):
            Validation rules keyed by environment variable name.

    Returns:
        dict[str, Any]:
            Validated and parsed values for keys that are present.

    Raises:
        TypeError:
            If a ``validator`` value is provided but is not callable.

        EnvValidationError:
            If one or more variables fail validation.
    """

    validated: dict[str, Any] = {}
    errors: list[str] = []

    for key, rules in schema.items():
        required = bool(rules.get("required", False))
        allow_empty = bool(rules.get("allow_empty", True))
        declared_type = str(rules.get("type", "str"))
        sep = str(rules.get("sep", ","))
        choices = rules.get("choices")
        minimum = rules.get("min")
        maximum = rules.get("max")
        validator_value = rules.get("validator")
        custom_validator: Callable[[Any], bool] | None = None

        if validator_value is not None:
            if not callable(validator_value):
                raise TypeError(f"validator for '{key}' must be callable")
            custom_validator = validator_value

        raw = core_access.get(key)

        if raw is None:
            if required:
                errors.append(f"Missing required environment variable: '{key}'")
            continue

        raw_str = str(raw).strip()

        if raw_str == "" and not allow_empty:
            errors.append(f"Environment variable '{key}' must not be empty")
            continue

        try:
            value = _parse_declared_type(
                key=key,
                raw_value=raw_str,
                declared_type=declared_type,
                sep=sep,
            )
        except ValueError as exc:
            errors.append(str(exc))
            continue

        if choices is not None and value not in choices:
            errors.append(
                f"Environment variable '{key}' has value {value!r}, "
                f"expected one of: {list(choices)!r}"
            )
            continue

        if minimum is not None and isinstance(value, (int, float)) and value < minimum:
            errors.append(
                f"Environment variable '{key}' must be >= {minimum}, got {value}"
            )
            continue

        if maximum is not None and isinstance(value, (int, float)) and value > maximum:
            errors.append(
                f"Environment variable '{key}' must be <= {maximum}, got {value}"
            )
            continue

        if custom_validator is not None and not custom_validator(value):
            errors.append(f"Environment variable '{key}' failed custom validation")
            continue

        validated[key] = value

    if errors:
        raise EnvValidationError("; ".join(errors))

    return validated


def is_valid_url(key: str) -> bool:
    """
    Check whether a variable exists and contains a valid absolute URL.

    A URL is considered valid when both:
        - scheme is present (e.g. "http", "https")
        - netloc is present (hostname[:port])

    Args:
        key (str):
            Environment variable name.

    Returns:
        bool:
            ``True`` if the value is a valid absolute URL, else ``False``.
    """

    value = core_access.get(key)

    if value is None:
        return False

    parsed = urlparse(str(value).strip())
    return bool(parsed.scheme and parsed.netloc)


def is_valid_path(key: str) -> bool:
    """
    Check whether a variable exists and resolves to an existing path.

    Args:
        key (str):
            Environment variable name.

    Returns:
        bool:
            ``True`` when the referenced path currently exists.
    """

    value = core_access.get(key)

    if value is None:
        return False

    return Path(str(value).strip()).exists()
