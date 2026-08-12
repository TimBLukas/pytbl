# -------------------------------------------
# tests/runner.py – test discovery and execution with coloured output
# -------------------------------------------

# -------------------------------------------
# Standard Library imports
# -------------------------------------------
import sys
import unittest
import os
from pathlib import Path
from typing import Union, Any

# -------------------------------------------
# Type aliases
# -------------------------------------------
TestResult = unittest.TestResult
TestCase = unittest.TestCase
TestSuite = unittest.TestSuite
# -------------------------------------------
# Constants
# -------------------------------------------
DEFAULT_PATTERN = "test_*.py"
DEFAULT_VERBOSITY = 2
DEFAULT_START_DIR = "."


# -------------------------------------------
# Colour support
# -------------------------------------------
def _supports_color() -> bool:
    """Check if the terminal supports ANSI colour codes"""
    if hasattr(sys.stdout, "isatty") and not sys.stdout.isatty():
        return False
    if "NO_COLOR" in os.environ:
        return False
    return True


_COLORS = {
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "reset": "\033[0m",
}


# -------------------------------------------
# Custom test result with coloured markers
# -------------------------------------------
class ColoredTextTestResult(unittest.TextTestResult):
    """Extends `TextTestResult` to print coloured PASS/FAIL/ERROR markers"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._use_color = _supports_color()

    def _color(self, name: str) -> str:
        return _COLORS.get(name, "") if self._use_color else ""

    def addSuccess(self, test: TestCase) -> None:
        super().addSuccess(test)
        sys.stderr.write(f"{self._color('green')}[PASS]{self._color('reset')} ")

    def addFailure(self, test: TestCase, err: Any) -> None:
        super().addFailure(test, err)
        sys.stderr.write(f"{self._color('red')}[FAIL]{self._color('reset')} ")

    def addError(self, test: TestCase, err: Any) -> None:
        super().addError(test, err)
        sys.stderr.write(f"{self._color('yellow')}[ERROR]{self._color('reset')} ")


class CustomTestRunner(unittest.TextTestRunner):
    """Test runner using `ColoredTextTestResult`"""

    resultclass = ColoredTextTestResult


# -------------------------------------------
# Public API
# -------------------------------------------
def run_tests(
    start_dir: str = DEFAULT_START_DIR,
    pattern: str = DEFAULT_PATTERN,
    verbosity: int = DEFAULT_VERBOSITY,
    failfast: bool = False,
    buffer: bool = False,
) -> bool:
    """
    Discover and run all tests matching a pattern in a directory

    Args:
        start_dir: Directory to start discovery (default: current directory)
        pattern: File name pattern for test files (default: "test_*.py")
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose) – default 2
        failfast: Stop at first failure/error
        buffer: Buffer stdout/stderr

    Returns:
        True if all tests passed, False otherwise

    Example:
        >>> success = run_tests("tests", verbosity=1)
    """
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern=pattern)
    runner = CustomTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=buffer,
    )
    result = runner.run(suite)
    return result.wasSuccessful()


def run_test_file(
    file_path: Union[str, Path],
    verbosity: int = DEFAULT_VERBOSITY,
    failfast: bool = False,
    buffer: bool = False,
) -> bool:
    """
    Run a single test file directly

    Args:
        file_path: Path to a Python file containing tests
        verbosity: Verbosity level
        failfast: Stop at first failure/error
        buffer: Buffer stdout/stderr

    Returns:
        True if all tests passed, False otherwise
    """
    path = Path(file_path)
    loader = unittest.TestLoader()
    suite = loader.discover(str(path.parent), pattern=path.name)
    runner = CustomTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=buffer,
    )
    result = runner.run(suite)
    return result.wasSuccessful()


def run_test_class(
    test_class: type,
    verbosity: int = DEFAULT_VERBOSITY,
    failfast: bool = False,
    buffer: bool = False,
) -> bool:
    """
    Run a specific test class.

    Args:
        test_class: A `unittest.TestCase` subclass.
        verbosity: Verbosity level.
        failfast: Stop at first failure/error.
        buffer: Buffer stdout/stderr.

    Returns:
        True if all tests passed, False otherwise.
    """
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
    runner = CustomTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=buffer,
    )
    result = runner.run(suite)
    return result.wasSuccessful()
