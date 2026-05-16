import os
import json
from pathlib import Path
from threading import Lock
from typing import Any
from collections.abc import Iterator, Mapping, Sequence, Callable
from contextlib import contextmanager
from urllib.parse import urlparse


# ============================================================
# Internal module cache
# ============================================================

# Cache for parsed .env values.
# The file is only parsed once for performance reasons.
_ENV_CACHE: dict[str, str] | None = None

# Thread lock to ensure cache initialization is thread-safe.
_ENV_LOCK = Lock()

# ============================================================
# Constants
# ============================================================

DEFAULT_SECRET_KEYWORDS: tuple[str, ...] = (
    "secret",
    "token",
    "password",
    "passwd",
    "api_key",
    "private_key",
    "access_key",
    "auth",
    "credential",
)
_TRUTHY_VALUES = {"1", "true", "t", "yes", "y", "on"}
_FALSY_VALUES = {"0", "false", "f", "no", "n", "off"}

# ============================================================
# Exceptions
# ============================================================

class EnvNotFoundError(RuntimeError):
    """
    Raised when a required environment variable
    cannot be found.
    """
    
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

def _load_dotenv(path: str = ".env") -> dict[str, str]:
    """
    Parse a .env file into a dictionary.

    This function reads the provided .env file line-by-line
    and extracts key-value pairs in the form:

        KEY=value

    Empty lines and comments are ignored.

    Supported formats:
        DATABASE_URL=localhost
        DEBUG=true
        API_KEY="secret"

    Notes:
        - Quotes surrounding values are removed.
        - Malformed lines are skipped silently.
        - Values are returned exactly as strings.

    Args:
        path (str):
            Path to the .env file.

    Returns:
        dict[str, str]:
            Dictionary containing parsed environment variables.
    """

    dotenv = Path(path)

    if not dotenv.is_file():
        return {}

    data: dict[str, str] = {}

    for line in dotenv.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        key, sep, value = line.partition("=")

        if not sep:
            continue

        key = key.strip()
        value = value.strip().strip('"').strip("'")

        data[key] = value

    return data


def _ensure_cache_loaded() -> None:
    """
    Initialize the internal .env cache if necessary.

    The cache is loaded lazily on first access to avoid
    unnecessary file operations during startup.

    Thread safety:
        Uses a lock to prevent race conditions in
        multi-threaded applications.
    """

    global _ENV_CACHE

    if _ENV_CACHE is None:

        with _ENV_LOCK:

            # Double-check pattern for thread safety
            if _ENV_CACHE is None:
                _ENV_CACHE = _load_dotenv()


def _load_env_value(name: str) -> str:
    """
    Load a single environment variable.

    Lookup order:
        1. Current process environment (`os.environ`)
        2. Cached `.env` values

    If a value is loaded from `.env`,
    it is automatically inserted into `os.environ`
    for faster future access.

    Args:
        name (str):
            Name of the environment variable.

    Returns:
        str:
            The resolved environment variable value.

    Raises:
        EnvNotFoundError:
            If the variable cannot be found.
    """

    value = os.getenv(name)

    if value is not None:
        return value.strip()

    _ensure_cache_loaded()

    assert _ENV_CACHE is not None

    if name in _ENV_CACHE:

        value = _ENV_CACHE[name]

        os.environ.setdefault(name, value)

        return value

    raise EnvNotFoundError(
        f"Missing required environment variable: '{name}'"
    )


def _mask_value(value: str, visible_chars: int = 2) -> str:
    """
    Redact a sensitive value while keeping a small visible boundary.

    This is useful when debugging configuration output while still
    preventing accidental credential leaks in logs or diagnostics.

    Masking behavior:
        - Empty values remain empty.
        - Very short values are fully masked.
        - Longer values preserve a prefix/suffix and hide the middle.

    Example:
        >>> _mask_value("super-secret-token")
        'su**************en'

    Args:
        value (str):
            Raw value to redact.

        visible_chars (int):
            Number of characters to preserve at both the beginning
            and the end of the string.

    Returns:
        str:
            Redacted value.
    """

    if visible_chars < 0:
        raise ValueError("visible_chars must be >= 0")

    if not value:
        return ""

    boundary = visible_chars * 2

    if len(value) <= boundary:
        return "*" * len(value)

    middle_mask = "*" * (len(value) - boundary)
    return f"{value[:visible_chars]}{middle_mask}{value[-visible_chars:]}"


def _read_optional_raw(key: str) -> str | None:
    """
    Read an environment variable value as a raw string.

    Unlike ``core_access.require``, this helper does not raise
    when the variable is missing; it simply returns ``None``.
    """

    value = get(key)

    if value is None:
        return None

    return str(value).strip()


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
        value = get_int(key)
        assert value is not None
        return value

    if declared_type == "float":
        value = get_float(key)
        assert value is not None
        return value

    if declared_type == "bool":
        value = get_bool(key)
        assert value is not None
        return value

    if declared_type == "list":
        value = get_list(key, sep=sep)
        return [] if value is None else value

    if declared_type == "json":
        return get_json(key)

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

