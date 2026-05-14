import os
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager

from . import core_access


# ============================================================
# Constants
# ============================================================

# Default keywords used to identify sensitive environment variables.
# Matching is performed case-insensitively against the variable name.
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


# ============================================================
# Internal helper functions
# ============================================================

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


# ============================================================
# Public API
# ============================================================

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

    return core_access.as_dict(prefix=prefix)


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

    value = core_access.get(key)

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

    data = core_access.as_dict()

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
                core_access.unset(key_str)
            else:
                core_access.set(key_str, value)

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
