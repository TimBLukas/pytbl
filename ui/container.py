"""container widgets for structure of the UI layout

provides layout components that manage the "skeleton" of an
application. E.g. scroll propagation, resizing logic, and child-widget
alignment.

Every factory:
* returns the container or a 'view' into the container's content area;
* follows the library's design system via :mod:`style`;
* implements complex event handling (scrolling, resizing) internally.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Callable, List, NamedTuple, Optional, Tuple

from .style import _COLORS, get_container_styles

__all__ = [
    "create_card",
    "create_scrollable_area",
    "create_sidebar",
    "create_collapsible_pane",
    "create_section",
    "create_button_group",
    "create_grid_container",
    "create_modal_overlay",
    "ButtonGroup",
    "ScrollableFrame",
    "CollapsiblePane",
    "ModalOverlay",
]

# Structural Containers
# ---------------------


def create_card(
    parent: tk.Misc, *, padding: int = 15, style: str = "Card.TFrame"
) -> ttk.Frame:
    """Create a white, elevated container.

    Args:
        parent: Parent widget.
        padding: Internal margin for content.
        style: Custom ttk style name.
    """
    get_container_styles(parent)
    return ttk.Frame(parent, style=style, padding=padding)


def create_sidebar(parent: tk.Misc, width: int = 250, padding: int = 10) -> ttk.Frame:
    """Create a fixed-width vertical container for navigation."""
    if width <= 0:
        raise ValueError("width must be greater than 0")
    get_container_styles(parent)
    frame = ttk.Frame(parent, style="Sidebar.TFrame", padding=padding, width=width)
    frame.pack_propagate(False)  # Maintain width regardless of children

    return frame


def create_section(parent: tk.Misc, title: str, *, padding: int = 10):
    """Create a titled container with a visual separator."""
    container = ttk.Frame(parent, padding=padding)

    header = ttk.Label(
        container,
        text=title.upper(),
        font=("Segoe UI", 9, "bold"),
        foreground=_COLORS["primary"],
    )
    header.pack(anchor="w", pady=(0, 2))

    sep = ttk.Separator(container, orient="horizontal")
    sep.pack(fill="x", pady=(0, 10))

    content = ttk.Frame(container)
    content.pack(fill="both", expand=True)

    return content  # Returns content area to the caller


# Layout & Scrolling
# ------------------


class ScrollableFrame(ttk.Frame):
    """A frame allowing vertical scrolling."""

    def __init__(self, parent: tk.Misc, padding: int = 10, **kwargs):
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0, bg=_COLORS["bg_white"])
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_content = ttk.Frame(
            self.canvas, padding=padding, style="Card.TFrame"
        )

        self.scrollable_content.bind(
            "<Configure>",
            lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.window_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_content, anchor="nw"
        )

        # Sync canvas with frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def create_scrollable_area(
    parent: tk.Misc, padding: int = 10
) -> Tuple[ttk.Frame, ScrollableFrame]:
    """Factory for :class:`ScrollableFrame`.

    Returns the inner content frame and the scrollable container so the
    caller can pack the container while adding children to the content
    frame.
    """
    container = ScrollableFrame(parent, padding=padding)
    return container.scrollable_content, container


# Interactive containers
# ----------------------


class CollapsiblePane(ttk.Frame):
    """A container that can be toggled open or closed."""

    def __init__(self, parent: tk.Misc, title: str, expanded: bool = True):
        super().__init__(parent)
        self._title = title
        self.is_expanded = expanded

        self.header = ttk.Button(
            self,
            text=self._header_text(),
            command=self.toggle,
            style="Outline.TButton",
        )

        self.header.pack(fill="x")

        self.content_area = ttk.Frame(self, padding=(15, 5))
        if expanded:
            self.content_area.pack(fill="x")

    def _header_text(self) -> str:
        return f"{'▼' if self.is_expanded else '▶'} {self._title}"

    def toggle(self) -> None:
        if self.is_expanded:
            self.content_area.pack_forget()
        else:
            self.content_area.pack(fill="x")
        self.is_expanded = not self.is_expanded
        self.header.configure(text=self._header_text())


def create_collapsible_pane(
    parent: tk.Misc, title: str, expanded: bool = True
) -> CollapsiblePane:
    """Create a toggleable accordion-style container."""
    return CollapsiblePane(parent, title, expanded)


class ButtonGroup(ttk.Frame):
    """Specialized frame for a group of buttons."""

    def __init__(
        self, parent: tk.Misc, alignment: str = "right", spacing: int = 8, **kwargs
    ):
        super().__init__(parent, **kwargs)
        if alignment not in {"left", "right", "top", "bottom"}:
            raise ValueError(
                "alignment must be one of 'left', 'right', 'top', or 'bottom'"
            )
        self._side = alignment
        self._spacing = spacing

    def add_button(self, btn: ttk.Button) -> None:
        """Add a button to the group and apply the layout."""
        btn.pack(in_=self, side=self._side, padx=self._spacing // 2)


def create_button_group(
    parent: tk.Misc, alignment: str = "right", spacing: int = 8
) -> ButtonGroup:
    """Create a button group for action buttons.

    Returns:
        A :class:`ButtonGroup` instance.
    """
    return ButtonGroup(parent, alignment=alignment, spacing=spacing)


def create_grid_container(
    parent: tk.Misc, columns: int = 2, padding: int = 10
) -> ttk.Frame:
    """Create a frame configured with uniform column weights.

    Useful for dashboard grids or two-column forms.
    """
    if columns <= 0:
        raise ValueError("columns must be greater than 0")

    frame = ttk.Frame(parent, padding=padding)
    for i in range(columns):
        frame.columnconfigure(i, weight=1, uniform="group1")
    return frame


# Adv. Overlays
# -------------


class ModalOverlay(tk.Frame):
    """A full-window overlay to emphasize a dialog."""

    def __init__(self, root: tk.Tk):
        super().__init__(root, bg="#000000")
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.configure(bg="#212529")  # Dark surface

        self.card = create_card(self, padding=30)
        self.content_area = self.card
        self.card.place(relx=0.5, rely=0.5, anchor="center")


def create_modal_overlay(root: tk.Tk) -> ModalOverlay:
    """Create a full-screen overlay and return the overlay widget."""
    return ModalOverlay(root)


def _demo():
    from . import buttons, widgets

    root = tk.Tk()
    root.title("Modern Dashboard")
    root.geometry("1000x700")

    # IMPORTANT: Force a theme that supports custom colors
    style_engine = ttk.Style()
    if "clam" in style_engine.theme_names():
        style_engine.theme_use("clam")

    # 1. Sidebar (Left)
    sidebar = create_sidebar(root, width=200)
    sidebar.pack(side="left", fill="y")  # No expand=True here, we want fixed width

    widgets.create_header(sidebar, "Navigation").pack(pady=20)
    widgets.create_sidebar_link(sidebar, "Dashboard", active=True).pack(fill="x")
    widgets.create_sidebar_link(sidebar, "Analytics").pack(fill="x")

    # 2. Main Content Area (Right)
    # We get BOTH the area to put stuff in, and the container to pack.
    inner_content, scroll_container = create_scrollable_area(root, padding=30)

    # Pack the CONTAINER, not the inner part.
    scroll_container.pack(side="left", fill="both", expand=True)

    # 3. Top Row: Header + Buttons
    top_row = ttk.Frame(inner_content)
    top_row.pack(fill="x", pady=(0, 20))

    widgets.create_header(top_row, "System Overview", level=1).pack(side="left")

    # Button Group
    actions = create_button_group(top_row, alignment="right")
    actions.pack(side="right")

    # Adding actual visible buttons
    btn_save = buttons.create_button(
        actions,
        "Save Report",
        lambda: print("Saved!"),
        variant=buttons.ButtonVariant.SUCCESS,
    )
    actions.add_button(btn_save)

    btn_ref = buttons.create_button(
        actions,
        "Refresh",
        lambda: print("Refreshed!"),
        variant=buttons.ButtonVariant.OUTLINE,
    )
    actions.add_button(btn_ref)

    # 4. Grid of Cards
    grid = create_grid_container(inner_content, columns=2)
    grid.pack(fill="x")

    # Card 1
    c1 = create_card(grid)
    c1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    widgets.create_header(c1, "Live Statistics", level=2).pack(anchor="w")
    widgets.create_data_row(c1, "Server Load", "24%", "🔥").pack(fill="x")

    # Card 2
    c2 = create_card(grid)
    c2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    widgets.create_header(c2, "User Activity", level=2).pack(anchor="w")
    widgets.create_progress_bar(c2, variant="primary").pack(fill="x", pady=10)
    widgets.create_muted_text(c2, "78% of target reached").pack()

    # 5. Collapsible section at the bottom
    settings = create_collapsible_pane(
        inner_content, "Advanced Settings", expanded=False
    )
    settings.pack(fill="x", pady=20)
    widgets.create_input_field(settings.content_area, placeholder="Enter License Key...").pack(
        fill="x"
    )

    root.mainloop()


if __name__ == "__main__":
    _demo()
