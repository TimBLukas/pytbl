# ------------------------------------------
# Standard Library imports
# ------------------------------------------
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator
from html.parser import HTMLParser
from html import escape

# ------------------------------------------
# Library specific imports
# ------------------------------------------
from datatypes import PathLike

# ------------------------------------------
# External Imports (optional)
# ------------------------------------------
try:
    from bs4 import BeautifulSoup

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# ------------------------------------------
# Globals (caching)
# ------------------------------------------
_CACHE_PATH: Optional[Path] = None
_CACHE_HTML: Optional[str] = None
_CACHE_SOUP: Any = None
_CACHE_MTIME: float = 0.0


# ------------------------------------------
# Private Helper Functions
# ------------------------------------------
def _normalize_path(path: PathLike) -> Path:
    """Convert PathLike to Path object."""
    return Path(path) if isinstance(path, str) else path


def _ensure_cache(path: PathLike, reload: bool = False) -> Any:
    """
    Load an HTML file and parse it with BeautifulSoup (cached).

    Returns:
        BeautifulSoup object.
    """
    global _CACHE_PATH, _CACHE_SOUP, _CACHE_MTIME
    target = _normalize_path(path).resolve()
    current_mtime = target.stat().st_mtime if target.exists() else 0

    cache_valid = (
        _CACHE_PATH == target
        and _CACHE_SOUP is not None
        and not reload
        and current_mtime == _CACHE_MTIME
    )

    if not cache_valid:
        if not target.exists():
            raise FileNotFoundError(f"HTML file not found: {target}")

        with target.open("r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, parser)
        _CACHE_PATH = target
        _CACHE_SOUP = soup
        _CACHE_MTIME = current_mtime

    return _CACHE_SOUP


def _render_html(
    tag: str, content: str = "", attributes: Optional[Dict[str, str]] = None
) -> str:
    """Render a single HTML tag with attributes and content."""
    attr_str = ""
    if attributes:
        # convert attribute names: 'class_' -> 'class'
        attrs = {}
        for k, v in attributes.items():
            key = k.rstrip("_")
            attrs[key] = v
            attr_str = " " + " ".join(
                f'{key}="{escape(str(val))}"' for key, val in attrs.items()
            )

    return f"<{tag}{attr_str}>{content}</{tag}"


def _escape_html(text: str) -> str:
    """Escape special characters for HTML."""
    return escape(text)


# ------------------------------------------
# Public Facing API – Reading & Parsing
# ------------------------------------------
def read_html(
    path: PathLike, use_cache: bool = True, parser: str = "html.parser"
) -> Any:
    """
    Read an HTML file and parse it with BeautifulSoup.

    Args:
        path: Path to the HTML file.
        use_cache: If True, use a cache keyed by file modification time.
        parser: Parser backend ('html.parser', 'lxml', 'html5lib').

    Returns:
        BeautifulSoup object (if BeautifulSoup is available).
        Otherwise raises ImportError.

    Raises:
        ImportError: If BeautifulSoup is not installed.
        FileNotFoundError: If the file does not exist.

    Example:
        >>> soup = read_html("report.html")
        >>> title = soup.title.string
    """
    if not BEAUTIFULSOUP_AVAILABLE:
        raise ImportError(
            "BeautifulSoup4 is required. Install with: pip install beautifulsoup4"
        )

    if use_cache:
        return _ensure_cache(path, parser=parser)
    target = _normalize_path(path)
    with target.open("r", encoding="utf-8") as f:
        html_content = f.read()

    return BeautifulSoup(html_content, parser)


def parse_html_string(html_string: str, parser: str = "html.parser") -> Any:
    """
    Parse an HTML string into a BeautifulSoup object.

    Args:
        html_string: Raw HTML content.
        parser: Parser backend.

    Returns:
        BeautifulSoup object.
    """
    if not BEAUTIFULSOUP_AVAILABLE:
        raise ImportError(
            "BeautifulSoup4 is required. Install with: pip install beautifulsoup4"
        )
    return BeautifulSoup(html_string, parser)


def extract_text(path: PathLike, selector: Optional[str] = None) -> str:
    """
    Extract plain text from an HTML file, optionally limited to a CSS selector.

    Args:
        path: Path to the HTML file.
        selector: CSS selector (e.g., '.content', '#main p').

    Returns:
        Extracted text (concatenated).
    """
    soup = read_html(path)
    if selector:
        elements = soup.select(selector)
        return " ".join(el.get_text(strip=True) for el in elements)

    return soup.get_text(strip=True)


def extract_links(
    path: PathLike, base_url: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Extract all <a> tags with href and text.

    Args:
        path: Path to the HTML file.
        base_url: If provided, resolve relative URLs.

    Returns:
        List of dicts: [{'href': '...', 'text': '...'}, ...]
    """
    soup = read_html(path)
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if base_url:
            href = urljoin(base_url, href)
        text = urljoin(base_url, href)
        links.append({"href": href, "text": text})

    return links


# ------------------------------------------
# Public Facing API – Generating HTML
# ------------------------------------------
def generate_html(
    title: str,
    body_content: str,
    style: Optional[str] = None,
    head_extras: Optional[str] = None,
) -> str:
    """
    Generate a complete HTML document.

    Args:
        title: Page title.
        body_content: HTML content for the <body>.
        style: CSS styles (string or path to CSS file).
        head_extras: Additional <head> content (e.g., meta tags, scripts).

    Returns:
        Complete HTML string.
    """
    css_content = ""
    if style:
        style_path = Path(style)
        if style_path.exists():
            with style_path.open("r", encoding="utf-8") as f:
                css_content = f.read()

        else:
            css_content = style

    style_tag = f"<style>{css_content}</style>" if css_content else ""
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width", initial-scale=1.0">
        <title>{_escape_html(title)}</title>
        {style_tag}
        {head_extras or ""}
    </head>
    <body>
        {body_content}
    </body>
    </html>"""
    return html


def create_html_log(
    log_entries: List[Dict[str, str]],
    title: str = "Application Log",
    output_path: Optional[PathLike] = None,
) -> Optional[str]:
    """
    Create a styled HTML log report from a list of log entries.

    Args:
        log_entries: List of dicts with keys: 'timestamp', 'level', 'message'.
        title: Report title.
        output_path: If provided, write to file; else return HTML string.

    Returns:
        HTML string if output_path is None, else None.
    """
    # TODO: generate a table with log entries
    pass


def tag(name: str, content: Union[str, List[str]] = "", **attributes) -> str:
    """
    Build a single HTML tag (functional style).

    Args:
        name: Tag name (e.g., 'div', 'p').
        content: Inner HTML (string or list of strings/child tags).
        **attributes: Tag attributes (e.g., class_='btn', id='main').

    Returns:
        HTML string.

    Example:
        >>> tag('a', 'Click me', href='https://example.com', class_='link')
        '<a href="https://example.com" class="link">Click me</a>'
    """
    # TODO: implement
    pass


def table(data: List[List[str]], headers: Optional[List[str]] = None, **attrs) -> str:
    """
    Generate an HTML table from 2D data.

    Args:
        data: List of rows (each row is a list of strings).
        headers: Optional list of column headers.
        **attrs: Table attributes (class, id, etc.).

    Returns:
        HTML table string.
    """
    # TODO: build <table> with <thead> and <tbody>
    pass


def unordered_list(items: List[str], **attrs) -> str:
    """Generate a <ul> list."""
    # TODO: implement
    pass


def ordered_list(items: List[str], **attrs) -> str:
    """Generate an <ol> list."""
    # TODO: implement
    pass


# ------------------------------------------
# Public Facing API – Modifying & Writing
# ------------------------------------------
def write_html(path: PathLike, html_string: str, atomic: bool = True) -> None:
    """
    Write an HTML string to a file, optionally atomically.

    Args:
        path: Destination file path.
        html_string: Complete HTML content.
        atomic: If True, write via temporary file.
    """
    # TODO: implement
    pass


def update_html(
    path: PathLike, selector: str, new_content: str, attribute: Optional[str] = None
) -> None:
    """
    Update an existing HTML file by replacing content of matched elements.

    Args:
        path: Path to HTML file.
        selector: CSS selector for elements to modify.
        new_content: New inner HTML or attribute value.
        attribute: If given, update this attribute instead of inner HTML.
    """
    # TODO: use BeautifulSoup to modify and write back
    pass

