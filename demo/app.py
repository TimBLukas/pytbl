"""Sample application that demonstrates many pytbl modules in one place."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from cli import CliApp, colorize, load_config, prompt_choice
from filetypes.envx import get_bool, temporary
from filetypes.jsonx import read_json, write_json
from logging import get_logger
from maths import mean, median, stddev
from reporting import Heading, Paragraph, Report, Table, render_to_string
from textx import slugify, wrap_text
from ui import (
    create_alert,
    create_badge,
    create_button,
    create_card,
    create_data_row,
    create_header,
    create_stat_card,
    create_status_bar,
)

try:  # pragma: no cover - UI is optional in headless runs.
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # pragma: no cover
    tk = None
    ttk = None

logger = get_logger("demo.app", console_output=False)

DEFAULT_DATA = [
    {"title": "Data cleanup", "category": "ops", "score": 82},
    {"title": "API review", "category": "engineering", "score": 91},
    {"title": "Customer onboarding", "category": "support", "score": 74},
    {"title": "Release checklist", "category": "ops", "score": 88},
    {"title": "Docs refresh", "category": "content", "score": 69},
    {"title": "Dashboard polish", "category": "design", "score": 94},
]


def build_demo_data() -> list[dict[str, Any]]:
    """Return a realistic dataset for the demo project."""

    return [dict(item) for item in DEFAULT_DATA]


def ensure_demo_data(path: str | os.PathLike[str]) -> list[dict[str, Any]]:
    """Create sample JSON data when the file does not yet exist."""

    file_path = Path(path)
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(file_path, build_demo_data())
        logger.info("Created demo data at %s", file_path)
    data = read_json(file_path)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of task records in {file_path!s}")
    return data


def summarise_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary values used in the demo UI and report."""

    rows = list(records)
    scores = [float(row["score"]) for row in rows]
    highest = max(rows, key=lambda row: row["score"])
    categories = {}
    for row in rows:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
    top_category = max(categories.items(), key=lambda item: item[1])[0]
    return {
        "count": len(rows),
        "average_score": round(mean(scores), 2),
        "median_score": round(median(scores), 2),
        "stddev_score": round(stddev(scores), 2),
        "top_category": top_category,
        "best_title": highest["title"],
        "slugged_titles": [slugify(row["title"]) for row in rows],
        "summary_sentence": wrap_text(
            f"The team reviewed {len(rows)} items with an average score of {round(mean(scores), 2)}.",
            width=72,
        ),
    }


def build_report(
    title: str, records: Iterable[dict[str, Any]], summary: dict[str, Any]
) -> Report:
    """Assemble a markdown-ready report with summary metrics and task details."""

    rows = [
        (row["title"], row["category"], row["score"], slugify(row["title"]))
        for row in records
    ]
    report = Report(
        title=title,
        components=[
            Heading(title, level=1),
            Paragraph(summary["summary_sentence"]),
            Table(
                headers=("Title", "Category", "Score", "Slug"),
                rows=tuple(rows),
            ),
            Heading("Key metrics", level=2),
            Table(
                headers=("Metric", "Value"),
                rows=(
                    ("Items reviewed", summary["count"]),
                    ("Average score", summary["average_score"]),
                    ("Median score", summary["median_score"]),
                    ("Std. dev.", summary["stddev_score"]),
                    ("Top category", summary["top_category"]),
                    ("Best item", summary["best_title"]),
                ),
            ),
        ],
    )
    return report


def build_demo_cli() -> CliApp:
    """Create the CLI interface for the demo project."""

    app = CliApp(
        "pytbl-demo", description="A mini app that ties together pytbl modules."
    )
    app.add_common_arguments(config=True, verbose=True, quiet=True)
    app.add_argument(
        "--input",
        default="demo/data/demo_data.json",
        help="JSON file with task records.",
    )
    app.add_argument(
        "--output",
        default="demo/output/report.md",
        help="Path to the generated markdown report.",
    )
    app.add_argument(
        "--title", default="Project Pulse", help="Title used in the generated report."
    )
    app.add_argument(
        "--show-ui",
        action="store_true",
        help="Open the Tkinter dashboard after generating the report.",
    )
    return app


