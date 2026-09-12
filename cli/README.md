# `cli`

Reusable command-line scaffolding for applications using `pytbl`.

This package provides a small, opinionated layer on top of Python's standard
`argparse` so you can build CLI tools with structured arguments, colored output,
progress indicators, config loading, and interactive prompts without repeating
boilerplate.

## Quick example

```python
from cli import CliApp, Command, ArgumentSpec, colorize, confirm, load_config

app = CliApp("demo", "A tiny example CLI")
app.add_common_arguments()

count_arg = ArgumentSpec(
    name="count",
    flags=("--count",),
    kind="int",
    default=1,
    help="Number of times to repeat the action.",
)
app.add_argument("--count", type=int, default=1, help="Number of times to repeat the action.")

config = load_config("config.json", defaults={"verbose": False})
print(colorize("Ready", fg="green", bold=True))
print(confirm("Continue?", default=True))
```

## Modules

- `parser.py`: argument definitions and `CliApp` wrappers around `argparse`
- `colors.py`: ANSI color helpers with automatic terminal detection
- `progress.py`: simple progress bar utilities
- `config.py`: config-file loading plus env and CLI precedence helpers
- `prompt.py`: interactive prompts, confirmations, and choice selection

## Typical usage

```python
from cli import ArgumentSpec, CliApp, ProgressBar, prompt, prompt_choice

app = CliApp("demo", description="Example CLI")
app.add_argument("--name", default="world", help="Name to greet")

options = app.parse_args(["--name", "friend"])
print(f"Hello, {options.name}!")

with ProgressBar(total=3, prefix="Processing: ") as progress:
    for step in range(1, 4):
        progress.update(step)

choice = prompt_choice("Select environment", ["dev", "staging", "prod"], default="dev")
print(choice)
```
