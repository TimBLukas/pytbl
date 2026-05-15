"""
ini_utils – utilities for reading, writing, and converting INI configuration files.

This package provides a high‑level interface for working with INI files,
including caching, atomic writes, dictionary conversion, flattening,
and export to JSON/YAML.

Public API:
    - read_ini() / read_ini_as_dict()
    - write_ini()
    - get_ini_value() / set_ini_value()
    - flatten_ini()
    - to_json() / to_yaml()
"""

from .core_functions import (
    # Core read/write
    read_ini,
    read_ini_as_dict,
    write_ini,
    # Value access
    get_ini_value,
    set_ini_value,
    # Transformation
    flatten_ini,
    # Conversion
    to_json,
    to_yaml,
)

__all__ = [
    "read_ini",
    "read_ini_as_dict",
    "write_ini",
    "get_ini_value",
    "set_ini_value",
    "flatten_ini",
    "to_json",
    "to_yaml",
]

__version__ = "0.0.1"
__author__ = "TBL"