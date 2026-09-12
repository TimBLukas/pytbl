# Using pytbl

This file describes the imports `pytbl` supports and the conventions shared by the library.
It is assumed you are running Python 3.10 or newer, there is no guaranteed compatibility
for older python versions.

## Documentation map

- [README](README.md): project overview, package list, and repository-level context.
- [USAGE.md](USAGE.md): practical examples and module-by-module usage guidance.
- Browse the package directories for module-specific READMEs when you need focused API details.

## Installation

From a checkout:

```bash
python -m pip install -e .
```

For a regular install, replace `-e .` with `.`. Keep project dependencies
isolated in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install .
```

Optional integrations are intentionally imported by the modules that need
them.
You can choose to install all of these external dependencies or only the ones
needed for your specific purpose.

| Feature                           | Dependency       |
| --------------------------------- | ---------------- |
| YAML read/write and conversion    | `pyyaml`         |
| YAML templates                    | `jinja2`         |
| HTML parsing and updates          | `beautifulsoup4` |
| Advanced XPath and XSD validation | `lxml`           |
| HTTP client                       | `requests`       |

See the [README](README.md) for the overall package map and a quick start.

## CLI helpers

The `cli` package provides a small reusable layer on top of `argparse`.
It helps standardize argument declarations, colored output, progress indicators,
config discovery, and interactive prompts across projects.

```python
from cli import ArgumentSpec, CliApp, colorize, load_config, prompt_choice

app = CliApp("demo", description="Example CLI")
app.add_argument("--name", default="world", help="Name to greet")

config = load_config("settings.json", defaults={"verbose": False})
print(colorize("Ready", fg="green", bold=True))
print(prompt_choice("Choose an environment", ["dev", "prod"], default="dev"))
```

Use `ArgumentSpec` when you want to describe arguments in data form, and use
`CliApp` when you want a convenient, reusable parser object.

## Demo project

The repository also includes a mini application in [`demo/`](demo/README.md)
that combines several modules together in one workflow. It demonstrates CLI
parsing, UI widgets, environment/config handling, file IO, summary math,
report generation, and logging in a single example.

```bash
python -m demo --input demo/data/demo_data.json --output demo/output/report.md --title "Project Pulse"
```

See the [demo README](demo/README.md) for the full walkthrough and sample output.

## File helpers

Use `pathlib.Path` for paths and explicitly choose UTF-8 when working with
text.
File helpers return parsed Python values when reading and write
atomically by default where supported.

```python
from pathlib import Path

from filetypes.jsonx import read_json, write_json, prettify_json
from filetypes.inix import read_ini_as_dict

config = Path("config.json")
write_json(config, {"service": {"enabled": True}})
print(read_json(config)["service"]["enabled"])
print(prettify_json(config))

settings = read_ini_as_dict(Path("settings.ini"))
print(settings.get("database", {}).get("host", "localhost"))
```

The matching entry points are available from `filetypes.yamlx`, `filetypes.xmlx`,
and `filetypes.htmlx`. `filetypes.envx` reads process environment variables;
use `temporary({"DEBUG": "1"})` when an override must be scoped:

```python
from filetypes.envx import get_bool, temporary

with temporary({"DEBUG": "true"}):
    assert get_bool("DEBUG") is True
```

## Text and maths

```python
from maths import mean, primes_up_to
from textx import snake_case, slugify, wrap_text

assert snake_case("Release Candidate") == "release_candidate"
print(slugify("Café menu"))              # cafe-menu
print(wrap_text("A short paragraph.", width=10))
print(mean([2, 4, 6]))
print(primes_up_to(20))
```

Functions validate their inputs and raise `ValueError` or `TypeError` for
invalid data.
Check the package READMEs for specialized geometry, matrix,
statistics, and tokenizer examples.

- textx [README](textx/README.md)
- maths [README](maths/README.md)

## HTTP requests

`http.HttpClient` uses `requests` and returns `HttpResponse` objects. Set
timeouts and retry behavior explicitly for production services:

```python
from http import HttpClient, HttpClientConfig

client = HttpClient(
    "https://api.example.com",
    config=HttpClientConfig(timeout=10, max_retries=2),
)
response = client.get("/health")
print(response.status_code, response.json())
```

The client raises its package exceptions for transport failures and, by
default, unsuccessful HTTP status codes.
Catch the narrow exception types needed by your application rather than using a broad `except`.

For more details read the modules README file:

- http [README](http/README.md)

## Reports

Build a format-neutral report once and render it to Markdown or HTML:

```python
from reporting import Heading, Paragraph, Report, render_to_string

report = Report(
    title="Build report",
    components=[Heading("Summary", level=2), Paragraph("All checks passed.")],
)
markdown = render_to_string(report, format="markdown")
```

Use `write_report` or a renderer's `write` method to persist output.

For more details read the modules README file:

- reporting [README](reporting/README.md)

## Logging and UI

```python
from logging import get_logger

logger = get_logger("my-app")
logger.info("Application started")
```

The `ui` package contains Tkinter widgets and styles. Create a `tk.Tk` root,
pass it to the factory functions, and start `mainloop()` in an application
entry point.
UI creation requires a graphical display.

For more details read the modules README file:

- logging [README](logging/README.md)
- ui[README](ui/README.md)

## Testing and project conventions

Run the repository tests with:

```bash
python -m pytest
```

Prefer public package imports (`from textx import slugify`) over imports from
implementation files such as `textx.slugging`.
Use `Path` objects, type annotations, narrow exception handling, and context managers for resources.

For more details read the modules README file:

- testing [README](tests/README.md)
