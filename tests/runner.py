# my_library/testing/runner.py
import unittest
import sys


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom result class to print green PASS and red FAIL markers."""

    def addSuccess(self, test):
        super().addSuccess(test)
        sys.stderr.write("\033[32m[PASS]\033[0m ")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        sys.stderr.write("\033[31m[FAIL]\033[0m ")

    def addError(self, test, err):
        super().addError(test, err)
        sys.stderr.write("\033[33m[ERROR]\033[0m ")


class CustomTestRunner(unittest.TextTestRunner):
    resultclass = ColoredTextTestResult


def run_tests_in_directory(start_dir: str = "."):
    """Discovers and runs all tests in the specified directory."""
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = CustomTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
