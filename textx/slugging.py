"""URL- and identifier-friendly slug helpers."""

from __future__ import annotations

import re
import unicodedata


def slugify(
    value: object,
    *,
    separator: str = "-",
    lowercase: bool = True,
    max_length: int | None = None,
) -> str:
    """Turn a value into a stable, human-readable slug.

    Accented characters are transliterated where Unicode provides a
    decomposition; punctuation and whitespace become ``separator``.
    """
    if not separator or any(character.isspace() for character in separator):
        raise ValueError("separator must be non-empty and contain no whitespace")
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", separator, text)
    text = text.strip(separator)
    text = re.sub(re.escape(separator) + r"{2,}", separator, text)
    if lowercase:
        text = text.lower()
    if max_length is not None:
        if max_length < 1:
            raise ValueError("max_length must be positive")
        text = text[:max_length].rstrip(separator)
    return text


slug = slugify
make_slug = slugify
slugify_text = slugify