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
        logging as _stdlib_logging,
        get_logger,
        reconfigure_logger,
        log_function_call,
        set_default_logging_config,
        get_logger_registry,
        clear_logger_registry,
)

getLogger = get_logger
basicConfig = _stdlib_logging.basicConfig
DEBUG = _stdlib_logging.DEBUG
INFO = _stdlib_logging.INFO
WARNING = _stdlib_logging.WARNING
ERROR = _stdlib_logging.ERROR
CRITICAL = _stdlib_logging.CRITICAL
NOTSET = _stdlib_logging.NOTSET
Logger = _stdlib_logging.Logger
Handler = _stdlib_logging.Handler
Formatter = _stdlib_logging.Formatter
StreamHandler = _stdlib_logging.StreamHandler
FileHandler = _stdlib_logging.FileHandler
NullHandler = _stdlib_logging.NullHandler

__all__ = [
        "get_logger",
        "reconfigure_logger",
        "log_function_call",
        "set_default_logging_config",
        "get_logger_registry",
        "clear_logger_registry",
        "getLogger",
        "basicConfig",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "NOTSET",
        "Logger",
        "Handler",
        "Formatter",
        "StreamHandler",
        "FileHandler",
        "NullHandler",
]

__version__ = "0.0.1"
__author__ = "TBL"