def get(key: str, default: Any | None = None) -> Any:
    """
    Retrieve an environment variable.

    This function attempts to load the variable from:
        1. `os.environ`
        2. `.env` cache

    If the variable cannot be found,
    the provided default value is returned.

    Example:
        >>> get("PORT", 8000)
        '8000'

        >>> get("UNKNOWN", "fallback")
        'fallback'

    Args:
        key (str):
            Name of the environment variable.

        default (Any | None):
            Value returned if the variable
            does not exist.

    Returns:
        Any:
            The resolved environment value
            or the provided default.
    """

    try:
        return _load_env_value(key)

    except EnvNotFoundError:
        return default


def get_prefix(prefix: str) -> dict[str, str]:
    """
    Return environment variables filtered by key prefix.

    This function delegates to ``core_access.as_dict`` so it uses
    the same source composition rules as the core module:
        1. Parsed `.env` values (cached)
        2. Process values from ``os.environ`` (take precedence)

    Example:
        >>> get_prefix("DB_")
        {'DB_HOST': 'localhost', 'DB_PORT': '5432'}

    Args:
        prefix (str):
            Prefix used to filter variable names.

    Returns:
        dict[str, str]:
            Prefix-matched key/value pairs.
    """

    return as_dict(prefix=prefix)


def require(key: str) -> str:
    """
    Retrieve a required environment variable.

    Unlike `get()`, this function raises an exception
    if the variable cannot be found.

    Example:
        >>> require("DATABASE_URL")
        'postgres://localhost'

    Args:
        key (str):
            Name of the required variable.

    Returns:
        str:
            Environment variable value.

    Raises:
        EnvNotFoundError:
            If the variable is missing.
    """

    return _load_env_value(key)


def set(key: str, value: Any) -> None:
    """
    Set an environment variable for the current process.

    Values are automatically converted to strings
    because environment variables are always stored
    as strings internally.

    Example:
        >>> set("DEBUG", True)

    Args:
        key (str):
            Variable name.

        value (Any):
            Value to assign.
    """

    os.environ[key] = str(value)


def unset(key: str) -> None:
    """
    Remove an environment variable from the current process.

    If the variable does not exist,
    the function silently succeeds.

    Example:
        >>> unset("DEBUG")

    Args:
        key (str):
            Variable name to remove.
    """
    os.environ.pop(key, None)


def exists(key: str) -> bool:
    """
    Check whether an environment variable exists.

    This checks both:
        - `os.environ`
        - cached `.env` values

    Example:
        >>> exists("PORT")
        True

    Args:
        key (str):
            Variable name.

    Returns:
        bool:
            True if the variable exists,
            otherwise False.
    """

    try:
        _load_env_value(key)
        return True

    except EnvNotFoundError:
        return False


def as_dict(prefix: str | None = None) -> dict[str, str]:
    """
    Return environment variables as a dictionary.

    This function combines:
        - variables from `os.environ`
        - variables loaded from the cached `.env`

    Variables from `os.environ` take precedence over `.env`
    values if the same key exists in both places.

    Optionally, variables can be filtered by prefix.

    Example:
        >>> as_dict()
        {
            "PORT": "8000",
            "DEBUG": "true"
        }

        >>> as_dict(prefix="DB_")
        {
            "DB_HOST": "localhost",
            "DB_PORT": "5432"
        }

    Args:
        prefix (str | None):
            Optional prefix filter.

    Returns:
        dict[str, str]:
            Dictionary containing environment variables.
    """

    _ensure_cache_loaded()

    assert _ENV_CACHE is not None

    data = dict(_ENV_CACHE)

    data.update(os.environ)

    if prefix is not None:
        data = {
            key: value
            for key, value in data.items()
            if key.startswith(prefix)
        }

    return data


def save_env(path: str = ".env") -> None:
    """
    Save current environment variables to a .env file.

    This writes all currently available environment variables
    into the specified file using:

        KEY=value

    Existing files are overwritten.

    Notes:
        - Values containing spaces are automatically quoted.
        - Variables are sorted alphabetically for readability.

    Example:
        >>> save_env()

    Args:
        path (str):
            Destination path for the .env file.
    """

    data = as_dict()

    lines: list[str] = []

    for key in sorted(data.keys()):

        value = str(data[key])

        # Quote values containing spaces
        if " " in value:
            value = f'"{value}"'

        lines.append(f"{key}={value}")

    Path(path).write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def reload_env(path: str = ".env") -> None:
    """
    Reload the internal .env cache.

    This forces the library to:
        1. Clear the existing cache
        2. Re-read the .env file
        3. Refresh cached values

    Useful when:
        - the .env file changes during runtime
        - tests modify environment configuration

    Example:
        >>> reload_env()

    Args:
        path (str):
            Path to the .env file.
    """

    global _ENV_CACHE

    with _ENV_LOCK:
        _ENV_CACHE = _load_dotenv(path)


