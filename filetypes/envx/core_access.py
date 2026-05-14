import os
from pathlib import Path
from threading import Lock
from typing import Any


# ============================================================
# Internal module cache
# ============================================================

# Cache for parsed .env values.
# The file is only parsed once for performance reasons.
_ENV_CACHE: dict[str, str] | None = None

# Thread lock to ensure cache initialization is thread-safe.
_ENV_LOCK = Lock()


# ============================================================
# Exceptions
# ============================================================

class EnvNotFoundError(RuntimeError):
    """
    Raised when a required environment variable
    cannot be found.
    """
    pass


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


