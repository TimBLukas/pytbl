"""Colorized terminal output helpers."""

from __future__ import annotations

import os
import sys
from typing import Iterable, Optional


class ANSIColors:
    """ANSI escape-code constants used by CLI output helper functions."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"


def supports_color(stream: Optional[object] = None) -> bool:
    """Return True when color output is likely supported."""

    target = stream if stream is not None else sys.stdout
    if not hasattr(target, "isatty"):
        return False
    if not target.isatty():
        return False
    return os.environ.get("TERM", "") != "dumb"


def colorize(
    text: str,
    *,
    fg: Optional[str] = None,
    bg: Optional[str] = None,
    bold: bool = False,
    dim: bool = False,
    enabled: Optional[bool] = None,
) -> str:
    """Apply ANSI color codes to text when terminal color is supported."""

    can_use_color = supports_color() if enabled is None else enabled
    if not can_use_color:
        return text

    codes: list[str] = []
    if bold:
        codes.append(ANSIColors.BOLD)
    if dim:
        codes.append(ANSIColors.DIM)
    if fg:
        fg_name = fg.upper()
        codes.append(getattr(ANSIColors, fg_name, ""))
    if bg:
        bg_name = f"BG_{bg.upper()}"
        codes.append(getattr(ANSIColors, bg_name, ""))
    if not codes:
        return text

    return f"{''.join(codes)}{text}{ANSIColors.RESET}"
