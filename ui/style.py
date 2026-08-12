"""Style generators for the UI library's tkinter/ttk widgets.

Each ``get_*_style`` function configures a named :class:`ttk.Style` and
returns its name, ready to be passed into a widget's ``style``
option, e.g.::

    btn = ttk.Button(root, text="Save", style=get_success_btn_style(root))

``ttk.Style`` is keyed by interpreter, not by instance, so calling a
``get_*_style`` function again simply reconfigures the same named style.
It is therefore safe (if slightly wasteful) to call on every widget
creation rather than caching the returned name yourself.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Set, Tuple

__all__ = [
    # btn styles
    "get_default_btn_style",
    "get_danger_btn_style",
    "get_success_btn_style",
    "get_outline_btn_style",
    "get_link_btn_style",
    "get_icon_btn_style",
    "get_rounded_btn_style",
    "get_circle_btn_style",
    # widget styles
    "get_label_style",
    "get_entry_style",
    "get_card_style",
    "get_progress_style",
    "get_tab_style",
    "get_sidebar_style",
    "get_alert_style",
    "get_tag_style",
    # container styles
    "get_container_styles",
]


_DEFAULT_FONT: Tuple[str, int] = ("Segoe UI", 10)
_DEFAULT_PADDING: Tuple[int, int] = (16, 9)


_FONT_FAMILY = "Segoe UI"
_H1_FONT = (_FONT_FAMILY, 18, "bold")
_H2_FONT = (_FONT_FAMILY, 14, "bold")
_BODY_FONT = (_FONT_FAMILY, 10)
_SMALL_FONT = (_FONT_FAMILY, 9)

_COLORS = {
    "bg_white": "#ffffff",
    "bg_gray_1": "#f8f9fa",
    "bg_gray_2": "#e9ecef",
    "border": "#dee2e6",
    "primary": "#1c7ed6",
    "success": "#2f9e44",
    "danger": "#e03131",
    "info": "#1098ad",
    "warning": "#f08c00",
    "text_main": "#212529",
    "text_muted": "#868e96",
}

_LABEL_VARIANTS = {"h1", "h2", "body", "muted", "badge"}
_PROGRESS_VARIANTS = {"primary", "success", "danger"}
_FEEDBACK_VARIANTS = {"primary", "success", "danger", "info", "warning"}


def _validate_variant(variant: str, allowed: Set[str], kind: str) -> None:
    if variant not in allowed:
        raise ValueError(f"Unknown {kind} variant: {variant!r}")


def _configure_solid_style(
    root: tk.Misc,
    style_name: str,
    *,
    background: str,
    foreground: str,
    active_background: str,
    pressed_background: str,
    disabled_foreground: str = "#999999",
    font: Tuple[str, int] = _DEFAULT_FONT,
    padding: Tuple[int, int] = _DEFAULT_PADDING,
    borderwidth: int = 0,
) -> str:
    """Configure a flat, solid-color ``TButton`` style and return its name.

    Shared by every "solid" button variant (default, danger, success, ...)
    so each public ``get_*_style`` function only has to supply the colors
    that make it distinct, instead of repeating the full ``configure``/
    ``map`` boilerplate.

    Args:
        root: Any widget (or the root window), used to resolve the
            ``ttk.Style`` instance for the current Tk interpreter.
        style_name: The ttk style identifier to (re)configure, e.g.
            ``"Danger.TButton"``.
        background: Fill color in the widget's resting state.
        foreground: Text color in the widget's resting state.
        active_background: Fill color while hovered.
        pressed_background: Fill color while the mouse button is held down.
        disabled_foreground: Text color when the widget is disabled.
        font: Font used for the button label.
        padding: ``(horizontal, vertical)`` padding in pixels.
        borderwidth: Border width in pixels; ``0`` keeps the flat look.

    Returns:
        The style name, unchanged, so calls can be chained/returned directly.
    """
    style = ttk.Style(root)
    style.configure(
        style_name,
        font=font,
        padding=padding,
        background=background,
        foreground=foreground,
        borderwidth=borderwidth,
    )
    style.map(
        style_name,
        background=[
            ("disabled", background),
            ("pressed", pressed_background),
            ("active", active_background),
        ],
        foreground=[
            ("disabled", disabled_foreground),
        ],
    )
    return style_name


def get_default_btn_style(root: tk.Misc) -> str:
    """Neutral, general-purpose button style for everyday actions."""
    return _configure_solid_style(
        root,
        "Default.TButton",
        background="#f0f0f0",
        foreground="#222222",
        active_background="#e5e5e5",
        pressed_background="#d6d6d6",
    )


def get_danger_btn_style(root: tk.Misc) -> str:
    """Style for destructive or irreversible actions (delete, discard, ...)."""
    return _configure_solid_style(
        root,
        "Danger.TButton",
        background=_COLORS["danger"],
        foreground=_COLORS["bg_white"],
        active_background="#c92a2a",
        pressed_background="#a51111",
        disabled_foreground="#f4c7c7",
    )


def get_success_btn_style(root: tk.Misc) -> str:
    """Style for confirming or positive actions (save, confirm, ...)."""
    return _configure_solid_style(
        root,
        "Success.TButton",
        background=_COLORS["success"],
        foreground=_COLORS["bg_white"],
        active_background="#2b8a3e",
        pressed_background="#237032",
        disabled_foreground="#bfe3c8",
    )


def get_outline_btn_style(root: tk.Misc) -> str:
    """Low-emphasis style: white fill with a colored label, no border."""
    return _configure_solid_style(
        root,
        "Outline.TButton",
        background=_COLORS["bg_white"],
        foreground="#1c7ed6",
        active_background="#e7f5ff",
        pressed_background="#d0ebff",
        disabled_foreground="#a5c8e6",
    )


def get_icon_btn_style(root: tk.Misc) -> str:
    """Compact style with tight padding, suited to icon-only buttons."""
    return _configure_solid_style(
        root,
        "Icon.TButton",
        background="#f0f0f0",
        foreground="#222222",
        active_background="#e5e5e5",
        pressed_background="#d6d6d6",
        padding=(6, 6),
    )


def get_link_btn_style(root: tk.Misc) -> str:
    """Hyperlink-like style: flat, underlined, no button chrome."""
    style = ttk.Style(root)
    style.configure(
        "Link.TButton",
        font=(_DEFAULT_FONT[0], _DEFAULT_FONT[1], "underline"),
        padding=(2, 2),
        background="#f0f0f0",
        foreground="#1c7ed6",
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Link.TButton",
        foreground=[
            ("disabled", "#a5c8e6"),
            ("pressed", "#0b4f8a"),
            ("active", "#1864ab"),
        ],
    )
    return "Link.TButton"


def get_rounded_btn_style(root: tk.Misc) -> str:
    """Pill-shaped button with horizontal padding"""
    return _configure_solid_style(
        root,
        "Rounded.TButton",
        background="#4dabf7",
        foreground=_COLORS["bg_white"],
        active_background=_COLORS["bg_white"],
        pressed_background="#1c7ed6",
        padding=(30, 9),
    )


def get_circle_btn_style(root: tk.Misc) -> str:
    """Style for circular/square icon buttons."""
    return _configure_solid_style(
        root,
        "Circle.TButton",
        background="#f0f0f0",
        foreground="222222",
        active_background="#e5e5e5",
        pressed_background="#d6d6d6",
        padding=(0, 0),
    )


def get_label_style(root: tk.Misc, variant: str = "body") -> str:
    """Typography styles: h1, h2, body, muted or badge"""
    _validate_variant(variant, _LABEL_VARIANTS, "label")
    style = ttk.Style(root)
    name = f"{variant.capitalize()}.TLabel"

    configs: Dict[str, Dict[str, Any]] = {
        "h1": {"font": _H1_FONT, "foreground": _COLORS["text_main"]},
        "h2": {"font": _H2_FONT, "foreground": _COLORS["text_main"]},
        "body": {"font": _BODY_FONT, "foreground": _COLORS["text_main"]},
        "muted": {"font": _SMALL_FONT, "foreground": _COLORS["text_muted"]},
        "badge": {
            "font": _SMALL_FONT,
            "background": _COLORS["primary"],
            "foreground": "white",
            "padding": (4, 2),
        },
    }

    style.configure(name, **configs.get(variant, configs["body"]))

    return name


def get_entry_style(root: tk.Misc, error: bool = False) -> str:
    """Input field style with optional error highlighting."""
    style = ttk.Style(root)
    name = "Error.TEntry" if error else "TEntry"

    border_color = _COLORS["danger"] if error else _COLORS["border"]

    style.configure(
        name,
        fieldbackground=_COLORS["bg_white"],
        bordercolor=border_color,
        lightcolor=border_color,
        darkcolor=border_color,
        padding=8,
    )

    return name


def get_card_style(root: tk.Misc) -> str:
    """Frame style that looks like a contained card."""
    style = ttk.Style(root)
    style.configure(
        "Card.TFrame",
        background=_COLORS["bg_white"],
        relief="solid",
        borderwidth=1,
    )
    return "Card.TFrame"


def get_progress_style(root: tk.Misc, variant: str = "primary") -> str:
    """Progressbar style for a limited semantic color palette."""
    _validate_variant(variant, _PROGRESS_VARIANTS, "progress")
    style = ttk.Style(root)
    name = f"{variant.capitalize()}.Horizontal.TProgressbar"

    color = _COLORS.get(variant, _COLORS["primary"])
    style.configure(
        name,
        troughcolor=_COLORS["bg_gray_1"],
        background=color,
        thickness=8,
        borderwidth=0,
    )
    return name


def get_tab_style(root: tk.Misc) -> str:
    """Notebook tab styling."""
    style = ttk.Style(root)
    style.configure("TNotebook", background=_COLORS["bg_gray_1"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(12, 4), font=_BODY_FONT)
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", _COLORS["bg_white"]),
            ("!selected", _COLORS["bg_gray_1"]),
        ],
        foreground=[("selected", _COLORS["primary"])],
    )
    return "TNotebook"


def get_alert_style(root: tk.Misc, variant: str) -> str:
    """Style for alert and banner components."""
    _validate_variant(variant, _FEEDBACK_VARIANTS, "alert")
    style = ttk.Style(root)
    name = f"{variant.capitalize()}.Alert.TFrame"
    color = _COLORS.get(variant, _COLORS["info"])
    style.configure(name, background=color, relief="flat")
    return name


def get_sidebar_style(root: tk.Misc, active: bool = False) -> str:
    """Style for sidebar navigation links."""
    style = ttk.Style(root)
    name = "Active.Sidebar.TButton" if active else "Sidebar.TButton"
    bg = _COLORS["bg_gray_2"] if active else _COLORS["bg_white"]
    fg = _COLORS["primary"] if active else _COLORS["text_main"]

    style.configure(
        name,
        font=("Segoe UI", 10, "bold" if active else "normal"),
        background=bg,
        foreground=fg,
        anchor="w",
        padding=(20, 10),
        borderwidth=0,
    )

    return name


def get_tag_style(root: tk.Misc, variant: str = "primary") -> str:
    """Style for tags and badges."""
    _validate_variant(variant, _FEEDBACK_VARIANTS, "tag")
    style = ttk.Style(root)
    name = f"{variant.capitalize()}.Tag.TLabel"
    color = _COLORS.get(variant, _COLORS["primary"])

    style.configure(
        name,
        background=color,
        foreground=_COLORS["bg_white"],
        font=("Segoe UI", 8, "bold"),
        padding=(6, 2),
    )

    return name


def get_container_styles(root: tk.Misc):
    """Initialize structural styles for containers."""
    style = ttk.Style(root)

    # Card: background and border
    style.configure(
        "Card.TFrame",
        background=_COLORS["bg_white"],
        relief="solid",
        borderwidth=1,
    )

    # surface
    style.configure("Surface.TFrame", background=_COLORS["bg_gray_1"], relief="flat")

    # sidebar
    style.configure("Sidebar.TFrame", background=_COLORS["bg_gray_2"], relief="flat")

    # modal overlay
    style.configure("Modal.TFrame", background="#000000")

    return style
