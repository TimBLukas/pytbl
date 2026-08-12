"""button widgets for quick UI creation

provides small factory functions that wrap :mod:`tkinter.ttk`
button widgets with sensible defaults, so simple UIs can be assembled in
a few lines. Every factory:

* returns the created widget instead of packing/gridding it itself, so
  the caller stays in control of layout;
* accepts an optional ``style`` override in addition to the library's
  built-in variants;
* is annotated and documented following standard library conventions.

Example:
    >>> root = tk.Tk()
    >>> btn = create_button(root, "Save", on_save, variant=ButtonVariant.SUCCESS)
    >>> btn.pack(padx=8, pady=8)
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from enum import Enum
from typing import Callable, Dict, NamedTuple, Optional

from style import (
    get_danger_btn_style,
    get_default_btn_style,
    get_icon_btn_style,
    get_link_btn_style,
    get_outline_btn_style,
    get_success_btn_style,
    get_rounded_btn_style,
    get_circle_btn_style,
)

__all__ = [
    "ButtonVariant",
    "create_button",
    "create_link_button",
    "create_icon_button",
    "ToggleButton",
    "create_toggle_button",
]


class ButtonVariant(Enum):
    """Visual/semantic flavor of a standard button.

    Each maps to a style-generator function in :mod:`style`.
    Passing a variant to :func:`create_button` picks the matching style
    automatically, unless an explicit ``style`` override is given.
    """

    STANDARD = "standard"
    DANGER = "danger"
    SUCCESS = "success"
    OUTLINE = "outline"
    ROUNDED = "rounded"
    CIRCLE = "circle"


_VARIANT_STYLE_GETTERS: Dict[ButtonVariant, Callable[[tk.Misc], str]] = {
    ButtonVariant.STANDARD: get_default_btn_style,
    ButtonVariant.DANGER: get_danger_btn_style,
    ButtonVariant.SUCCESS: get_success_btn_style,
    ButtonVariant.OUTLINE: get_outline_btn_style,
    ButtonVariant.ROUNDED: get_rounded_btn_style,
    ButtonVariant.CIRCLE: get_circle_btn_style,
}


def _apply_dimensions(
    btn: ttk.Button, width: Optional[int], height: Optional[int]
) -> None:
    """Apply optional width/height hints to ``btn``.

    ``ttk.Button`` only exposes a native ``width`` option, measured in
    text units (characters) rather than pixels, and has no ``height``
    option at all. To still offer a ``height`` knob, it is approximated
    here as vertical padding applied to this widget instance only
    (overriding the style's padding just for this button). This is a
    deliberate approximation, not a pixel-perfect height, and resets the
    horizontal padding to a fixed default when used.

    Args:
        btn: The button to resize.
        width: Desired width in characters. ``None`` leaves it unset.
        height: Desired vertical padding in pixels, approximating a
            taller button. ``None`` leaves it unset.
    """
    if width is not None:
        btn.configure(width=width)
    if height is not None:
        btn.configure(padding=(12, height))


def create_button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None],
    *,
    variant: ButtonVariant = ButtonVariant.STANDARD,
    style: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    disabled: bool = False,
) -> ttk.Button:
    """Create a standard, ready-to-place button.

    This is the general-purpose entry point covering the common button
    variants (standard, danger, success, outline). For icon or toggle
    buttons, see :func:`create_icon_button` and :func:`create_toggle_button`.

    Args:
        parent: The parent widget the button will belong to.
        text: Label shown on the button.
        command: Callback invoked with no arguments when clicked.
        variant: Semantic style to apply. Ignored if ``style`` is given.
        style: Explicit ttk style name, overriding ``variant``.
        width: Optional width in characters.
        height: Optional approximate height in pixels (see notes on
            ``ttk.Button`` sizing in this module).
        disabled: If ``True``, the button starts in a disabled state.

    Returns:
        The created, unpacked :class:`ttk.Button`. Call ``.pack()``,
        ``.grid()`` or ``.place()`` on it to add it to the layout.
    """
    resolved_style = style or _VARIANT_STYLE_GETTERS[variant](parent)
    btn = ttk.Button(parent, text=text, style=resolved_style, command=command)
    _apply_dimensions(btn, width, height)
    if disabled:
        btn.state(["disabled"])
    return btn


def create_link_button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None],
    *,
    style: Optional[str] = None,
) -> ttk.Button:
    """Create a hyperlink-styled button (flat, underlined, no chrome).

    Useful for secondary or tertiary actions such as "Cancel" or
    "Learn more" links inside a form.

    Args:
        parent: The parent widget the button will belong to.
        text: Link label.
        command: Callback invoked with no arguments when clicked.
        style: Explicit ttk style name, overriding the library default.

    Returns:
        The created, unpacked :class:`ttk.Button`.
    """
    resolved_style = style or get_link_btn_style(parent)
    btn = ttk.Button(parent, text=text, style=resolved_style, command=command)
    btn.configure(cursor="hand2")
    return btn


def create_icon_button(
    parent: tk.Misc,
    image: tk.PhotoImage,
    command: Callable[[], None],
    *,
    text: Optional[str] = None,
    compound: str = "left",
    style: Optional[str] = None,
) -> ttk.Button:
    """Create a button showing an icon, optionally next to a text label.

    Args:
        parent: The parent widget the button will belong to.
        image: A pre-loaded :class:`tkinter.PhotoImage` (or subclass,
            e.g. ``PIL.ImageTk.PhotoImage``). The caller is responsible
            for loading it.
        command: Callback invoked with no arguments when clicked.
        text: Optional label shown alongside the icon. If ``None``, the
            button is icon-only.
        compound: Placement of the icon relative to the text (``"left"``,
            ``"right"``, ``"top"``, ``"bottom"``); ignored if ``text`` is
            ``None``.
        style: Explicit ttk style name, overriding the library default.

    Returns:
        The created, unpacked :class:`ttk.Button`.

    Note:
        Tkinter does not keep its own reference to ``image``; if nothing
        else holds one, it is garbage-collected and the button silently
        shows a blank icon. This function stores it on ``btn.image`` to
        keep it alive for as long as the button exists -- a well-known
        Tkinter idiom, not a design choice specific to this library.
    """
    resolved_style = style or get_icon_btn_style(parent)
    kwargs: Dict[str, object] = {
        "image": image,
        "command": command,
        "style": resolved_style,
    }
    if text is not None:
        kwargs.update(text=text, compound=compound)
    btn = ttk.Button(parent, **kwargs)
    btn.image = image  # type: ignore[attr-defined]  # keep alive, see Note above.
    return btn


class ToggleButton(NamedTuple):
    """Handle returned by :func:`create_toggle_button`.

    Bundles the widget together with the boolean state backing it, since
    callers typically need to read or observe the state in addition to
    placing the widget.

    Attributes:
        widget: The underlying button.
        is_on: Boolean variable tracking the toggle's current state.
    """

    widget: ttk.Button
    is_on: tk.BooleanVar


def create_toggle_button(
    parent: tk.Misc,
    text_on: str,
    text_off: str,
    *,
    initial: bool = False,
    on_toggle: Optional[Callable[[bool], None]] = None,
    style: Optional[str] = None,
) -> ToggleButton:
    """Create a two-state button that flips between "on" and "off".

    Args:
        parent: The parent widget the button will belong to.
        text_on: Label shown while the toggle is on.
        text_off: Label shown while the toggle is off.
        initial: Starting state.
        on_toggle: Optional callback invoked with the new boolean state
            every time the button is clicked.
        style: Explicit ttk style name, overriding the library default.

    Returns:
        A :class:`ToggleButton` bundling the widget and its state
        variable, e.g. ``toggle.widget.pack(); toggle.is_on.get()``.
    """
    resolved_style = style or get_default_btn_style(parent)
    is_on = tk.BooleanVar(parent, value=initial)

    def _handle_click() -> None:
        is_on.set(not is_on.get())
        btn.configure(text=text_on if is_on.get() else text_off)
        if on_toggle is not None:
            on_toggle(is_on.get())

    btn = ttk.Button(
        parent,
        text=text_on if initial else text_off,
        style=resolved_style,
        command=_handle_click,
    )
    return ToggleButton(widget=btn, is_on=is_on)


def create_circle_button(
    parent: tk.Misc,
    text: Optional[str],
    image: Optional[tk.PhotoImage],
    command: Callable[[], None],
    *,
    radius: int = 40,
    style: Optional[str] = None,
) -> ttk.Button:
    """Create a circular button, e.g. for icons

    Args:
    radius: The diameter/size of the button in pixels,
    """
    resolved_style = style or get_circle_btn_style(parent)
    btn = ttk.Button(parent, image=image, command=command, style=resolved_style)
    if image:
        btn.configure(image=image)

    if text:
        btn.configure(text=text)

    # To keep it circular, enforce height and width to be equal
    btn.configure(width=1)
    btn.configure(padding=radius // 4)
    return btn


def _demo() -> None:
    """Small manual smoke test; not part of the public API."""
    root = tk.Tk()
    root.title("Button library demo")

    create_button(
        root, "Save", lambda: print("Saved"), variant=ButtonVariant.SUCCESS
    ).pack(padx=8, pady=4, fill="x")

    create_button(
        root, "Delete", lambda: print("Deleted"), variant=ButtonVariant.DANGER
    ).pack(padx=8, pady=4, fill="x")

    create_button(
        root, "More info", lambda: print("Info"), variant=ButtonVariant.OUTLINE
    ).pack(padx=8, pady=4, fill="x")

    create_link_button(root, "Cancel", lambda: print("Cancelled")).pack(pady=4)

    toggle = create_toggle_button(
        root, "Enabled", "Disabled", on_toggle=lambda state: print("Toggled:", state)
    )
    toggle.widget.pack(padx=8, pady=4, fill="x")

    round = create_button(
        root,
        "Round",
        lambda: print("Round button"),
        variant=ButtonVariant.ROUNDED,
    ).pack(padx=8, pady=4, fill="x")

    root.mainloop()


if __name__ == "__main__":
    _demo()
