from __future__ import annotations

from typing import (
    Union, Literal, Callable, Awaitable, Coroutine, Any, IO, 
    TYPE_CHECKING
)
from pathlib import Path
from os import PathLike as OsPathLike  # Renamed to avoid conflict
from asyncio import Future, Task
from datetime import datetime, date, time, timedelta, tzinfo
from logging import Logger

# ----------------------------------------------------------------------
# Path & File Helpers
# ----------------------------------------------------------------------

type PathLike = Path | str
"""
Type alias for a filesystem path.

Can be either:
    - a :class:`pathlib.Path` object, or
    - a :class:`str` containing the filesystem path.

Functions that accept a `PathLike` will need to convert strings
and correctly handle both possibilities.

Note: You could also accept `os.PathLike` for even broader compatibility.
"""

type FilePath = Path | str
"""
Alias for a file path – same as `PathLike`. Kept for semantic clarity
when a function strictly expects a *file* (not a directory).
"""

type FileDescriptor = int
"""
A Unix file descriptor (as returned by `os.open()`).

Use this to indicate that a function works with low-level OS file handles.
"""

type ReadableFile = FilePath | IO[bytes] | IO[str] | bytes | str
"""
Anything that can be read as a byte stream or text.

Includes:
    - a filesystem path (`FilePath`)
    - an open binary or text file object (`IO[bytes]` or `IO[str]`)
    - raw bytes or a string (treated as the entire content)

Useful for functions like `read_file()` that accept many input forms.
"""

type WritableFile = FilePath | IO[bytes] | IO[str]
"""
Anything that can be written to as a byte or text stream.

Includes:
    - a filesystem path (`FilePath` – file will be opened for writing)
    - an open binary or text file object (`IO[bytes]` or `IO[str]`)
"""

type OpenTextMode = Literal['r', 'w', 'a', 'x', 'r+', 'w+', 'a+', 'x+']
"""
Valid text‑mode strings for `open()` (e.g., `'r'`, `'w'`, `'a'`, etc.).
"""

type OpenBinaryMode = Literal['rb', 'wb', 'ab', 'xb', 'rb+', 'wb+', 'ab+', 'xb+']
"""
Valid binary‑mode strings for `open()` (e.g., `'rb'`, `'wb'`, etc.).
"""

# ----------------------------------------------------------------------
# JSON & Data Structures
# ----------------------------------------------------------------------

type JsonPrimitive = str | int | float | bool | None
"""
Primitive types allowed in JSON: strings, numbers, booleans, and null.
"""

type JsonValue = JsonPrimitive | list[JsonValue] | dict[str, JsonValue]
"""
Any valid JSON value: primitive, array, or object (recursive).
"""

type JsonObject = dict[str, JsonValue]
"""
A JSON object – dictionary with string keys and JSON‑valid values.
"""

type StrDict = dict[str, Any]
"""
Generic dictionary with string keys and arbitrary values.
Useful for configuration or attribute bags.
"""

type IntDict[T] = dict[int, T]
"""
Dictionary with integer keys and values of type `T`.
"""

type Pair[T, U] = tuple[T, U]
"""
Generic 2‑element tuple (pair). More readable than `tuple[T, U]`.
"""

type Triple[T, U, V] = tuple[T, U, V]
"""
Generic 3‑element tuple (triple).
"""

# ----------------------------------------------------------------------
# Numeric & Byte Helpers
# ----------------------------------------------------------------------

type IntOrFloat = int | float
"""
A value that can be either an integer or a float.
"""

type Number = int | float | complex
"""
Any numeric type in Python: `int`, `float`, or `complex`.
"""

type BytesLike = bytes | bytearray | memoryview
"""
Any object that represents a sequence of bytes (read‑only or mutable).
"""

type StringLike = str | bytes
"""
Either a text string (`str`) or a byte string (interpreted as UTF‑8).
"""

# ----------------------------------------------------------------------
# Callable & Functional Helpers
# ----------------------------------------------------------------------

type UnaryFunc[T, R] = Callable[[T], R]
"""
A function that takes one argument of type `T` and returns `R`.
"""

type Predicate[T] = Callable[[T], bool]
"""
A function that tests a condition on `T` and returns a boolean.
"""

type KeyFunc[T] = Callable[[T], Any]
"""
A function that extracts a sort/group key from `T`.
"""

type Supplier[T] = Callable[[], T]
"""
A function that takes no arguments and produces a value of type `T`.
"""

type Consumer[T] = Callable[[T], None]
"""
A function that consumes a value of type `T` and returns nothing.
"""

type Mapper[T, R] = Callable[[T], R]
"""
Synonym for `UnaryFunc[T, R]` – transforms `T` into `R`.
"""

type Reducer[T, R] = Callable[[R, T], R]
"""
A reduction function: accumulates a result of type `R` with each `T`.
"""

