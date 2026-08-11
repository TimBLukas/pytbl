# ------------------------------------------
# Standard Library imports
# ------------------------------------------
import importlib.util
import os
import sys
import sysconfig
from pathlib import Path
from typing import Optional, Union, Dict, Any, Callable, Literal, overload
from functools import wraps

# ------------------------------------------
# Library specific imports
# ------------------------------------------
PathLike = str | Path


def _load_stdlib_logging():
        stdlib_dir = Path(sysconfig.get_paths()["stdlib"]) / "logging"
        original_logging = sys.modules.get("logging")

        logging_spec = importlib.util.spec_from_file_location(
                "_stdlib_logging",
                stdlib_dir / "__init__.py",
                submodule_search_locations=[str(stdlib_dir)],
        )
        assert logging_spec is not None and logging_spec.loader is not None
        stdlib_logging = importlib.util.module_from_spec(logging_spec)

        handlers_spec = importlib.util.spec_from_file_location(
                "_stdlib_logging.handlers",
                stdlib_dir / "handlers.py",
        )
        assert handlers_spec is not None and handlers_spec.loader is not None
        stdlib_handlers = importlib.util.module_from_spec(handlers_spec)

        try:
                sys.modules["logging"] = stdlib_logging
                logging_spec.loader.exec_module(stdlib_logging)
                handlers_spec.loader.exec_module(stdlib_handlers)
        finally:
                if original_logging is not None:
                        sys.modules["logging"] = original_logging
                else:
                        sys.modules.pop("logging", None)

        return stdlib_logging, stdlib_handlers


logging, _logging_handlers = _load_stdlib_logging()
RotatingFileHandler = _logging_handlers.RotatingFileHandler
TimedRotatingFileHandler = _logging_handlers.TimedRotatingFileHandler

# ------------------------------------------
# Type aliases
# ------------------------------------------
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LogLevelInt = int  # e.g., logging.DEBUG (10)

# ------------------------------------------
# Configuration defaults
# ------------------------------------------
_DEFAULT_LOG_LEVEL = logging.INFO
_DEFAULT_LOG_FORMAT = (
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
_DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
_DEFAULT_LOG_FILE: Optional[Path] = None  # No file logging by default
_DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_DEFAULT_BACKUP_COUNT = 5
_DEFAULT_CONSOLE_OUTPUT = True
_DEFAULT_ROTATION = 'size'  # 'size' or 'time'

# ------------------------------------------
# Global registry
# ------------------------------------------
_logger_registry: Dict[str, logging.Logger] = {}
_logger_configs: Dict[str, Dict[str, Any]] = {}

# ------------------------------------------
# Private Helper Functions
# ------------------------------------------
def _normalize_path(path: Optional[PathLike]) -> Optional[Path]:
        """
        Convert a PathLike object to a Path object (or None).

        Args:
                path: PathLike (str or Path) or None.

        Returns:
                Path or None.
        """
        if path is None:
                return None
        return Path(path) if isinstance(path, str) else path


def _validate_log_level(level: Union[LogLevel, LogLevelInt]) -> int:
        """
        Convert a string log level to its integer constant.

        Args:
                level: Either a string ('DEBUG', 'INFO', etc.) or an integer (10, 20, ...).

        Returns:
                Integer log level.

        Raises:
                ValueError: If the string level is unknown
        """
        if isinstance(level, int):
                return level
        level_upper = level.upper()
        if hasattr(logging, level_upper):
                return getattr(logging, level_upper)
        raise ValueError(f"Unknown log level: {level}")


def _ensure_log_dir(path: Path) -> None:
        """
        Create the parent directory for a log file if it does not exist

        Args:
                path: Path to the log file

        Raises:
                OSError: If directory creation fails
        """
        parent = path.parent
        if parent and not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)


def _create_file_handler(
        log_path: Path,
        max_bytes: int,
        backup_count: int,
        formatter: logging.Formatter,
        rotation: str = 'size'
) -> Optional[logging.Handler]:
        """
        Create a rotating file handler.

        Args:
                log_path: Path to the log file.
                max_bytes: Maximum file size in bytes (for size rotation).
                backup_count: Number of backup files to keep.
                formatter: Formatter for the handler.
                rotation: 'size' for RotatingFileHandler, 'time' for TimedRotatingFileHandler.

        Returns:
                Configured file handler, or None if creation fails.
        """
        try:
                _ensure_log_dir(log_path)
                if rotation == 'size':
                        handler = RotatingFileHandler(
                                log_path,
                                maxBytes=max_bytes,
                                backupCount=backup_count,
                                encoding='utf-8'
                        )
                elif rotation == 'time':
                        # Use daily rotation by default, keep backup_count days
                        handler = TimedRotatingFileHandler(
                                log_path,
                                when='midnight',
                                backupCount=backup_count,
                                encoding='utf-8'
                        )
                else:
                        raise ValueError(f"Unknown rotation type: {rotation}")
                
                handler.setFormatter(formatter)
                return handler
        except Exception as e:
                # Log to stderr (since logger may not be available)
                print(f"ERROR: Failed to create file handler for {log_path}: {e}", file=sys.stderr)
                return None


