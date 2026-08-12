"""UI widgets for application assembly

provides factory functions and high-level components that wrap :mod:`tkinter`
and :mod:`tkinter.ttk`.
This module allows interfaces to be constructed with minimal boilerplate by
providing defaults for typography, inputs, and feedback elements.

Every factory and component:

* returns the created widget instead of packing/gridding it itself, so
  the caller stays in control of layout;
* leverages a centralized design system in :mod:`style` while allowing
  explicit ``style`` overrides;
* simplifies state management (e.g., bundling variables with checkboxes
  or managing internal switch logic);
* is annotated and documented following standard library conventions.

Example:
    >>> root = tk.Tk()
    >>> # Assemble a quick login card
    >>> card = create_card(root)
    >>> card.pack(padx=20, pady=20)
    >>> create_header(card, "Login", level=2).pack(pady=5)
    >>> user = create_input_field(card, placeholder="Username")
    >>> user.pack(fill="x", pady=5)
    >>> Switch(card, command=on_toggle).pack(pady=10)
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Any, Tuple, NamedTuple, Dict

from style import (
    get_label_style,
    get_entry_style,
    get_card_style,
    get_progress_style,
    get_tab_style,
    _COLORS,
    _BODY_FONT,
    get_tag_style,
    get_alert_style,
    get_sidebar_style,
)


def create_header(parent: tk.Misc, text: str, level: int = 1) -> ttk.Label:
    """Create a H1 or H2 header label."""
    variant = "h1" if level == 1 else "h2"
    style = get_label_style(parent, variant)
    return ttk.Label(parent, text=text, style=style)


def create_muted_text(parent: tk.Misc, text: str) -> ttk.Label:
    """Create small, de-emphasized text (e.g. help text or timestamps)."""
    return ttk.Label(parent, text=text, style=get_label_style(parent, "muted"))


def create_badge(parent: tk.Misc, text: str) -> ttk.Label:
    """Create a small pill-shaped tag with a background color."""
    return ttk.Label(parent, text=text.upper(), style=get_label_style(parent, "badge"))


def create_input_field(
    parent: tk.Misc, placeholder: str = "", password: bool = False, error: bool = False
) -> ttk.Entry:
    """Create a modern text entry field."""
    style = get_entry_style(parent, error=error)
    entry = ttk.Entry(parent, style=style, show="*" if password else "")
    if placeholder:
        entry.insert(0, placeholder)
        entry.bind(
            "<FocusIn>",
            lambda e: entry.delete(0, tk.END) if entry.get() == placeholder else None,
        )
    return entry


def create_number_spinner(
    parent: tk.Misc, from_: int, to: int, initial: int = 0
) -> ttk.Spinbox:
    """Create a numeric input with up/down arrows."""
    sb = ttk.Spinbox(parent, from_=from_, to=to)
    sb.set(initial)
    return sb


def create_dropdown(
    parent: tk.Misc, options: List[str], default: Optional[str] = None
) -> ttk.Combobox:
    """Create a read-only selection dropdown."""
    cb = ttk.Combobox(parent, values=options, state="readonly")
    if default:
        cb.set(default)
    elif options:
        cb.current(0)
    return cb


def create_checkbox(
    parent: tk.Misc, text: str, initial: bool = False
) -> Tuple[ttk.Checkbutton, tk.BooleanVar]:
    """Create a checkbox bundled with its boolean variable."""
    var = tk.BooleanVar(value=initial)
    chk = ttk.Checkbutton(parent, text=text, variable=var)
    return chk, var


def create_search_bar(parent: tk.Misc, on_search: Callable[[str], None]) -> ttk.Frame:
    """Create a composite search widget (Entry + Button)."""
    frame = ttk.Frame(parent)
    entry = create_input_field(frame, placeholder="Search...")
    entry.pack(side="left", fill="x", expand=True)

    # Using a simple button for the search action
    btn = ttk.Button(frame, text="🔍", width=3, command=lambda: on_search(entry.get()))
    btn.pack(side="right", padx=(4, 0))
    return frame


def create_progress_bar(
    parent: tk.Misc, mode: str = "determinate", variant: str = "primary"
) -> ttk.Progressbar:
    """
    Create a styled progress bar (primary, success, or danger),

    Raises.
        ValueError: if mode not in Literal['determinate', 'indeterminate']
    """
    style = get_progress_style(parent, variant)

    if mode not in ["determinate", "indeterminate"]:
        raise ValueError(
            "Invalid mode provided, mode needs to be Literal['determinate', 'indeterminate']"
        )
    return ttk.Progressbar(parent, mode=mode, style=style)


def create_separator(parent: tk.Misc, vertical: bool = False) -> ttk.Separator:
    """Create a visual divider line"""
    orient = "vertical" if vertical else "horizontal"
    return ttk.Separator(parent, orient=orient)


def create_status_bar(parent: tk.Misc, initial_text: str = "Ready") -> ttk.Label:
    """Create a thin bar typically placed at the bottom of a window."""
    lbl = ttk.Label(parent, text=initial_text, relief="sunken", anchor="w", padding=2)
    return lbl


def create_card(parent: tk.Misc, padding: int = 15) -> ttk.Frame:
    """Create a white background frame with a border for grouping content."""
    style = get_card_style(parent)
    frame = ttk.Frame(parent, style=style, padding=padding)
    return frame


def create_tab_container(parent: tk.Misc) -> ttk.Notebook:
    """Create a tabbed interface holder."""
    style = get_tab_style(parent)
    return ttk.Notebook(parent, style=style)


def create_scrollable_text(
    parent: tk.Misc, height: int = 5
) -> Tuple[tk.Text, ttk.Scrollbar]:
    """Create a multi-line text area with a scrollbar."""
    frame = ttk.Frame(parent)
    txt = tk.Text(frame, height=height, font=_BODY_FONT, relief="flat", padx=5, pady=5)
    scrolly = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=scrolly.set)

    txt.pack(side="left", fill="both", expand=True)
    scrolly.pack(side="right", fill="y")

    return frame, txt  # type: ignore


def create_stat_card(
    parent: tk.Misc, label: str, value: str, trend: str = ""
) -> ttk.Frame:
    card = ttk.Frame(parent, padding=15, style="Card.TFrame")
    ttk.Label(
        card, text=label, font=("Segoe UI", 10), foreground=_COLORS["text_muted"]
    ).pack(anchor="w")
    ttk.Label(card, text=value, font=("Segoe UI", 20, "bold")).pack(anchor="w")
    if trend:
        color = _COLORS["success"] if "+" in trend else _COLORS["danger"]
        ttk.Label(card, text=trend, font=("Segoe UI", 9), foreground=color).pack(
            anchor="w"
        )
    return card


def create_avatar(parent: tk.Misc, initials: str, size: int = 40) -> tk.Canvas:
    canvas = tk.Canvas(
        parent,
        width=size,
        height=size,
        bg=parent["bg"] if "bg" in parent.keys() else "#ffffff",
        highlightthickness=0,
    )
    canvas.create_oval(2, 2, size - 2, size - 2, fill=_COLORS["primary"], outline="")
    canvas.create_text(
        size // 2,
        size // 2,
        text=initials,
        fill="white",
        font=("Segoe UI", size // 3, "bold"),
    )
    return canvas


def create_alert(parent: tk.Misc, text: str, variant: str = "info") -> ttk.Frame:
    alert_style = get_alert_style(parent, variant)
    frame = ttk.Frame(parent, style=alert_style, padding=10)
    lbl = ttk.Label(
        frame, text=text, background=_COLORS.get(variant), foreground="white"
    )
    lbl.pack(side="left", padx=10)
    ttk.Button(frame, text="✕", width=2, command=frame.destroy).pack(side="right")
    return frame


class Switch(tk.Canvas):
    def __init__(self, parent, command: Callable[[bool], None] = None):
        super().__init__(
            parent, width=40, height=20, highlightthickness=0, cursor="hand2"
        )
        self.state = False
        self.command = command
        self.bind("<Button-1>", self._toggle)
        self._draw()

    def _draw(self):
        self.delete("all")
        color = _COLORS["success"] if self.state else _COLORS["border"]
        self.create_rounded_rect(2, 2, 38, 18, radius=10, fill=color, outline="")
        x = 22 if self.state else 2
        self.create_oval(x + 2, 4, x + 14, 16, fill="white", outline="")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1 + radius,
            y1,
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _toggle(self, event):
        self.state = not self.state
        self._draw()
        if self.command:
            self.command(self.state)


def create_data_row(
    parent: tk.Misc, title: str, subtitle: str, icon: str = "📄"
) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=10)
    ttk.Label(frame, text=icon, font=("Segoe UI", 16)).pack(side="left", padx=(0, 10))
    txt_container = ttk.Frame(frame)
    txt_container.pack(side="left")
    ttk.Label(txt_container, text=title, font=("Segoe UI", 10, "bold")).pack(anchor="w")
    ttk.Label(
        txt_container,
        text=subtitle,
        font=("Segoe UI", 9),
        foreground=_COLORS["text_muted"],
    ).pack(anchor="w")
    return frame


def create_metric_ring(parent: tk.Misc, percent: int, size: int = 60) -> tk.Canvas:
    canvas = tk.Canvas(parent, width=size, height=size, highlightthickness=0)
    extent = (percent / 100) * 359
    canvas.create_arc(
        5,
        5,
        size - 5,
        size - 5,
        start=90,
        extent=-359,
        outline=_COLORS["border"],
        width=5,
        style="arc",
    )
    canvas.create_arc(
        5,
        5,
        size - 5,
        size - 5,
        start=90,
        extent=-extent,
        outline=_COLORS["primary"],
        width=5,
        style="arc",
    )
    canvas.create_text(
        size // 2, size // 2, text=f"{percent}%", font=("Segoe UI", 8, "bold")
    )
    return canvas


def create_sidebar_link(
    parent: tk.Misc, text: str, active: bool = False, command=None
) -> ttk.Button:
    s = get_sidebar_style(parent, active)
    return ttk.Button(parent, text=text, style=s, command=command)


def create_step_indicator(parent: tk.Misc, steps: List[str], current: int) -> ttk.Frame:
    frame = ttk.Frame(parent)
    for i, step in enumerate(steps):
        color = _COLORS["primary"] if i <= current else _COLORS["border"]
        lbl = tk.Label(
            frame,
            text=str(i + 1),
            bg=color,
            fg="white",
            width=2,
            font=("Segoe UI", 8, "bold"),
        )
        lbl.pack(side="left")
        if i < len(steps) - 1:
            ttk.Separator(frame, orient="horizontal").pack(
                side="left", fill="x", expand=True, padx=5
            )
    return frame


class TagEntry(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tags: List[str] = []
        self.entry = ttk.Entry(self)
        self.entry.pack(side="right", fill="x", expand=True)
        self.entry.bind("<Return>", self._add_tag)
        self.container = ttk.Frame(self)
        self.container.pack(side="left")

    def _add_tag(self, event):
        val = self.entry.get().strip()
        if val and val not in self.tags:
            self.tags.append(val)
            tag_lbl = ttk.Label(
                self.container, text=val, style=get_tag_style(self, "info")
            )
            tag_lbl.pack(side="left", padx=2)
            tag_lbl.bind(
                "<Button-1>", lambda e: [tag_lbl.destroy(), self.tags.remove(val)]
            )
            self.entry.delete(0, tk.END)


class Accordion(ttk.Frame):
    def __init__(self, parent, title: str, content_func: Callable[[ttk.Frame], None]):
        super().__init__(parent)
        self.header = ttk.Button(self, text=f"▶ {title}", command=self._toggle)
        self.header.pack(fill="x")
        self.content_frame = ttk.Frame(self)
        content_func(self.content_frame)
        self.is_open = False

    def _toggle(self):
        if self.is_open:
            self.content_frame.pack_forget()
            self.header.configure(text=self.header.cget("text").replace("▼", "▶"))
        else:
            self.content_frame.pack(fill="x", pady=5)
            self.header.configure(text=self.header.cget("text").replace("▶", "▼"))
        self.is_open = not self.is_open


def create_empty_state(parent: tk.Misc, message: str) -> ttk.Frame:
    f = ttk.Frame(parent)
    ttk.Label(f, text="📂", font=("Segoe UI", 48)).pack()
    ttk.Label(
        f, text=message, font=("Segoe UI", 12), foreground=_COLORS["text_muted"]
    ).pack()
    return f


def create_segmented_control(
    parent: tk.Misc, options: List[str], callback
) -> ttk.Frame:
    f = ttk.Frame(parent)
    for opt in options:
        ttk.Button(f, text=opt, command=lambda o=opt: callback(o)).pack(side="left")
    return f


def show_toast(root: tk.Tk, message: str):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.geometry(f"+{root.winfo_x() + 20}+{root.winfo_y() + 20}")
    ttk.Label(
        toast, text=message, background="#333", foreground="white", padding=10
    ).pack()
    root.after(3000, toast.destroy)


def create_breadcrumbs(parent: tk.Misc, paths: List[str]) -> ttk.Frame:
    f = ttk.Frame(parent)
    for i, p in enumerate(paths):
        ttk.Label(f, text=p, foreground=_COLORS["primary"], cursor="hand2").pack(
            side="left"
        )
        if i < len(paths) - 1:
            ttk.Label(f, text=" / ", foreground=_COLORS["text_muted"]).pack(side="left")
    return f


def create_password_meter(parent: tk.Misc, entry: ttk.Entry) -> ttk.Progressbar:
    meter = ttk.Progressbar(parent, length=100)

    def check_strength(e):
        s = len(entry.get())
        meter["value"] = min(s * 10, 100)

    entry.bind("<KeyRelease>", check_strength)
    return meter


def create_loading_overlay(parent: tk.Frame) -> ttk.Frame:
    overlay = ttk.Frame(parent)
    ttk.Label(overlay, text="⌛ Loading...", font=("Segoe UI", 12, "bold")).place(
        relx=0.5, rely=0.5, anchor="center"
    )
    return overlay


def create_drop_zone(parent: tk.Misc) -> ttk.Frame:
    f = ttk.Frame(parent, padding=30, style="Card.TFrame")
    ttk.Label(f, text="<Drop Files>", font=("Segoe UI", 24)).pack()
    ttk.Label(f, text="Drag & Drop Files Here", font=("Segoe UI", 10)).pack()
    return f


def add_tooltip(widget: tk.Widget, text: str):
    def enter(event):
        global tooltip_window
        tooltip_window = tk.Toplevel(widget)
        tooltip_window.overrideredirect(True)
        tooltip_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tk.Label(
            tooltip_window, text=text, bg="#ffffca", relief="solid", borderwidth=1
        ).pack()

    def leave(event):
        if "tooltip_window" in globals():
            tooltip_window.destroy()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


class SearchHistory(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.entry = ttk.Combobox(self, values=["Recent search 1", "Recent search 2"])
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(self, text="🔍", width=3).pack(side="left")


def _demo():
    import buttons

    root = tk.Tk()
    root.title("UI Library Component Gallery")
    root.geometry("500x800")
    root.configure(bg=_COLORS["bg_gray_1"])

    s = ttk.Style()
    s.theme_use("clam")

    header_frame = ttk.Frame(root, padding=(20, 20, 20, 10))
    header_frame.pack(fill="x")
    create_header(header_frame, "Component Library", level=1).pack(side="left")
    create_avatar(header_frame, "JD", size=40).pack(side="right")

    # --- Main Tab Container ---
    tabs = create_tab_container(root)
    tabs.pack(fill="both", expand=True, padx=10, pady=10)

    def create_tab(name):
        frame = ttk.Frame(tabs, padding=15)
        tabs.add(frame, text=name)
        # Create scrollable area
        canvas = tk.Canvas(frame, bg=_COLORS["bg_white"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_content = ttk.Frame(canvas)

        scroll_content.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scroll_content

    # --- TAB 1: DASHBOARD & DATA ---
    tab_data = create_tab("Dashboard")

    create_header(tab_data, "System Metrics", level=2).pack(anchor="w", pady=(0, 10))

    stats_row = ttk.Frame(tab_data)
    stats_row.pack(fill="x", pady=10)
    create_stat_card(stats_row, "Revenue", "$12,400", "+12%").pack(
        side="left", fill="x", expand=True, padx=5
    )
    create_stat_card(stats_row, "Users", "1,240", "+5%").pack(
        side="left", fill="x", expand=True, padx=5
    )

    create_separator(tab_data).pack(fill="x", pady=15)

    create_header(tab_data, "Engagement", level=2).pack(anchor="w")
    ring_frame = ttk.Frame(tab_data)
    ring_frame.pack(pady=10)
    create_metric_ring(ring_frame, 75).pack(side="left", padx=20)
    create_metric_ring(ring_frame, 40).pack(side="left", padx=20)

    create_header(tab_data, "Recent Files", level=2).pack(anchor="w", pady=(20, 5))
    create_data_row(tab_data, "Report_Q3.pdf", "Updated 2h ago", "📄").pack(fill="x")
    create_data_row(tab_data, "Analytics.csv", "Updated 5h ago", "📊").pack(fill="x")

    # --- TAB 2: INPUTS & FORMS ---
    tab_inputs = create_tab("Inputs")

    create_header(tab_inputs, "Modern Controls", level=2).pack(anchor="w", pady=(0, 10))

    # Switch Control
    switch_row = ttk.Frame(tab_inputs)
    switch_row.pack(fill="x", pady=5)
    ttk.Label(switch_row, text="Dark Mode").pack(side="left")
    Switch(switch_row, command=lambda s: print(f"Switch: {s}")).pack(side="right")

    # Tag Entry
    ttk.Label(tab_inputs, text="Project Tags (Press Enter)").pack(
        anchor="w", pady=(15, 5)
    )
    TagEntry(tab_inputs).pack(fill="x", pady=5)

    # Password with Meter
    ttk.Label(tab_inputs, text="New Password").pack(anchor="w", pady=(15, 5))
    pw_input = create_input_field(tab_inputs, password=True)
    pw_input.pack(fill="x")
    create_password_meter(tab_inputs, pw_input).pack(fill="x", pady=5)

    # Segmented Control
    ttk.Label(tab_inputs, text="Priority Level").pack(anchor="w", pady=(15, 5))
    create_segmented_control(tab_inputs, ["Low", "Med", "High"], print).pack(fill="x")

    # Drop Zone
    ttk.Label(tab_inputs, text="Attachments").pack(anchor="w", pady=(15, 5))
    create_drop_zone(tab_inputs).pack(fill="x", pady=5)

    # --- TAB 3: NAVIGATION & FEEDBACK ---
    tab_nav = create_tab("Flow")

    # Breadcrumbs
    create_breadcrumbs(tab_nav, ["Settings", "Account", "Security"]).pack(
        anchor="w", pady=10
    )

    # Step Indicator
    create_step_indicator(tab_nav, ["Profile", "Billing", "Review"], current=1).pack(
        fill="x", pady=20
    )

    # Accordion
    def build_accordion_content(f):
        create_muted_text(
            f,
            "This is hidden content inside an accordion. Useful for FAQs or advanced settings.",
        ).pack(pady=5)

    Accordion(tab_nav, "Advanced Options", build_accordion_content).pack(
        fill="x", pady=10
    )

    # Alerts
    create_header(tab_nav, "Notifications", level=2).pack(anchor="w", pady=(20, 10))
    create_alert(
        tab_nav, "Your subscription expires in 3 days!", variant="warning"
    ).pack(fill="x", pady=5)
    create_alert(tab_nav, "Profile updated successfully.", variant="success").pack(
        fill="x", pady=5
    )

    buttons.create_button(
        tab_nav,
        "Show Toast Notification",
        lambda: show_toast(root, "Message Sent!"),
        variant=buttons.ButtonVariant.OUTLINE,
    ).pack(pady=20)

    # Empty State Example
    create_separator(tab_nav).pack(fill="x", pady=20)
    create_empty_state(tab_nav, "No archived messages found").pack(pady=20)

    # --- TAB 4: SIDEBAR & TOOLTIPS ---
    tab_misc = create_tab("Misc")

    create_header(tab_misc, "Sidebar Navigation", level=2).pack(
        anchor="w", pady=(0, 10)
    )
    sidebar_sim = ttk.Frame(tab_misc, style="Card.TFrame", padding=10)
    sidebar_sim.pack(fill="x")
    create_sidebar_link(sidebar_sim, "🏠 Dashboard", active=True).pack(fill="x")
    create_sidebar_link(sidebar_sim, "👤 Profile").pack(fill="x")
    create_sidebar_link(sidebar_sim, "⚙️ Settings").pack(fill="x")

    # Tooltip Demo
    create_header(tab_misc, "Interactive", level=2).pack(anchor="w", pady=(20, 10))
    info_btn = buttons.create_button(
        tab_misc, "Hover for Help", lambda: None, variant=buttons.ButtonVariant.STANDARD
    )
    info_btn.pack(pady=5)
    add_tooltip(info_btn, "This is a custom tooltip!")

    # Search with History
    ttk.Label(tab_misc, text="Search with History").pack(anchor="w", pady=(15, 5))
    SearchHistory(tab_misc).pack(fill="x")

    # Status Bar
    status = create_status_bar(root, "System Online")
    status.pack(side="bottom", fill="x")

    root.mainloop()


if __name__ == "__main__":
    _demo()
