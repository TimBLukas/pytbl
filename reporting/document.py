"""Format-neutral document components used by the reporting package."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Sequence


Content = Any


@dataclass(frozen=True)
class ReportMetadata:
    """Optional metadata displayed by document renderers."""

    title: str | None = None
    subtitle: str | None = None
    author: str | None = None
    date: str | date | None = None
    description: str | None = None
    version: str | None = None
    language: str = "en"

    def values(self) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in self.__dict__.items()
            if value is not None and key != "language"
        }


@dataclass(frozen=True)
class Heading:
    text: Content
    level: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 6:
            raise ValueError("heading level must be between 1 and 6")


@dataclass(frozen=True)
class Paragraph:
    text: Content


@dataclass(frozen=True)
class Emphasis:
    text: Content
    strong: bool = False


@dataclass(frozen=True)
class Strong(Emphasis):
    """Strong emphasis rendered as bold text."""

    def __init__(self, text: Content) -> None:
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "strong", True)


Bold = Strong


@dataclass(frozen=True)
class Link:
    text: Content
    url: str
    title: str | None = None

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("link URL cannot be empty")


@dataclass(frozen=True)
class Image:
    source: str
    alt: str = ""
    title: str | None = None

    @property
    def url(self) -> str:
        return self.source


@dataclass(frozen=True)
class InlineCode:
    code: str


@dataclass(frozen=True)
class ListItem:
    content: Content
    children: tuple["ListItem", ...] = ()

    def __init__(self, content: Content, children: Iterable["ListItem"] = ()) -> None:
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "children", tuple(children))


@dataclass(frozen=True)
class ListBlock:
    items: tuple[ListItem | Content, ...] = ()
    ordered: bool = False
    start: int = 1

    def __init__(
        self,
        items: Iterable[ListItem | Content] = (),
        ordered: bool = False,
        start: int = 1,
    ) -> None:
        if start < 1:
            raise ValueError("list start must be positive")
        object.__setattr__(
            self,
            "items",
            tuple(item if isinstance(item, ListItem) else ListItem(item) for item in items),
        )
        object.__setattr__(self, "ordered", ordered)
        object.__setattr__(self, "start", start)


List = ListBlock


@dataclass(frozen=True)
class BlockQuote:
    content: Content


@dataclass(frozen=True)
class CodeBlock:
    code: str
    language: str | None = None


@dataclass(frozen=True)
class Table:
    headers: tuple[Content, ...]
    rows: tuple[tuple[Content, ...], ...] = ()
    alignments: tuple[str | None, ...] = ()
    caption: str | None = None

    def __init__(
        self,
        headers: Sequence[Content],
        rows: Iterable[Sequence[Content]] = (),
        alignments: Sequence[str | None] = (),
        caption: str | None = None,
    ) -> None:
        header_values = tuple(headers)
        row_values = tuple(tuple(row) for row in rows)
        if not header_values:
            raise ValueError("a table requires at least one header")
        if any(len(row) != len(header_values) for row in row_values):
            raise ValueError("each table row must match the number of headers")
        if alignments and len(alignments) != len(header_values):
            raise ValueError("alignments must match the number of headers")
        normalized = tuple(
            alignment.lower() if alignment else None for alignment in alignments
        )
        if any(value not in (None, "left", "center", "right") for value in normalized):
            raise ValueError("table alignments must be left, center, right, or None")
        object.__setattr__(self, "headers", header_values)
        object.__setattr__(self, "rows", row_values)
        object.__setattr__(self, "alignments", normalized)
        object.__setattr__(self, "caption", caption)

    @classmethod
    def from_records(cls, records: Iterable[dict[str, Content]]) -> "Table":
        """Build a table from dictionaries using the first record's keys."""
        values = list(records)
        if not values:
            raise ValueError("records cannot be empty")
        headers = tuple(values[0])
        return cls(headers, ([record.get(header, "") for header in headers] for record in values))


@dataclass(frozen=True)
class HorizontalRule:
    """A thematic break."""


@dataclass(frozen=True)
class MermaidBlock:
    diagram: Any


@dataclass(frozen=True)
class Section:
    """A titled group of document components."""

    title: str
    components: tuple[Content, ...] = ()
    level: int = 2

    def __init__(
        self,
        title: str,
        components: Iterable[Content] = (),
        level: int = 2,
    ) -> None:
        if not title.strip():
            raise ValueError("section title cannot be empty")
        if not 1 <= level <= 6:
            raise ValueError("section level must be between 1 and 6")
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "components", tuple(components))
        object.__setattr__(self, "level", level)


@dataclass(frozen=True)
class RawContent:
    content: str
    format: str = "any"

    def __post_init__(self) -> None:
        if self.format not in {"any", "markdown", "html", "text"}:
            raise ValueError("raw content format must be any, markdown, html, or text")