type Transformer[T] = Callable[[T], T]
"""
A function that transforms a value of type `T` to another value of the same type.
"""

# ----------------------------------------------------------------------
# Time & Date Helpers
# ----------------------------------------------------------------------

type DatetimeLike = datetime | str | int | float
"""
Something that represents a point in time.

Accepts:
    - a `datetime` object,
    - an ISO‑format string (e.g., `"2025-01-15T12:00:00"`),
    - a Unix timestamp as `int` or `float` (seconds since epoch).
"""

type DateLike = date | str | datetime
"""
Something that represents a calendar date.

Accepts:
    - a `date` object,
    - a `datetime` object (date part extracted),
    - an ISO‑format string (e.g., `"2025-01-15"`).
"""

type TimeDeltaLike = timedelta | int | float
"""
Something that represents a duration.

Accepts:
    - a `timedelta` object,
    - seconds as an `int` or `float`.
"""

type TimeZoneLike = tzinfo | str
"""
Something that represents a time zone.

Accepts:
    - a `tzinfo` object (e.g., `timezone.utc`),
    - a string like `"UTC"`, `"Europe/Berlin"`.
"""

# ----------------------------------------------------------------------
# Network & URL Helpers
# ----------------------------------------------------------------------

type Host = str
"""
A hostname or IP address (e.g., `"localhost"`, `"192.168.1.1"`).
"""

type Port = int
"""
A TCP/UDP port number (1‑65535).
"""

type Address = tuple[str, Port]
"""
A network address as `(host, port)`.
"""

type URL = str
"""
A Uniform Resource Locator string (e.g., `"https://example.com/path"`).
"""

type PathSegments = list[str]
"""
A list of URL path segments (split on `'/'`).
Example: `["api", "v2", "users"]`
"""

type QueryParam = tuple[str, str] | tuple[str, str | list[str] | None]
"""
A single HTTP query parameter.

Can be a simple `(key, value)` pair, or a more complex one where the value
is a string, a list of strings (multiple values), or `None`.
"""

type Headers = dict[str, str] | list[tuple[str, str]]
"""
HTTP headers as either a dictionary or a list of key‑value pairs.
"""

# ----------------------------------------------------------------------
# Configuration & Environment
# ----------------------------------------------------------------------

type EnvVar = str
"""
The name of an environment variable.
"""

type EnvValue = str | int | bool | float | None
"""
The value of an environment variable (string, number, boolean, or null).
"""

type EnvDict = dict[EnvVar, EnvValue]
"""
A dictionary mapping environment variable names to their values.
"""

type ConfigPath = Path | str | None
"""
A path to a configuration file.

- If a `Path` or `str`, that specific file is used.
- If `None`, a default location (e.g., `~/.config/mylib/config.json`) is used.
"""

type ConfigData = JsonObject | str
"""
Configuration data either as a parsed JSON object (`dict`) or a JSON string.
"""

# ----------------------------------------------------------------------
# Logging Helpers
# ----------------------------------------------------------------------

type LoggerLike = Logger | str
"""
Something that identifies a logger.

Accepts:
    - a `logging.Logger` instance,
    - a string name (which will be used to get or create a logger).
"""

type LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] | int
"""
A log level as either a string constant or its integer value.
"""

type ExtraData = dict[str, Any] | None
"""
Extra data to attach to a log record, or `None` for none.
"""

# ----------------------------------------------------------------------
# Async & Concurrency Helpers
# ----------------------------------------------------------------------

type AsyncFunc[T] = Callable[..., Awaitable[T]]
"""
An asynchronous function (coroutine) that returns `Awaitable[T]`.
"""

type CoroutineLike[T] = Coroutine[Any, Any, T] | Future[T] | Task[T]
"""
Anything that can be awaited to produce a value of type `T`.

Includes:
    - a coroutine object,
    - a `Future`,
    - a `Task`.
"""

type SyncOrAsync[T] = T | Awaitable[T]
"""
A value that may be either a plain `T` or an awaitable that yields `T`.

Useful for functions that accept both synchronous and asynchronous callbacks.
"""

# ----------------------------------------------------------------------
# Optional & Default Helpers
# ----------------------------------------------------------------------

type Missing = Literal["__MISSING__"]
"""
A sentinel value indicating that a parameter was *not* provided.

Used to distinguish between `None` (allowed value) and "no argument given".
Example:
    def func(value: T | Missing = __MISSING__):
        if value is __MISSING__:
            ...  # not provided
"""

type OptionalDefault[T] = T | Missing
"""
A value that is either of type `T` or the `Missing` sentinel.
"""

type Lazy[T] = T | Callable[[], T]
"""
A lazy value: either a concrete `T` or a zero‑argument callable that produces `T`.

The callable is evaluated only when needed (lazy initialisation).
"""
