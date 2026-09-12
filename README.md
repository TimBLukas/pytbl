# pytbl

`pytbl` is a small collection of reusable Python helpers for file formats,
text processing, mathematics, HTTP clients, reporting, logging, Tkinter UI
components, and type aliases.

The library favors small, composable functions and standard-library types.

## Documentation map

- [README](README.md): overview, package map, installation, and project-level guidance.
- [USAGE.md](USAGE.md): practical examples and how-to recipes for the supported modules.
- Each package also has its own README for module-specific details.

Install it from a checkout with:

```bash
python -m pip install -e .
```

## Quick start

```python
from pathlib import Path

from filetypes.jsonx import read_json, write_json
from textx import slugify

path = Path("data.json")
write_json(path, {"title": "A useful example", "items": [1, 2, 3]})
data = read_json(path)
print(slugify(data["title"]))  # a-useful-example
```

## Package map

| Package | Purpose |
| --- | --- |
| `datatypes` | Reusable type aliases such as `PathLike`, `JsonValue`, and `Headers`. |
| `cli` | CLI scaffolding for argument parsing, colored output, progress bars, config resolution, and prompts. |
| `demo` | A working mini application that combines the library's modules in one workflow. |
| `filetypes.jsonx` | JSON reading, writing, validation, formatting, and conversion. |
| `filetypes.yamlx` | YAML reading, writing, merging, templating, and conversion. |
| `filetypes.xmlx` | XML parsing, creation, querying, editing, and validation. |
| `filetypes.htmlx` | HTML parsing, extraction, generation, and updates. |
| `filetypes.inix` | INI parsing, editing, flattening, and conversion. |
| `filetypes.envx` | Environment variables, `.env` files, typed access, validation, and redaction. |
| `maths` | Number theory, statistics, algebra, geometry, simulation, and matrix I/O. |
| `textx` | Case conversion, slugs, wrapping, and lightweight tokenizers. |
| `http` | A configurable `requests` client with retries and typed responses. |
| `reporting` | Format-neutral documents rendered to Markdown, HTML, or Mermaid. |
| `logging` | Cached logger configuration, rotation, and call tracing. |
| `ui` | Tkinter/ttk buttons, widgets, containers, and styles. |

Each package has a README with its public purpose and examples. The
[USAGE guide](USAGE.md) covers installation guidance, dependency notes, and
cross-package examples, while this README focuses on the project overview and
package map.

## Optional dependencies

Install the dependencies needed by the features you use:

```bash
python -m pip install pyyaml          # YAML and YAML conversions
python -m pip install beautifulsoup4  # HTML parsing and updates
python -m pip install lxml            # advanced XPath and XSD validation
python -m pip install requests        # HTTP client
python -m pip install jinja2          # YAML templates
```

`pytest` is used by the repository's test suite. Tkinter is provided by most
Python distributions as an operating-system package rather than a PyPI
dependency.

## Development

Run the tests from the repository root:

```bash
python -m pytest
```

The project is licensed under GPL-3.0-or-later. See `LICENSE`.
