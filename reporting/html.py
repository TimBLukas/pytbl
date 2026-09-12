"""HTML renderer facade."""

from .renderers import HTMLRenderer, HtmlRenderer, escape_html, render_to_string, write_report

__all__ = ["HtmlRenderer", "HTMLRenderer", "escape_html", "render_to_string", "write_report"]
