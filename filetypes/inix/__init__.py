"""
ini_utils
~~~~~~~~~

Utilities for reading, writing, and converting INI configuration files.

package provides a high-level interface for interacting with INI files:
- caching, atomic writes, dictionary conversion, flattening, and export to JSON/YAML.

Reading
-------
- :func:`read_ini`         – parse an INI file into a ``ConfigParser`` object (cached)
- :func:`read_ini_as_dict` – parse an INI file directly into a nested ``dict``

Writing
-------
- :func:`write_ini`        – write a dict back to an INI file on disk

Value Access
------------
- :func:`get_ini_value`    – read a single key from a section (with optional fallback)
- :func:`set_ini_value`    – update a single key in a section and persist to disk

Transformation
--------------
- :func:`flatten_ini`      – collapse ``{section: {key: value}}`` into ``section.key`` pairs

Conversion
----------
- :func:`to_json`          – serialize an INI file's contents to a JSON string or file
- :func:`to_yaml`          – serialize an INI file's contents to a YAML string or file
                             (requires ``pyyaml``)

Optional dependency:
    PyYAML (``pyyaml``) is required for :func:`to_yaml`.
    All other functions work without it.
    Availability can be checked via ``YAML_AVAILABLE``.
"""

from .ini_core_functions import (
    # Reading
    read_ini,
    read_ini_as_dict,
    # Writing
    write_ini,
    # Value access
    get_ini_value,
    set_ini_value,
    # Transformation
    flatten_ini,
    # Conversion
    to_json,
    to_yaml,
    # Availability flag (useful for optional-dependency feature checks)
    YAML_AVAILABLE,
)

__all__ = [
    # Reading
    "read_ini",
    "read_ini_as_dict",
    # Writing
    "write_ini",
    # Value access
    "get_ini_value",
    "set_ini_value",
    # Transformation
    "flatten_ini",
    # Conversion
    "to_json",
    "to_yaml",
    # Availability flag
    "YAML_AVAILABLE",
]

__version__ = "0.0.1"
__author__ = "TBL"
