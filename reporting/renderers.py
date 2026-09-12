"""Markdown and HTML renderers for :mod:`reporting.document`."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any, Iterable

from .document import (
    BlockQuote,
    CodeBlock,
    Emphasis,
    Heading,
    HorizontalRule,
    Image,
    InlineCode,
    Link,
    ListBlock,
    ListItem,
    MermaidBlock,
    Paragraph,
    RawContent,
    Report,
    Section,
    Table,
)


def escape_markdown(value: object, *, table: bool = False) -> str:
    """Escape user text so it remains literal Markdown."""
    text = str(value)
    text = text.replace("\\", "\\\\")
    for character in r"`*_{}[]<>#+-.!|":
        if character == "|" and not table:
            continue
        text = text.replace(character, "\\" + character)
    return text


def escape_html(value: object, *, quote: bool = True) -> str:
    """Escape text for safe HTML text or attribute content."""
    return html.escape(str(value), quote=quote)


def _safe_url(value: str) -> str:
    """Reject control characters and dangerous executable URL schemes."""
    if any(ord(character) < 32 for character in value):
        raise ValueError("URLs cannot contain control characters")
    if re.match(r"(?i)^(?:javascript|vbscript|data):", value.strip()):
        raise ValueError("unsafe URL scheme")
    return value


def _diagram_text(diagram: Any) -> str:
    if hasattr(diagram, "to_mermaid"):
        return str(diagram.to_mermaid())
    if hasattr(diagram, "render"):
        return str(diagram.render())
    return str(diagram)


class MarkdownRenderer:
    """Render a :class:`Report` as CommonMark-compatible Markdown."""

    format = "markdown"

    def render(self, report: Report) -> str:
        parts: list[str] = []
        if report.title:
            parts.append("# " + escape_markdown(report.title))
        if report.subtitle:
            parts.append("## " + escape_markdown(report.subtitle))
        if report.author or report.date:
            details = " — ".join(
                str(value) for value in (report.author, report.date) if value
            )
            parts.append("*" + escape_markdown(details) + "*")
        if report.description:
            parts.append(escape_markdown(report.description))
        parts.extend(
            self.render_component(component) for component in report.components
        )
        return "\n\n".join(part for part in parts if part != "") + (
            "\n" if parts else ""
        )

    render_to_string = render

    def write(self, report: Report, path: str | Path, encoding: str = "utf-8") -> Path:
        destination = Path(path)
        destination.write_text(self.render(report), encoding=encoding)
        return destination

    def render_inline(self, value: Any) -> str:
        if isinstance(value, (list, tuple)):
            return "".join(self.render_inline(item) for item in value)
        if isinstance(value, Emphasis):
            marker = "**" if value.strong else "*"
            return marker + self.render_inline(value.text) + marker
        if isinstance(value, Link):
            url = _safe_url(value.url).replace("(", r"\(").replace(")", r"\)")
            title = f' "{escape_markdown(value.title)}"' if value.title else ""
            return f"[{self.render_inline(value.text)}]({url}{title})"
        if isinstance(value, Image):
            url = _safe_url(value.source).replace("(", r"\(").replace(")", r"\)")
            title = f' "{escape_markdown(value.title)}"' if value.title else ""
            return f"![{escape_markdown(value.alt)}]({url}{title})"
        if isinstance(value, InlineCode):
            fence = "`" if "`" not in value.code else "``"
            return f"{fence}{value.code}{fence}"
        return escape_markdown(value)

    def render_component(self, component: Any, *, list_depth: int = 0) -> str:
        if isinstance(component, str):
            return escape_markdown(component)
        if isinstance(component, Heading):
            return "#" * component.level + " " + self.render_inline(component.text)
        if isinstance(component, Section):
            parts = ["#" * component.level + " " + self.render_inline(component.title)]
            parts.extend(self.render_component(item) for item in component.components)
            return "\n\n".join(parts)
        if isinstance(component, Paragraph):
            return self.render_inline(component.text)
        if isinstance(component, (Link, Image, InlineCode, Emphasis)):
            return self.render_inline(component)
        if isinstance(component, ListBlock):
            return self._render_list(component, list_depth)
        if isinstance(component, ListItem):
            return self.render_inline(component.content)
        if isinstance(component, BlockQuote):
            body = component.content
            rendered = (
                "\n\n".join(self.render_component(item) for item in body)
                if isinstance(body, (list, tuple))
                else self.render_inline(body)
            )
            return "\n".join(
                "> " + line if line else ">" for line in rendered.splitlines()
            )
        if isinstance(component, CodeBlock):
            language = component.language or ""
            fence = "```" if "```" not in component.code else "````"
            return f"{fence}{language}\n{component.code}\n{fence}"
        if isinstance(component, Table):
            headers = [
                self.render_inline(value).replace("|", r"\|")
                for value in component.headers
            ]
            separator = []
            for alignment in component.alignments or (None,) * len(headers):
                separator.append(
                    ":---:"
                    if alignment == "center"
                    else "---:"
                    if alignment == "right"
                    else ":---"
                    if alignment == "left"
                    else "---"
                )
            rows = [
                "| " + " | ".join(headers) + " |",
                "| " + " | ".join(separator) + " |",
            ]
            rows.extend(
                "| "
                + " | ".join(
                    self.render_inline(value).replace("|", r"\|") for value in row
                )
                + " |"
                for row in component.rows
            )
            if component.caption:
                rows.insert(0, f"**{escape_markdown(component.caption)}**")
            return "\n".join(rows)
        if isinstance(component, HorizontalRule):
            return "---"
        if isinstance(component, MermaidBlock):
            return "```mermaid\n" + _diagram_text(component.diagram).rstrip() + "\n```"
        if isinstance(component, RawContent):
            return (
                component.content
                if component.format in {"any", "markdown", "text"}
                else escape_markdown(component.content)
            )
        return self.render_inline(component)

    def _render_list(self, block: ListBlock, depth: int = 0) -> str:
        lines: list[str] = []
        indent = "  " * depth
        for index, item in enumerate(block.items):
            marker = f"{block.start + index}." if block.ordered else "-"
            item = item if isinstance(item, ListItem) else ListItem(item)
            content = self.render_inline(item.content)
            lines.append(f"{indent}{marker} {content}")
            if item.children:
                nested = self._render_list(
                    ListBlock(item.children, ordered=False), depth + 1
                )
                lines.extend(nested.splitlines())
        return "\n".join(lines)


class HtmlRenderer:
    """Render a :class:`Report` as a complete escaped HTML document."""

    format = "html"

    def render(self, report: Report) -> str:
        language = report.metadata.language if report.metadata else "en"
        title = report.title or "Report"
        head = [f'<meta charset="utf-8">', f"<title>{escape_html(title)}</title>"]
        if report.description:
            head.append(
                f'<meta name="description" content="{escape_html(report.description)}">'
            )
        if report.author:
            head.append(f'<meta name="author" content="{escape_html(report.author)}">')
        body: list[str] = []
        if report.title:
            body.append(f"<h1>{self.render_inline(report.title)}</h1>")
        if report.subtitle:
            body.append(f"<h2>{self.render_inline(report.subtitle)}</h2>")
        if report.author or report.date:
            details = " — ".join(
                str(value) for value in (report.author, report.date) if value
            )
            body.append(f"<p><em>{self.render_inline(details)}</em></p>")
        if report.description:
            body.append(f"<p>{self.render_inline(report.description)}</p>")
        body.extend(self.render_component(component) for component in report.components)
        return (
            "<!doctype html>\n"
            f'<html lang="{escape_html(language)}">\n<head>\n'
            + "\n".join(head)
            + "\n</head>\n<body>\n"
            + "\n".join(part for part in body if part)
            + "\n</body>\n</html>\n"
        )

    render_to_string = render

    def write(self, report: Report, path: str | Path, encoding: str = "utf-8") -> Path:
        destination = Path(path)
        destination.write_text(self.render(report), encoding=encoding)
        return destination

    def render_inline(self, value: Any) -> str:
        if isinstance(value, (list, tuple)):
            return "".join(self.render_inline(item) for item in value)
        if isinstance(value, Emphasis):
            tag = "strong" if value.strong else "em"
            return f"<{tag}>{self.render_inline(value.text)}</{tag}>"
        if isinstance(value, Link):
            url = escape_html(_safe_url(value.url))
            title = f' title="{escape_html(value.title)}"' if value.title else ""
            return f'<a href="{url}"{title}>{self.render_inline(value.text)}</a>'
        if isinstance(value, Image):
            source = escape_html(_safe_url(value.source))
            title = f' title="{escape_html(value.title)}"' if value.title else ""
            return f'<img src="{source}" alt="{escape_html(value.alt)}"{title}>'
        if isinstance(value, InlineCode):
            return f"<code>{escape_html(value.code)}</code>"
        return escape_html(value)

    def render_component(self, component: Any) -> str:
        if isinstance(component, str):
            return f"<p>{escape_html(component)}</p>"
        if isinstance(component, Heading):
            return f"<h{component.level}>{self.render_inline(component.text)}</h{component.level}>"
        if isinstance(component, Section):
            parts = [
                f"<h{component.level}>{self.render_inline(component.title)}</h{component.level}>"
            ]
            parts.extend(self.render_component(item) for item in component.components)
            return "\n".join(parts)
        if isinstance(component, Paragraph):
            return f"<p>{self.render_inline(component.text)}</p>"
        if isinstance(component, (Link, Image, InlineCode, Emphasis)):
            return f"<p>{self.render_inline(component)}</p>"
        if isinstance(component, ListBlock):
            tag = "ol" if component.ordered else "ul"
            start = (
                f' start="{component.start}"'
                if component.ordered and component.start != 1
                else ""
            )
            return (
                f"<{tag}{start}>\n"
                + "\n".join(self._render_item(item) for item in component.items)
                + f"\n</{tag}>"
            )
        if isinstance(component, BlockQuote):
            body = (
                "\n".join(self.render_component(item) for item in component.content)
                if isinstance(component.content, (list, tuple))
                else f"<p>{self.render_inline(component.content)}</p>"
            )
            return f"<blockquote>\n{body}\n</blockquote>"
        if isinstance(component, CodeBlock):
            language = (
                f' class="language-{escape_html(component.language)}"'
                if component.language
                else ""
            )
            return f"<pre><code{language}>{escape_html(component.code)}</code></pre>"
        if isinstance(component, Table):
            caption = (
                f"<caption>{escape_html(component.caption)}</caption>"
                if component.caption
                else ""
            )
            headers = "".join(
                f"<th>{self.render_inline(value)}</th>" for value in component.headers
            )
            rows = "\n".join(
                "<tr>"
                + "".join(f"<td>{self.render_inline(value)}</td>" for value in row)
                + "</tr>"
                for row in component.rows
            )
            return f"<table>\n{caption}<thead><tr>{headers}</tr></thead>\n<tbody>{rows}</tbody>\n</table>"
        if isinstance(component, HorizontalRule):
            return "<hr>"
        if isinstance(component, MermaidBlock):
            return f'<pre class="mermaid">{escape_html(_diagram_text(component.diagram))}</pre>'
        if isinstance(component, RawContent):
            if component.format in {"any", "html"}:
                return component.content
            return f"<p>{escape_html(component.content)}</p>"
        return f"<p>{self.render_inline(component)}</p>"

    def _render_item(self, item: Any) -> str:
        item = item if isinstance(item, ListItem) else ListItem(item)
        content = self.render_inline(item.content)
        if item.children:
            content += "\n" + self.render_component(ListBlock(item.children))
        return f"<li>{content}</li>"


HTMLRenderer = HtmlRenderer


def render_to_string(report: Report, format: str = "markdown") -> str:
    """Render a report without explicitly constructing a renderer."""
    renderer = (
        HtmlRenderer() if format.lower() in {"html", "htm"} else MarkdownRenderer()
    )
    return renderer.render(report)


def write_report(
    report: Report,
    path: str | Path,
    format: str | None = None,
    encoding: str = "utf-8",
) -> Path:
    """Render a report and write it to a path."""
    destination = Path(path)
    selected = format or (
        "html" if destination.suffix.lower() in {".html", ".htm"} else "markdown"
    )
    destination.write_text(render_to_string(report, selected), encoding=encoding)
    return destination
