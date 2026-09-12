"""Tests for the reusable CLI helper package."""

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli import (
    ArgumentSpec,
    CliApp,
    ProgressBar,
    build_parser,
    colorize,
    confirm,
    load_config,
    prompt,
    prompt_choice,
)


class TestCliParserHelpers(unittest.TestCase):
    def test_cli_app_argument_parsing(self) -> None:
        app = CliApp("demo")
        app.add_argument("--name", default="world")
        parsed = app.parse_args(["--name", "friend"])
        self.assertEqual(parsed.name, "friend")

    def test_build_parser_from_argument_specs(self) -> None:
        parser = build_parser(
            "demo",
            "Example parser",
            [
                ArgumentSpec(
                    name="count",
                    flags=("--count",),
                    kind="int",
                    default=1,
                    help="Repeat count.",
                )
            ],
        )
        parsed = parser.parse_args(["--count", "3"])
        self.assertEqual(parsed.count, 3)

    def test_command_registration_and_execution(self) -> None:
        def greet(args):
            return f"hello {args.name}"

        app = CliApp("demo")
        app.add_command(
            __import__("cli.parser", fromlist=["Command"]).Command(
                name="greet",
                description="Greet the user",
                arguments=(ArgumentSpec(name="name", flags=("--name",), default="world"),),
                handler=greet,
            )
        )
        result = app.run(["greet", "--name", "friend"])
        self.assertEqual(result, "hello friend")


class TestCliUtilities(unittest.TestCase):
    def test_colorize_uses_ansi_when_enabled(self) -> None:
        output = colorize("hello", fg="green", bold=True, enabled=True)
        self.assertIn("\033[32m", output)
        self.assertTrue(output.endswith("\033[0m"))

    def test_progress_bar_updates_output(self) -> None:
        stream = io.StringIO()
        bar = ProgressBar(total=4, prefix="Working: ", stream=stream)
        bar.update(3)
        self.assertIn("75%", stream.getvalue())

    def test_load_config_file_and_environment_values(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            config_path = Path(tempdir) / "settings.json"
            config_path.write_text(json.dumps({"verbose": False, "name": "base"}), encoding="utf-8")
            with patch.dict(os.environ, {"APP_VERBOSE": "true", "APP_NAME": "from-env"}, clear=False):
                config = load_config(config_path, defaults={"verbose": True}, env_prefix="APP_")
                self.assertEqual(config["verbose"], "true")
                self.assertEqual(config["name"], "from-env")

    def test_prompt_helpers(self) -> None:
        with patch("builtins.input", side_effect=["alice", "yes", "prod"]):
            self.assertEqual(prompt("Name?"), "alice")
            self.assertTrue(confirm("Continue?", default=False))
            self.assertEqual(prompt_choice("Pick a target", ["dev", "prod"], default="dev"), "prod")


if __name__ == "__main__":
    unittest.main()