def merge_sources(
    env: Mapping[str, object] | None = None,
    dotenv: Mapping[str, object] | None = None,
    secrets: Mapping[str, object] | None = None,
    cli: Mapping[str, object] | None = None,
) -> dict[str, str]:
    """
    Merge multiple configuration sources with deterministic precedence.

    Precedence (lowest -> highest):
        1. dotenv
        2. env
        3. secrets
        4. cli

    This ordering reflects common production behavior:
        - `.env` files provide local defaults
        - real environment variables override file defaults
        - secret stores override generic environment values
        - runtime CLI flags are highest-priority overrides

    Notes:
        - ``None`` sources are ignored.
        - Keys and values are normalized to strings.
        - Entries with value ``None`` are skipped.

    Args:
        env (Mapping[str, object] | None):
            Variables typically read from process environment.

        dotenv (Mapping[str, object] | None):
            Variables read from a `.env` file.

        secrets (Mapping[str, object] | None):
            Variables loaded from a secret backend.

        cli (Mapping[str, object] | None):
            Variables provided via command-line arguments.

    Returns:
        dict[str, str]:
            Final merged configuration map.
    """

    result: dict[str, str] = {}

    for source in (dotenv, env, secrets, cli):
        if source is None:
            continue

        for key, value in source.items():
            if value is None:
                continue
            result[str(key)] = str(value)

    return result


def is_secret(key: str, key_words: Sequence[str] | None = None) -> bool:
    """
    Heuristically detect whether a key likely contains sensitive data.

    Detection uses simple keyword matching against the variable name.
    This intentionally favors practical behavior over strict schemas,
    making it useful for diagnostics and redaction utilities.

    Example:
        >>> is_secret("DATABASE_PASSWORD")
        True

        >>> is_secret("PORT")
        False

    Args:
        key (str):
            Environment variable name.

        key_words (Sequence[str] | None):
            Optional custom keywords. If not provided, defaults to
            ``DEFAULT_SECRET_KEYWORDS``.

    Returns:
        bool:
            ``True`` if the key appears sensitive, else ``False``.
    """

    terms = tuple(key_words) if key_words is not None else DEFAULT_SECRET_KEYWORDS
    key_lower = key.lower()
    return any(term.lower() in key_lower for term in terms)


def mask(key: str) -> str:
    """
    Return a safe display value for an environment variable.

    Behavior:
        - Missing variables return an empty string.
        - Non-sensitive variables return the original value.
        - Sensitive variables are redacted with ``_mask_value``.

    This function is designed for logging/diagnostic output and avoids
    exposing secrets while still preserving enough context to identify
    configuration state.

    Args:
        key (str):
            Environment variable name.

    Returns:
        str:
            Original or masked value, depending on sensitivity.
    """

    value = get(key)

    if value is None:
        return ""

    value_str = str(value)

    if not is_secret(key):
        return value_str

    return _mask_value(value_str)


def redacted_dict() -> dict[str, str]:
    """
    Return all available variables with sensitive keys redacted.

    This produces a dictionary suitable for safe logging where
    potentially sensitive values are masked but non-sensitive values
    remain readable.

    Returns:
        dict[str, str]:
            Full variable map with selective value redaction.
    """

    data = as_dict()

    return {
        key: (_mask_value(value) if is_secret(key) else value)
        for key, value in data.items()
    }


@contextmanager
def temporary(overrides: Mapping[str, object]) -> Iterator[None]:
    """
    Temporarily apply environment overrides inside a context block.

    This context manager snapshots the current process environment,
    applies overrides, yields control, and restores the snapshot even
    when an exception is raised.

    Rules:
        - ``value is None``: variable is unset for the block.
        - other values: variable is set as ``str(value)``.

    Example:
        >>> with temporary({"DEBUG": "1", "TOKEN": None}):
        ...     ...

    Args:
        overrides (Mapping[str, object]):
            Temporary key/value assignments.
    """

    previous_state = snapshot()

    try:
        for key, value in overrides.items():
            key_str = str(key)
            if value is None:
                unset(key_str)
            else:
                set(key_str, value)

        yield

    finally:
        restore(previous_state)


def snapshot() -> dict[str, str]:
    """
    Capture the current process environment.

    This snapshot can be passed to ``restore`` to return the process
    environment to exactly the same key/value state.

    Returns:
        dict[str, str]:
            Copy of ``os.environ``.
    """

    return dict(os.environ)


def restore(snapshot: Mapping[str, str]) -> None:
    """
    Restore a previously captured environment snapshot.

    This operation fully replaces the current process environment with
    the provided snapshot:
        1. Clears all existing keys.
        2. Re-populates keys from ``snapshot``.

    Args:
        snapshot (Mapping[str, str]):
            Environment state returned by ``snapshot()``.
    """

    os.environ.clear()
    os.environ.update({str(key): str(value) for key, value in snapshot.items()})


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
        value = get(key)

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

        raw = get(key)

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

    value = get(key)

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

    value = get(key)

    if value is None:
        return False

    return Path(str(value).strip()).exists()
