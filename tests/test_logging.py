"""Tests for the logging helpers."""

import importlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


def load_logging_package():
    repo_root = Path(__file__).resolve().parents[1]
    package_dir = repo_root / "logging"

    current_path = list(sys.path)
    sys.modules.pop("logging", None)
    sys.modules.pop("logging.handlers", None)
    sys.path = [
        entry
        for entry in current_path
        if Path(entry or ".").resolve() != repo_root
    ]
    try:
        stdlib_logging = importlib.import_module("logging")
        stdlib_handlers = importlib.import_module("logging.handlers")
    finally:
        sys.path = current_path

    spec = importlib.util.spec_from_file_location(
        "pytbl_logging",
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules["logging"] = stdlib_logging
    sys.modules["logging.handlers"] = stdlib_handlers
    sys.modules["pytbl_logging"] = module
    spec.loader.exec_module(module)
    return module


logging_pkg = load_logging_package()


class TestLoggingHelpers(unittest.TestCase):
    """Cover logger construction, reconfiguration, and decorators."""

    def setUp(self) -> None:
        logging_pkg.clear_logger_registry()
        logging_pkg.set_default_logging_config()
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        logging_pkg.clear_logger_registry()
        self.tempdir.cleanup()

    def test_logger_creation_and_registry(self) -> None:
        logfile = self.root / "app.log"
        logger = logging_pkg.get_logger("pytbl.test", console_output=False, log_file=logfile)
        logger.info("hello")
        for handler in logger.handlers:
            handler.flush()

        self.assertIn("pytbl.test", logging_pkg.get_logger_registry())
        self.assertTrue(logfile.exists())
        self.assertIn("hello", logfile.read_text(encoding="utf-8"))

    def test_reconfigure_and_default_config(self) -> None:
        logging_pkg.set_default_logging_config(level="ERROR", console_output=False)
        logger = logging_pkg.get_logger("pytbl.default", console_output=False)
        self.assertEqual(logger.level, 40)

        updated = logging_pkg.reconfigure_logger("pytbl.default", level="DEBUG")
        self.assertEqual(updated.level, 10)

    def test_log_function_call_success(self) -> None:
        stream = io.StringIO()
        logger = logging_pkg.get_logger("pytbl.decorator", console_output=False)
        handler = importlib.import_module("logging").StreamHandler(stream)
        logger.addHandler(handler)

        @logging_pkg.log_function_call(logger=logger, level="INFO")
        def add(a, b):
            return a + b

        self.assertEqual(add(2, 3), 5)
        output = stream.getvalue()
        self.assertIn("Entering add(2, 3)", output)
        self.assertIn("Exiting add - Returned: 5", output)

    def test_log_function_call_exception(self) -> None:
        stream = io.StringIO()
        logger = logging_pkg.get_logger("pytbl.decorator.error", console_output=False)
        handler = importlib.import_module("logging").StreamHandler(stream)
        logger.addHandler(handler)

        @logging_pkg.log_function_call(logger=logger)
        def fail():
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            fail()

        self.assertIn("Exception in fail: boom", stream.getvalue())

    def test_registry_clears(self) -> None:
        logging_pkg.get_logger("pytbl.one", console_output=False)
        logging_pkg.clear_logger_registry()
        self.assertEqual(logging_pkg.get_logger_registry(), {})
