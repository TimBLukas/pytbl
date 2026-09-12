"""Backward-compatible Markdown reporting facade."""

from .document import *
from .renderers import MarkdownRenderer, escape_markdown, render_to_string, write_report
