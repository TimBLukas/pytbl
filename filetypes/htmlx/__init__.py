"""
html_utils
~~~~~~~~~~

A lightweight HTML reading, generation, and manipulation library.

Reading & Parsing
-----------------
- :func:`read_html`          – parse an HTML file into a BeautifulSoup object (cached)
- :func:`parse_html_string`  – parse a raw HTML string
- :func:`extract_text`       – extract plain text, optionally scoped to a CSS selector
- :func:`extract_links`      – collect all <a href> targets with their link text

Generating HTML
---------------
- :func:`generate_html`      – produce a complete ``<!DOCTYPE html>`` document
- :func:`create_html_log`    – render a list of log entries as a styled HTML report
- :func:`tag`                – build any single HTML element (functional style)
- :func:`table`              – generate an HTML table from 2-D data
- :func:`unordered_list`     – generate a ``<ul>`` list
- :func:`ordered_list`       – generate an ``<ol>`` list

Modifying & Writing
-------------------
- :func:`write_html`         – write an HTML string to disk (optionally atomic)
- :func:`update_html`        – patch elements in an existing file via CSS selector

BeautifulSoup (``beautifulsoup4``) is required for all read/update operations.
It is an optional dependency — generation helpers work without it.
"""

from .html_core_functions import (
    # Reading & Parsing
    read_html,
    parse_html_string,
    extract_text,
    extract_links,
    # Generating HTML
    generate_html,
    create_html_log,
    tag,
    table,
    unordered_list,
    ordered_list,
    # Modifying & Writing
    write_html,
    update_html,
)

__all__ = [
    # Reading & Parsing
    "read_html",
    "parse_html_string",
    "extract_text",
    "extract_links",
    # Generating HTML
    "generate_html",
    "create_html_log",
    "tag",
    "table",
    "unordered_list",
    "ordered_list",
    # Modifying & Writing
    "write_html",
    "update_html",
]