def launch_dashboard(summary: dict[str, Any]) -> None:
    """Open a more polished Tkinter dashboard showing the key metrics."""

    if tk is None or ttk is None:
        logger.warning(
            "Tkinter is unavailable in this environment; skipping dashboard launch."
        )
        return

    root = tk.Tk()
    root.title("pytbl demo dashboard")
    root.geometry("860x560")
    root.minsize(720, 500)
    root.configure(bg="#f3f5f9")

    shell = create_card(root, padding=24)
    shell.pack(fill="both", expand=True, padx=18, pady=18)
    shell.configure(padding=20)

    header = ttk.Frame(shell)
    header.pack(fill="x", pady=(0, 16))
    create_badge(header, "LIVE").pack(side="left", padx=(0, 10))
    create_header(header, "Project Pulse", level=1).pack(side="left")

    status = create_status_bar(shell, "All systems healthy")
    status.pack(fill="x", pady=(0, 14))

    alert = create_alert(
        shell,
        "Delivery score is above target for this review cycle.",
        variant="success",
    )
    alert.pack(fill="x", pady=(0, 16))

    metrics = ttk.Frame(shell)
    metrics.pack(fill="x", pady=(0, 16))
    metric_cards = [
        ("Reviewed", str(summary["count"]), "+12%"),
        ("Average", f"{summary['average_score']:.2f}", "+4.2%"),
        ("Median", f"{summary['median_score']:.2f}", "+2.1%"),
        ("Top category", summary["top_category"], "active"),
    ]
    for index, (label, value, trend) in enumerate(metric_cards):
        card = create_card(metrics)
        card.pack(side="left", fill="x", expand=True, padx=(0 if index == 0 else 8, 0))
        create_stat_card(card, label, value, trend).pack(fill="x")

    lower = ttk.Frame(shell)
    lower.pack(fill="both", expand=True)

    left = create_card(lower)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))
    create_header(left, "Highlights", level=2).pack(anchor="w", pady=(0, 12))
    for title, subtitle in [
        ("Best item", summary["best_title"]),
        ("Category focus", summary["top_category"]),
        ("Average score", f"{summary['average_score']:.2f}"),
    ]:
        create_data_row(left, title, subtitle).pack(anchor="w", fill="x")

    right = create_card(lower)
    right.pack(side="right", fill="both", expand=True)
    create_header(right, "Recent work", level=2).pack(anchor="w", pady=(0, 12))
    for item in [
        "Data cleanup",
        "API review",
        "Dashboard polish",
        "Release checklist",
    ]:
        create_data_row(right, item, "completed").pack(anchor="w", fill="x")

    button_row = ttk.Frame(shell)
    button_row.pack(fill="x", pady=(16, 0))
    create_button(button_row, "Close", command=root.destroy, width=12).pack(
        side="right"
    )

    root.mainloop()


def run(argv: list[str] | None = None) -> int:
    """Execute the demo app as a mini CLI workflow."""

    app = build_demo_cli()
    options = app.parse_args(argv)

    config = load_config(
        options.config,
        defaults={"title": options.title, "show_ui": bool(options.show_ui)},
        env_prefix="PYTBL_DEMO_",
    )
    resolved_title = config.get("title", options.title)
    show_ui = bool(config.get("show_ui", options.show_ui)) or bool(options.show_ui)

    with temporary({"PYTBL_DEMO_MODE": "true"}):
        demo_mode = get_bool("PYTBL_DEMO_MODE")
        logger.info("Demo mode active: %s", demo_mode)

    records = ensure_demo_data(options.input)
    summary = summarise_records(records)
    report = build_report(resolved_title, records, summary)
    rendered = render_to_string(report, format="markdown")

    output_path = Path(options.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")

    print(colorize(f"Report generated: {output_path}", fg="green", bold=True))
    print(
        colorize(f"Average score: {summary['average_score']:.2f}", fg="cyan", bold=True)
    )

    env_choice = prompt_choice(
        "Select the environment used for the release note",
        ["dev", "staging", "prod"],
        default="staging",
    )
    print(colorize(f"Selected environment: {env_choice}", fg="yellow", bold=True))

    if show_ui:
        launch_dashboard(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
