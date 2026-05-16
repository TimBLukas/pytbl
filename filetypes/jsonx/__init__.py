"""
json_utils – comprehensive JSON file handling and conversions.

This module provides:
    - Read, write, append, delete, validate, minify, prettify JSON.
    - Conversion between JSON and CSV, XML, YAML.
    - Caching, atomic writes, dot‑notation access for nested deletions.

Public API:
    - read_json / write_json / append_json / delete_json
    - validate_json / minify_json / prettify_json
    - json_to_csv / csv_to_json
    - json_to_xml / xml_to_json
    - json_to_yaml / yaml_to_json
"""

from .core_functions import (
    read_json,
    write_json,
    append_json,
    delete_json,
    validate_json,
    minify_json,
    prettify_json,
    json_to_csv,
    csv_to_json,
    json_to_xml,
    xml_to_json,
    json_to_yaml,
    yaml_to_json,
)

__all__ = [
    "read_json",
    "write_json",
    "append_json",
    "delete_json",
    "validate_json",
    "minify_json",
    "prettify_json",
    "json_to_csv",
    "csv_to_json",
    "json_to_xml",
    "xml_to_json",
    "json_to_yaml",
    "yaml_to_json",
]

__version__ = "0.0.1"
__author__ = "TBL"