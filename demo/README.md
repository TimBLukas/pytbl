# pytbl demo project

This folder contains a small application that demonstrates how `pytbl` modules
work together in a realistic workflow.

## What the demo does

The application:

- reads task data from JSON,
- loads configuration from file and environment variables,
- creates a reusable CLI interface,
- calculates summary metrics with `maths`,
- rewrites titles with `textx.slugify`,
- renders a Markdown report with `reporting`,
- writes output to disk with `filetypes.jsonx`,
- optionally opens a Tkinter dashboard with `ui`,
- logs activity through the repository's `logging` helpers.

## Project layout

- `app.py` – main CLI + dashboard logic
- `__main__.py` – lets you run `python -m demo`
- `data/demo_data.json` – sample task data
- `tests/test_demo_app.py` – example coverage for the demo logic

## Run it

From the repository root:

```bash
python -m demo --config demo/config.example.json --input demo/data/demo_data.json --output demo/output/report.md --title "Project Pulse" --show-ui
```

You can also invoke the app entry point directly:

```bash
python demo/app.py --input demo/data/demo_data.json --output demo/output/report.md
```

## Demo workflow

1. Ensure the input JSON exists or let `ensure_demo_data` create it.
2. Load configuration from a file or environment variables.
3. Parse the CLI arguments with `cli.CliApp`.
4. Build a report with `reporting.Report` and `Table` components.
5. Save the report as Markdown and, optionally, show the dashboard UI.

## Modules used in the demo

- `cli` – argument parsing and prompt helpers
- `ui` – Tkinter dashboard cards and buttons
- `textx` – slug generation and wrapping
- `maths` – mean, median, and standard deviation
- `filetypes.jsonx` – JSON persistence
- `filetypes.envx` – environment overrides and config precedence
- `logging` – structured logger usage
- `reporting` – report composition and markdown rendering

## Development notes

This is intentionally small and educational: it demonstrates the style of using
several `pytbl` modules together rather than trying to be a production-ready
application framework.
