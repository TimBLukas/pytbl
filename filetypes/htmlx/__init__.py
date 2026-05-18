"""
html_utils – HTML parsing, generation, and log creation.

Public API:
    - read_html / parse_html_string
    - extract_text / extract_links
    - generate_html / create_html_log
    - tag / table / unordered_list / ordered_list
    - write_html / update_html
"""

from .html_utils import (
    read_html,
    parse_html_string,
    extract_text,
    extract_links,
    generate_html,
    create_html_log,
    tag,
    table,
    unordered_list,
    ordered_list,
    write_html,
    update_html,
)

__all__ = [
    "read_html",
    "parse_html_string",
    "extract_text",
    "extract_links",
    "generate_html",
    "create_html_log",
    "tag",
    "table",
    "unordered_list",
    "ordered_list",
    "write_html",
    "update_html",
]

__version__ = "0.1.0"