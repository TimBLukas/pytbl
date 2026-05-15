"""
datatypes – a collection of reusable type aliases for my personal Python library.

This package provides semantic type hints for common patterns:
paths, JSON data, callables, time, networking, configuration, logging, async, and more.

All types are re‑exported from the `helpers` module for convenient importing:

    from datatypes import PathLike, JsonObject, Predicate, ...

For a complete list, see `__all__` below or the `helpers` module docstring.
"""

from datatypes.helpers import *

# Explicitly list all public members (optional but good for linters and docs)
__all__ = [
    # Path & File
    "PathLike",
    "FilePath",
    "FileDescriptor",
    "ReadableFile",
    "WritableFile",
    "OpenTextMode",
    "OpenBinaryMode",

    # JSON & Data
    "JsonPrimitive",
    "JsonValue",
    "JsonObject",
    "StrDict",
    "IntDict",
    "Pair",
    "Triple",

    # Numeric & Bytes
    "IntOrFloat",
    "Number",
    "BytesLike",
    "StringLike",

    # Callables
    "UnaryFunc",
    "Predicate",
    "KeyFunc",
    "Supplier",
    "Consumer",
    "Mapper",
    "Reducer",
    "Transformer",

    # Time & Date
    "DatetimeLike",
    "DateLike",
    "TimeDeltaLike",
    "TimeZoneLike",

    # Network & URL
    "Host",
    "Port",
    "Address",
    "URL",
    "PathSegments",
    "QueryParam",
    "Headers",

    # Config & Env
    "EnvVar",
    "EnvValue",
    "EnvDict",
    "ConfigPath",
    "ConfigData",

    # Logging
    "LoggerLike",
    "LogLevel",
    "ExtraData",

    # Async
    "AsyncFunc",
    "CoroutineLike",
    "SyncOrAsync",

    # Optional & Lazy
    "Missing",
    "OptionalDefault",
    "Lazy",
]

__version__ = "0.0.1"
__author__ = "TBL"
