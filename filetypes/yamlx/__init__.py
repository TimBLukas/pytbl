"""
yaml_utils
~~~~~~~~~~

Utilities for reading, writing, merging, templating, and converting YAML files.

package provides a high-level interface for working with YAML files,
including caching, atomic writes, deep merging, Jinja2 templating,
and conversion to/from JSON and XML.

Reading & Writing
-----------------
- :func:`read_yaml`   – parse a YAML file (cached by modification time)
- :func:`write_yaml`  – write YAML-serializable data to disk (atomic)
- :func:`yaml_to_dict` – read a YAML file and enforce a ``dict`` root

Merging & Templating
--------------------
- :func:`merge_yaml`     – deep-merge two YAML files (override wins on conflicts)
- :func:`yaml_template`  – render a YAML file as a Jinja2 template
                           (requires ``jinja2``)

Conversion — to YAML
---------------------
- :func:`from_json`  – convert a JSON file to YAML
- :func:`from_xml`   – convert an XML file to YAML
- :func:`from_yaml`  – round-trip / re-format a YAML file (symmetry alias)

Conversion — from YAML
-----------------------
- :func:`to_json`  – convert a YAML file to JSON
- :func:`to_xml`   – convert a YAML file to XML
- :func:`to_yaml`  – pretty-print / re-format a YAML file

Optional dependencies:
    PyYAML (``pyyaml``) is required for all operations.
    Jinja2 (``jinja2``) is required for :func:`yaml_template` only.
    Availability can be checked via ``YAML_AVAILABLE`` and ``JINJA_AVAILABLE``.
"""

from .yaml_core_functions import (
    # Reading & Writing
    read_yaml,
    write_yaml,
    yaml_to_dict,
    # Merging & Templating
    merge_yaml,
    yaml_template,
    # Conversion — to YAML
    from_json,
    from_xml,
    from_yaml,
    # Conversion — from YAML
    to_json,
    to_xml,
    to_yaml,
    # Availability flags (useful for optional-dependency feature checks)
    YAML_AVAILABLE,
    JINJA_AVAILABLE,
)

__all__ = [
    # Reading & Writing
    "read_yaml",
    "write_yaml",
    "yaml_to_dict",
    # Merging & Templating
    "merge_yaml",
    "yaml_template",
    # Conversion — to YAML
    "from_json",
    "from_xml",
    "from_yaml",
    # Conversion — from YAML
    "to_json",
    "to_xml",
    "to_yaml",
    # Availability flags
    "YAML_AVAILABLE",
    "JINJA_AVAILABLE",
]

__version__ = "0.0.1"
__author__ = "TBL"
