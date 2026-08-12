"""
envx
~~~

A environment variable module with .env support,
typed accessors, validation, and redaction.

Core Access
-----------
- :func:`get`             – read a variable, return a default if missing
- :func:`require`         – read a required variable, raise if missing
- :func:`require_one_of`  – require at least one from a list of candidates
- :func:`exists`          – check whether a variable is present
- :func:`get_prefix`      – return all variables matching a key prefix
- :func:`as_dict`         – return all variables as a plain dict

Typed Accessors
---------------
- :func:`get_int`         – parse value as ``int``
- :func:`get_float`       – parse value as ``float``
- :func:`get_bool`        – parse value as ``bool``
- :func:`get_list`        – parse value as a delimited list
- :func:`get_json`        – parse value as JSON

Mutation
--------
- :func:`set`             – set a variable in the current process
- :func:`unset`           – remove a variable from the current process

Persistence
-----------
- :func:`save_env`        – write current environment to a .env file
- :func:`reload_env`      – force re-read of the .env cache

Merging & Snapshots
-------------------
- :func:`merge_sources`   – merge dotenv / env / secrets / cli with precedence
- :func:`snapshot`        – capture a copy of the current process environment
- :func:`restore`         – restore a previously captured snapshot
- :func:`temporary`       – context manager for scoped environment overrides

Validation
----------
- :func:`validate`        – validate variables against a declarative schema
- :func:`is_valid_url`    – check whether a variable holds a valid absolute URL
- :func:`is_valid_path`   – check whether a variable holds an existing path

Redaction
---------
- :func:`mask`            – return a safe display value for a single variable
- :func:`redacted_dict`   – return all variables with sensitive values masked
- :func:`is_secret`       – heuristically detect sensitive keys

Exceptions
----------
- :exc:`EnvNotFoundError`    – raised when a required variable is missing
- :exc:`EnvValidationError`  – raised when schema validation fails

Constants
---------
- :data:`DEFAULT_SECRET_KEYWORDS` – keywords used by :func:`is_secret`
"""

from .envx_core_functions import (
    # Core access
    get,
    require,
    require_one_of,
    exists,
    get_prefix,
    as_dict,
    # Typed accessors
    get_int,
    get_float,
    get_bool,
    get_list,
    get_json,
    # Mutation
    set,
    unset,
    # Persistence
    save_env,
    reload_env,
    # Merging & snapshots
    merge_sources,
    snapshot,
    restore,
    temporary,
    # Validation
    validate,
    is_valid_url,
    is_valid_path,
    # Redaction
    mask,
    redacted_dict,
    is_secret,
    # Exceptions
    EnvNotFoundError,
    EnvValidationError,
    # Constants
    DEFAULT_SECRET_KEYWORDS,
)

__all__ = [
    # Core access
    "get",
    "require",
    "require_one_of",
    "exists",
    "get_prefix",
    "as_dict",
    # Typed accessors
    "get_int",
    "get_float",
    "get_bool",
    "get_list",
    "get_json",
    # Mutation
    "set",
    "unset",
    # Persistence
    "save_env",
    "reload_env",
    # Merging & snapshots
    "merge_sources",
    "snapshot",
    "restore",
    "temporary",
    # Validation
    "validate",
    "is_valid_url",
    "is_valid_path",
    # Redaction
    "mask",
    "redacted_dict",
    "is_secret",
    # Exceptions
    "EnvNotFoundError",
    "EnvValidationError",
    # Constants
    "DEFAULT_SECRET_KEYWORDS",
]
