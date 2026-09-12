"""Text wrapping helpers built on Python's standard :mod:`textwrap`."""

from __future__ import annotations

import textwrap


def wrap_text(
    text: str,
    width: int = 70,
    *,
    initial_indent: str = "",
    subsequent_indent: str = "",
    break_long_words: bool = True,
    break_on_hyphens: bool = True,
) -> str:
    """Wrap text to ``width`` columns while retaining paragraph breaks."""
    if width < 1:
        raise ValueError("width must be at least 1")
    wrapper = textwrap.TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=break_long_words,
        break_on_hyphens=break_on_hyphens,
    )
    paragraphs = text.splitlines()
    return "\n".join(wrapper.fill(line) if line.strip() else "" for line in paragraphs)


def wrap_words(text: str, width: int = 70) -> list[str]:
    """Return wrapped lines rather than a joined string."""
    if width < 1:
        raise ValueError("width must be at least 1")
    return textwrap.wrap(text, width=width)


def indent(text: str, prefix: str = "  ", *, predicate=None) -> str:
    """Indent each line, optionally using a line predicate."""
    return textwrap.indent(text, prefix, predicate)


def dedent(text: str) -> str:
    """Remove common leading whitespace from text."""
    return textwrap.dedent(text)


wrap = wrap_text

