"""Reusable parser scaffolding for CLI applications."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional, Sequence


@dataclass
class ArgumentSpec:
    """Describe a single CLI argument in a structured way."""

    name: str
    flags: Sequence[str] = field(default_factory=tuple)
    help: str = ""
    kind: str = "str"
    default: Any = None
    required: bool = False
    choices: Optional[Sequence[str]] = None
    metavar: Optional[str] = None
    nargs: Optional[str | int] = None
    env_var: Optional[str] = None
    action: Optional[str] = None

    def to_argparse_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "help": self.help,
            "default": self.default,
            "required": self.required,
        }
        if self.action is not None:
            kwargs["action"] = self.action
        if self.choices is not None:
            kwargs["choices"] = list(self.choices)
        if self.metavar is not None:
            kwargs["metavar"] = self.metavar
        if self.nargs is not None:
            kwargs["nargs"] = self.nargs
        if self.kind != "str" and self.action is None:
            kwargs["type"] = self._type_for_kind()
        return kwargs

    def _type_for_kind(self):
        mapping = {
            "int": int,
            "float": float,
            "bool": lambda value: value.lower() in {"1", "true", "yes", "on"},
            "path": str,
            "str": str,
        }
        return mapping.get(self.kind, str)


@dataclass
class Command:
    """Describe a subcommand and its handler."""

    name: str
    description: str = ""
    arguments: Sequence[ArgumentSpec] = field(default_factory=tuple)
    handler: Optional[Callable[..., Any]] = None


class CliApp:
    """Thin wrapper around argparse that makes command definitions easier to reuse."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self.parser = argparse.ArgumentParser(prog=name, description=description)
        self.command_map: dict[str, Command] = {}
        self._command_parser = None

    def add_argument(self, *flags: str, **kwargs: Any) -> None:
        self.parser.add_argument(*flags, **kwargs)

    def add_common_arguments(self, *, config: bool = True, verbose: bool = True, quiet: bool = False) -> None:
        if config:
            self.add_argument("--config", help="Path to a JSON, INI, TOML, or YAML config file.")
        if verbose:
            self.add_argument("--verbose", action="store_true", help="Enable verbose logging output.")
        if quiet:
            self.add_argument("--quiet", action="store_true", help="Suppress non-essential output.")

    def add_command(self, command: Command) -> None:
        self.command_map[command.name] = command
        if self._command_parser is None:
            self._command_parser = self.parser.add_subparsers(dest="command")
        subparser = self._command_parser.add_parser(command.name, help=command.description, description=command.description)
        for argument in command.arguments:
            flags = tuple(argument.flags) or (f"--{argument.name}",)
            subparser.add_argument(*flags, **argument.to_argparse_kwargs())
        if command.handler is not None:
            subparser.set_defaults(_handler=command.handler)

    def parse_args(self, argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
        return self.parser.parse_args(argv)

    def run(self, argv: Optional[Sequence[str]] = None) -> Any:
        parsed = self.parse_args(argv)
        handler = getattr(parsed, "_handler", None)
        if handler is None:
            self.parser.print_help()
            return None
        return handler(parsed)


def build_parser(
    name: str,
    description: str = "",
    arguments: Optional[Iterable[ArgumentSpec]] = None,
) -> argparse.ArgumentParser:
    """Create an argparse parser for a simple CLI with reusable argument metadata."""

    parser = argparse.ArgumentParser(prog=name, description=description)
    for argument in arguments or ():
        flags = tuple(argument.flags) or (f"--{argument.name}",)
        parser.add_argument(*flags, **argument.to_argparse_kwargs())
    return parser


def add_common_arguments(parser: argparse.ArgumentParser, **kwargs: Any) -> None:
    """Attach common CLI flags to an argparse parser."""

    parser.add_argument("--config", help=kwargs.get("config_help", "Path to a config file."))
    parser.add_argument("--verbose", action="store_true", help=kwargs.get("verbose_help", "Enable verbose output."))
    parser.add_argument("--quiet", action="store_true", help=kwargs.get("quiet_help", "Suppress non-essential output."))
