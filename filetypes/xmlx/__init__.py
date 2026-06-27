"""
xml_utils
~~~~~~~~~

Utilities for reading, writing, querying, modifying, and validating XML files.

This package provides a high-level interface for working with XML files,
including caching, atomic writes, dictionary conversion, XPath queries,
element manipulation, and XSD schema validation.

Reading & Parsing
-----------------
- :func:`read_xml`          – parse an XML file into an ``ElementTree`` (cached)
- :func:`parse_xml_string`  – parse a raw XML string into a root ``Element``
- :func:`read_xml_as_dict`  – parse an XML file directly into a nested ``dict``
- :func:`xpath_query`       – execute an XPath expression against an XML file

Writing & Creating
------------------
- :func:`write_xml`         – write an ``Element`` or ``ElementTree`` to disk (atomic)
- :func:`create_xml`        – build a root ``Element`` from a nested dict
- :func:`create_xml_file`   – create an XML file from a nested dict in one call

Modifying & Searching
---------------------
- :func:`find_elements`     – find all elements with a given tag (recursive)
- :func:`set_element_text`  – update the text of the first element matching an XPath
- :func:`append_child`      – append a child element to the first parent matching an XPath
- :func:`remove_elements`   – remove all elements matching an XPath
- :func:`merge_xml`         – merge two XML files (override wins on overlapping elements)

Validation
----------
- :func:`validate_xml_schema` – validate an XML file against an XSD schema
                                (requires ``lxml``)

Optional dependency:
    lxml (``lxml``) enables full XPath support in :func:`xpath_query`,
    :func:`set_element_text`, :func:`remove_elements`, and
    :func:`validate_xml_schema`. All other functions fall back to the
    standard-library ``xml.etree.ElementTree``.
    Availability can be checked via ``LXML_AVAILABLE``.
"""

from .xml_core_functions import (
    # Reading & Parsing
    read_xml,
    parse_xml_string,
    read_xml_as_dict,
    xpath_query,
    # Writing & Creating
    write_xml,
    create_xml,
    create_xml_file,
    # Modifying & Searching
    find_elements,
    set_element_text,
    append_child,
    remove_elements,
    merge_xml,
    # Validation
    validate_xml_schema,
    # Availability flag (useful for optional-dependency feature checks)
    LXML_AVAILABLE,
)

__all__ = [
    # Reading & Parsing
    "read_xml",
    "parse_xml_string",
    "read_xml_as_dict",
    "xpath_query",
    # Writing & Creating
    "write_xml",
    "create_xml",
    "create_xml_file",
    # Modifying & Searching
    "find_elements",
    "set_element_text",
    "append_child",
    "remove_elements",
    "merge_xml",
    # Validation
    "validate_xml_schema",
    # Availability flag
    "LXML_AVAILABLE",
]

__version__ = "0.0.1"
__author__ = "TBL"