@dataclass
class Report:
    """A sequence of reusable document components."""

    title: str | None = None
    subtitle: str | None = None
    author: str | None = None
    date: str | date | None = None
    description: str | None = None
    version: str | None = None
    components: list[Content] = field(default_factory=list)
    metadata: ReportMetadata | None = None

    def __post_init__(self) -> None:
        if isinstance(self.metadata, dict):
            self.metadata = ReportMetadata(**self.metadata)
        if self.metadata is not None:
            for name in ("title", "subtitle", "author", "date", "description", "version"):
                if getattr(self, name) is None:
                    setattr(self, name, getattr(self.metadata, name))
        self.components = [
            component if not isinstance(component, str) else Paragraph(component)
            for component in self.components
        ]

    @property
    def elements(self) -> list[Content]:
        """Alias for ``components``."""
        return self.components

    @property
    def blocks(self) -> list[Content]:
        """Alias for ``components``."""
        return self.components

    @property
    def sections(self) -> list[Content]:
        """Alias for ``components``."""
        return self.components

    def add(self, component: Content) -> "Report":
        self.components.append(component if not isinstance(component, str) else Paragraph(component))
        return self

    append = add

    def extend(self, components: Iterable[Content]) -> "Report":
        for component in components:
            self.add(component)
        return self

    def heading(self, text: Content, level: int = 1) -> "Report":
        return self.add(Heading(text, level))

    add_heading = heading

    def paragraph(self, text: Content) -> "Report":
        return self.add(Paragraph(text))

    add_paragraph = paragraph

    def emphasis(self, text: Content, strong: bool = False) -> "Report":
        return self.add(Paragraph(Emphasis(text, strong)))

    def link(self, text: Content, url: str, title: str | None = None) -> "Report":
        return self.add(Paragraph(Link(text, url, title)))

    add_link = link

    def image(self, source: str, alt: str = "", title: str | None = None) -> "Report":
        return self.add(Image(source, alt, title))

    add_image = image

    def code(self, code: str, language: str | None = None) -> "Report":
        return self.add(CodeBlock(code, language))

    add_code = code

    def inline_code(self, code: str) -> "Report":
        return self.add(Paragraph(InlineCode(code)))

    def bullet_list(self, items: Iterable[Content]) -> "Report":
        return self.add(ListBlock(items))

    add_list = bullet_list

    def ordered_list(self, items: Iterable[Content], start: int = 1) -> "Report":
        return self.add(ListBlock(items, ordered=True, start=start))

    def table(
        self,
        headers: Sequence[Content],
        rows: Iterable[Sequence[Content]] = (),
        **kwargs: Any,
    ) -> "Report":
        return self.add(Table(headers, rows, **kwargs))

    add_table = table

    def horizontal_rule(self) -> "Report":
        return self.add(HorizontalRule())

    add_horizontal_rule = horizontal_rule

    def mermaid(self, diagram: Any) -> "Report":
        return self.add(MermaidBlock(diagram))

    add_mermaid = mermaid

    def section(
        self,
        title: str,
        components: Iterable[Content] = (),
        level: int = 2,
    ) -> "Report":
        return self.add(Section(title, components, level))

    add_section = section

    def raw(self, content: str, format: str = "any") -> "Report":
        return self.add(RawContent(content, format))

    add_raw = raw
    def render(self, renderer: Any = None, *, format: str | None = None) -> str:
        if format is not None:
            renderer = format
        if renderer is None:
            from .renderers import MarkdownRenderer
            renderer = MarkdownRenderer()
        elif isinstance(renderer, str):
            from .renderers import HtmlRenderer, MarkdownRenderer
            renderer = HtmlRenderer() if renderer.lower() in {"html", "htm"} else MarkdownRenderer()
        elif isinstance(renderer, type):
            renderer = renderer()
        return renderer.render(self)

    def render_to_string(self, renderer: Any = None, *, format: str | None = None) -> str:
        return self.render(renderer, format=format)

    def write(
        self,
        path: str | Path,
        renderer: Any = None,
        encoding: str = "utf-8",
        *,
        format: str | None = None,
    ) -> Path:
        destination = Path(path)
        if format is not None:
            renderer = format
        elif renderer is None and destination.suffix.lower() in {".html", ".htm"}:
            renderer = "html"
        destination.write_text(self.render(renderer), encoding=encoding)
        return destination

    write_to = write
    render_to_file = write


Document = Report
ReportElement = Content
Text = Paragraph
UnorderedList = ListBlock
OrderedList = ListBlock
Blockquote = BlockQuote
ImageBlock = Image
Mermaid = MermaidBlock
Diagram = MermaidBlock
