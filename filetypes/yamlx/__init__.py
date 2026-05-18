"""
yaml_utils – comprehensive YAML file handling and conversions.

This module provides:
    - Reading and writing YAML files with caching.
    - Merging two YAML files recursively.
    - Templating YAML with Jinja2.
    - Converting YAML to/from JSON, XML, and YAML (pretty‑print).

Public API:
    - read_yaml / write_yaml
    - merge_yaml
    - yaml_template
    - yaml_to_dict
    - to_json / to_yaml / to_xml
    - from_json / from_yaml / from_xml
"""

from .core_functions import (
    read_yaml,
    write_yaml,
    merge_yaml,
    yaml_template,
    yaml_to_dict,
    to_json,
    to_yaml,
    to_xml,
    from_json,
    from_yaml,
    from_xml,
)

__all__ = [
    "read_yaml",
    "write_yaml",
    "merge_yaml",
    "yaml_template",
    "yaml_to_dict",
    "to_json",
    "to_yaml",
    "to_xml",
    "from_json",
    "from_yaml",
    "from_xml",
]

__version__ = "0.0.1"
__author__ = "TBL"