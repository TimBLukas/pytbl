"""
xml_utils – XML parsing, creation, modification, and validation.

Public API:
    - read_xml / parse_xml_string / read_xml_as_dict
    - xpath_query
    - write_xml / create_xml / create_xml_file
    - find_elements / set_element_text / append_child / remove_elements
    - merge_xml
    - validate_xml_schema
"""

from .core_functions import (
    read_xml,
    parse_xml_string,
    read_xml_as_dict,
    xpath_query,
    write_xml,
    create_xml,
    create_xml_file,
    find_elements,
    set_element_text,
    append_child,
    remove_elements,
    merge_xml,
    validate_xml_schema,
)

__all__ = [
    "read_xml",
    "parse_xml_string",
    "read_xml_as_dict",
    "xpath_query",
    "write_xml",
    "create_xml",
    "create_xml_file",
    "find_elements",
    "set_element_text",
    "append_child",
    "remove_elements",
    "merge_xml",
    "validate_xml_schema",
]

__version__ = "0.0.1"
__author__ = "TBL"