def _configure_logger_from_registry(name: str) -> logging.Logger:
        """
        Configure or reconfigure a logger based on stored config.

        Args:
                name: Logger name.

        Returns:
                Configured logger.
        """
        if name not in _logger_configs:
                # No config stored, return a basic logger
                return logging.getLogger(name)

        cfg = _logger_configs[name]
        level = cfg['level']
        log_file = cfg.get('log_file')
        console_output = cfg.get('console_output', True)
        log_format = cfg.get('log_format', _DEFAULT_LOG_FORMAT)
        date_format = cfg.get('date_format', _DEFAULT_DATE_FORMAT)
        max_bytes = cfg.get('max_bytes', _DEFAULT_MAX_BYTES)
        backup_count = cfg.get('backup_count', _DEFAULT_BACKUP_COUNT)
        rotation = cfg.get('rotation', 'size')

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        # Clear existing handlers to avoid duplication
        if logger.hasHandlers():
                logger.handlers.clear()

        formatter = logging.Formatter(log_format, datefmt=date_format)

        # Console handler
        if console_output:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

        # File handler
        if log_file:
                log_path = _normalize_path(log_file)
                if log_path:
                        file_handler = _create_file_handler(
                                log_path, max_bytes, backup_count, formatter, rotation
                        )
                if file_handler:
                        logger.addHandler(file_handler)

        return logger


# ------------------------------------------
# Public Facing API
# ------------------------------------------
def get_logger(
        name: str = 'pytbl',
        level: Union[LogLevel, LogLevelInt, None] = None,
        log_file: Optional[PathLike] = None,
        console_output: Optional[bool] = None,
        log_format: Optional[str] = None,
        date_format: Optional[str] = None,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None,
        rotation: Optional[Literal['size', 'time']] = None
) -> logging.Logger:
        """
        Configure and return a logger instance.

        The logger is cached by name. Subsequent calls with the same name will
        return the existing logger, but you can reconfigure it by calling again
        with different parameters (the configuration will be updated).

        Args:
                name: Name of the logger (usually module name).
                level: Logging level (e.g., 'DEBUG', 'INFO', or logging.DEBUG).
                log_file: Path to a log file. If None, file logging is disabled.
                console_output: Whether to log to the console (stderr).
                log_format: Format string for log messages.
                date_format: Format string for timestamps.
                max_bytes: Maximum size of a log file before rotation (bytes, for 'size' rotation).
                backup_count: Number of old log files to keep.
                rotation: Rotation strategy – 'size' (size-based) or 'time' (daily midnight).

        Returns:
                Configured logger instance.

        Example:
                >>> logger = get_logger('myapp', level='DEBUG', log_file='logs/app.log')
                >>> logger.info('Application started')
        """
        level_int = _validate_log_level(_DEFAULT_LOG_LEVEL if level is None else level)

        log_path = _normalize_path(_DEFAULT_LOG_FILE if log_file is None else log_file)
        console_output = _DEFAULT_CONSOLE_OUTPUT if console_output is None else console_output
        log_format = _DEFAULT_LOG_FORMAT if log_format is None else log_format
        date_format = _DEFAULT_DATE_FORMAT if date_format is None else date_format
        max_bytes = _DEFAULT_MAX_BYTES if max_bytes is None else max_bytes
        backup_count = _DEFAULT_BACKUP_COUNT if backup_count is None else backup_count
        rotation = _DEFAULT_ROTATION if rotation is None else rotation

        _logger_configs[name] = {
                'level': level_int,
                'log_file': log_path,
                'console_output': console_output,
                'log_format': log_format,
                'date_format': date_format,
                'max_bytes': max_bytes,
                'backup_count': backup_count,
                'rotation': rotation,
        }

        logger = _configure_logger_from_registry(name)
        _logger_registry[name] = logger
        return logger


def reconfigure_logger(
        name: str,
        **kwargs
) -> logging.Logger:
        """
        Reconfigure an existing logger with new settings.

        Any keyword argument accepted by `get_logger` can be used.
        If the logger does not exist, it will be created.

        Args:
                name: Logger name.
                **kwargs: Configuration overrides (level, log_file, etc.).

        Returns:
                The reconfigured logger.

        Example:
                >>> logger = reconfigure_logger('myapp', level='ERROR', console_output=False)
        """
        current = _logger_configs.get(name, {})
        new_config = {
                'level': current.get('level', _DEFAULT_LOG_LEVEL),
                'log_file': current.get('log_file', _DEFAULT_LOG_FILE),
                'console_output': current.get('console_output', _DEFAULT_CONSOLE_OUTPUT),
                'log_format': current.get('log_format', _DEFAULT_LOG_FORMAT),
                'date_format': current.get('date_format', _DEFAULT_DATE_FORMAT),
                'max_bytes': current.get('max_bytes', _DEFAULT_MAX_BYTES),
                'backup_count': current.get('backup_count', _DEFAULT_BACKUP_COUNT),
                'rotation': current.get('rotation', _DEFAULT_ROTATION),
        }

        new_config.update(kwargs)
        return get_logger(name, **new_config)


