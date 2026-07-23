"""
testing – extended test utilities for unittest.

This package provides a `BaseTestCase` class with additional assertions,
patching helpers, temporary file management, and other testing utilities.

Public API:
    - BaseTestCase
    - time_limit
    - retry
    - skip_if
    - skip_unless
    - repeat
    - require_module
    - require_env
    - flaky
    - timeout
"""

from .base import BaseTestCase
from .decorators import (
    time_limit,
    retry,
    skip_if,
    skip_unless,
    repeat,
    require_module,
    require_env,
    flaky,
    timeout,
)

__all__ = [
    "BaseTestCase",
    "time_limit",
    "retry",
    "skip_if",
    "skip_unless",
    "repeat",
    "require_module",
    "require_env",
    "flaky",
    "timeout",
]

__version__ = "0.0.1"
__author__ = "tbl"
