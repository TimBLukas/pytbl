"""
logging_utils – flexible logging configuration and function call tracing.

This module provides:
        - A `get_logger` function with caching, file rotation, and console output.
        - `log_function_call` decorator for automatic entry/exit/exception logging.
        - Global default configuration management.
        - Support for both size‑based and time‑based log rotation.

Public API:
        - get_logger
        - reconfigure_logger
        - log_function_call
        - set_default_logging_config
        - get_logger_registry
        - clear_logger_registry
"""

from .logging_utils import (
        get_logger,
        reconfigure_logger,
        log_function_call,
        set_default_logging_config,
        get_logger_registry,
        clear_logger_registry,
)

__all__ = [
        "get_logger",
        "reconfigure_logger",
        "log_function_call",
        "set_default_logging_config",
        "get_logger_registry",
        "clear_logger_registry",
]

__version__ = "0.0.1"
__author__ = "TBL"