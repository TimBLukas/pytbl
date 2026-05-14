"""
High-level environment access package.

This package provides four layers:
    1. ``core_access``: raw/get/set/require/cache primitives
    2. ``typed_access``: typed parsing helpers (int/float/bool/list/json)
    3. ``validation``: schema and utility-based validation
    4. ``helpers``: operational helpers (redaction, snapshots, overrides)
"""

from .core_access import (
    EnvNotFoundError,
    as_dict,
    exists,
    get,
    reload_env,
    require,
    save_env,
    set,
    unset,
)
from .helpers import (
    get_prefix,
    is_secret,
    mask,
    merge_sources,
    redacted_dict,
    restore,
    snapshot,
    temporary,
)
from .typed_access import get_bool, get_float, get_int, get_json, get_list
from .validation import EnvValidationError, is_valid_path, is_valid_url, require_one_of, validate

__all__ = [
    "EnvNotFoundError",
    "EnvValidationError",
    "as_dict",
    "exists",
    "get",
    "get_bool",
    "get_float",
    "get_int",
    "get_json",
    "get_list",
    "get_prefix",
    "is_secret",
    "is_valid_path",
    "is_valid_url",
    "mask",
    "merge_sources",
    "redacted_dict",
    "reload_env",
    "require",
    "require_one_of",
    "restore",
    "save_env",
    "set",
    "snapshot",
    "temporary",
    "unset",
    "validate",
]
