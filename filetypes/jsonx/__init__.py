"""
json_utils
~~~~~~~~~~

Utilities for reading, writing, transforming, and converting JSON files.

package provides a interface for working with JSON files,
including caching, atomic writes, nested key access, minification,
prettification, and conversion to/from CSV, XML, and YAML.

Reading & Writing
-----------------
- :func:`read_json`    – parse a JSON file (cached by modification time)
- :func:`write_json`   – write JSON-serializable data to disk (atomic)
- :func:`append_json`  – append an item to a JSON array file
- :func:`delete_json`  – delete a key or element by dot-notation path

Validation & Formatting
-----------------------
- :func:`validate_json`  – check whether a file or string contains valid JSON
- :func:`minify_json`    – strip all optional whitespace from JSON
- :func:`prettify_json`  – reformat JSON with indentation for readability

Conversion
----------
- :func:`json_to_csv`   – convert a JSON array to a CSV file
- :func:`csv_to_json`   – convert a CSV file to a JSON array
- :func:`json_to_xml`   – convert a JSON file to XML
- :func:`xml_to_json`   – convert an XML file to JSON
- :func:`json_to_yaml`  – convert a JSON file to YAML (requires ``pyyaml``)
- :func:`yaml_to_json`  – convert a YAML file to JSON (requires ``pyyaml``)

Optional dependency:
    PyYAML (``pyyaml``) is required for :func:`json_to_yaml` and
    :func:`yaml_to_json`. All other functions work without it.
    Availability can be checked via ``YAML_AVAILABLE``.
"""

from .json_core_functions import (
    # Reading & Writing
    read_json,
    write_json,
    append_json,
    delete_json,
    # Validation & Formatting
    validate_json,
    minify_json,
    prettify_json,
    # Conversion
    json_to_csv,
    csv_to_json,
    json_to_xml,
    xml_to_json,
    json_to_yaml,
    yaml_to_json,
    # Availability flag (useful for optional-dependency feature checks)
    YAML_AVAILABLE,
)

__all__ = [
    # Reading & Writing
    "read_json",
    "write_json",
    "append_json",
    "delete_json",
    # Validation & Formatting
    "validate_json",
    "minify_json",
    "prettify_json",
    # Conversion
    "json_to_csv",
    "csv_to_json",
    "json_to_xml",
    "xml_to_json",
    "json_to_yaml",
    "yaml_to_json",
    # Availability flag
    "YAML_AVAILABLE",
]

__version__ = "0.0.1"
__author__ = "TBL"