def get_logger_registry() -> Dict[str, logging.Logger]:
        """
        Return a copy of the internal logger registry.

        Returns:
                Dictionary mapping logger names to logger instances.
        """
        return _logger_registry.copy()


def clear_logger_registry() -> None:
        """
        Clear all cached loggers and their configurations.
        Useful for testing or resetting the library state.
        """
        _logger_registry.clear()
        _logger_configs.clear()


# ------------------------------------------
# Decorator for function call logging
# ------------------------------------------
def log_function_call(
        logger: Optional[Union[logging.Logger, str]] = None,
        level: Union[LogLevel, LogLevelInt] = 'DEBUG',
        log_args: bool = True,
        log_result: bool = True,
        log_exceptions: bool = True
) -> Callable:
        """
        Decorator to log function entry, exit, and exceptions.

        Args:
                logger: Either a logger instance, a logger name (str), or None.
                        If None, uses a logger named after the function's module.
                level: Log level for entry/exit messages.
                log_args: If True, log function arguments.
                log_result: If True, log return value.
                log_exceptions: If True, log exceptions with traceback.

        Returns:
                Decorator function.

        Example:
                >>> @log_function_call(level='INFO')
                ... def add(a, b):
                ...     return a + b
                >>> add(3, 5)
                DEBUG: Entering add(3, 5)
                DEBUG: Exiting add - Returned: 8
        """
        def decorator(func: Callable) -> Callable:
                @wraps(func)
                def wrapper(*args, **kwargs):
                        # Determine logger
                        if logger is None:
                                log = logging.getLogger(func.__module__)
                        elif isinstance(logger, str):
                                log = get_logger(logger)
                        else:
                                log = logger

                        level_int = _validate_log_level(level)

                        arg_str = ''
                        if log_args:
                                args_repr = [repr(a) for a in args]
                                kwargs_repr = [f'{k}={repr(v)}' for k, v in kwargs.items()]
                                arg_str = ', '.join(args_repr + kwargs_repr)
                                if arg_str:
                                        arg_str = f'({arg_str})'

                        log.log(level_int, f"Entering {func.__name__}{arg_str}")

                        try:
                                result = func(*args, **kwargs)
                                if log_result:
                                        log.log(level_int, f"Exiting {func.__name__} - Returned: {repr(result)}")
                                return result
                        except Exception as e:
                                if log_exceptions:
                                        log.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                                raise

                return wrapper
        return decorator


# ------------------------------------------
# Global defaults configuration
# ------------------------------------------
def set_default_logging_config(
        level: Union[LogLevel, LogLevelInt] = _DEFAULT_LOG_LEVEL,
        log_format: str = _DEFAULT_LOG_FORMAT,
        date_format: str = _DEFAULT_DATE_FORMAT,
        console_output: bool = _DEFAULT_CONSOLE_OUTPUT,
        max_bytes: int = _DEFAULT_MAX_BYTES,
        backup_count: int = _DEFAULT_BACKUP_COUNT,
        rotation: Literal['size', 'time'] = 'size'
) -> None:
        """
        Set global default configuration for all loggers created after this call.

        Existing loggers are not affected.

        Args:
                level: Default log level.
                log_format: Default format string.
                date_format: Default date format.
                console_output: Default console output flag.
                max_bytes: Default max bytes for size rotation.
                backup_count: Default backup count.
                rotation: Default rotation type.
        """
        global _DEFAULT_LOG_LEVEL, _DEFAULT_LOG_FORMAT, _DEFAULT_DATE_FORMAT
        global _DEFAULT_CONSOLE_OUTPUT, _DEFAULT_MAX_BYTES, _DEFAULT_BACKUP_COUNT, _DEFAULT_ROTATION

        _DEFAULT_LOG_LEVEL = _validate_log_level(level)
        _DEFAULT_LOG_FORMAT = log_format
        _DEFAULT_DATE_FORMAT = date_format
        _DEFAULT_CONSOLE_OUTPUT = console_output
        _DEFAULT_MAX_BYTES = max_bytes
        _DEFAULT_BACKUP_COUNT = backup_count
        _DEFAULT_ROTATION = rotation


# Internal default config dict for merging
_DEFAULT_CONFIG = {
        'level': _DEFAULT_LOG_LEVEL,
        'log_file': _DEFAULT_LOG_FILE,
        'console_output': _DEFAULT_CONSOLE_OUTPUT,
        'log_format': _DEFAULT_LOG_FORMAT,
        'date_format': _DEFAULT_DATE_FORMAT,
        'max_bytes': _DEFAULT_MAX_BYTES,
        'backup_count': _DEFAULT_BACKUP_COUNT,
        'rotation': _DEFAULT_ROTATION,
}