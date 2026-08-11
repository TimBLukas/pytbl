"""Tests for the testing utility package."""

import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tests.base import BaseTestCase
from tests import decorators, runner


class TestBaseTestCase(BaseTestCase):
    """Cover the extended unittest base case."""

    def test_temp_helpers(self) -> None:
        file_path = self.create_temp_file("hello", suffix=".txt")
        dir_path = self.create_temp_dir(prefix="sample_")

        self.assertTrue(file_path.exists())
        self.assertTrue(dir_path.exists())
        self.assertFileExists(file_path)
        self.assertFileContent(file_path, "hello")
        self.assertTrue(self.temp_dir.exists())

    def test_assertions_and_output_capture(self) -> None:
        self.assertEmpty([])
        self.assertNotEmpty([1])
        self.assertMatches(r"\d+", "abc123")
        self.assertNotMatches(r"\d+", "abc")
        self.assertDictSubset({"a": 1}, {"a": 1, "b": 2})
        self.assertJSONEqual({"a": 1}, '{"a": 1}')

        with self.assertRaises(AssertionError):
            self.assertEmpty([1])
        with self.assertRaises(AssertionError):
            self.assertNotEmpty([])

        with self.capture_stdout() as output:
            print("hello")
        self.assertEqual(output(), "hello\n")

    def test_env_and_mock_helpers(self) -> None:
        self.patch_env(TEST_SETTING="value", REMOVE_ME=None)
        self.assertEqual(os.environ["TEST_SETTING"], "value")
        self.assertNotIn("REMOVE_ME", os.environ)

        mock_time = self.patch_time(1000.0)
        self.assertEqual(mock_time.return_value, 1000.0)

        mock = self.patch("os.getcwd", return_value="/tmp")
        self.assertEqual(os.getcwd(), "/tmp")
        self.assertEqual(mock.call_count, 1)

    def test_assert_raises_with_message_and_call_count(self) -> None:
        def boom() -> None:
            raise ValueError("invalid input")

        self.assertRaisesWithMessage(ValueError, "invalid", boom)

        mock = MagicMock()
        mock()
        mock()
        self.assertCallCount(mock, 2)


class TestDecorators(unittest.TestCase):
    """Cover the test decorators."""

    def test_retry(self) -> None:
        attempts = {"count": 0}

        @decorators.retry(attempts=3)
        def flaky():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise RuntimeError("try again")
            return "ok"

        self.assertEqual(flaky(), "ok")
        self.assertEqual(attempts["count"], 3)

    def test_retry_failure(self) -> None:
        @decorators.retry(attempts=2)
        def always_fails():
            raise RuntimeError("nope")

        with self.assertRaises(AssertionError):
            always_fails()

    def test_time_limit(self) -> None:
        @decorators.time_limit(1.0)
        def fast():
            return "ok"

        self.assertEqual(fast(), "ok")

        with patch("tests.decorators.time.perf_counter", side_effect=[0.0, 2.0]):
            @decorators.time_limit(1.0)
            def slow():
                return "slow"

            with self.assertRaises(AssertionError):
                slow()


class TestRunnerHelpers(unittest.TestCase):
    """Cover the custom test runner wiring."""

    def test_runner_configuration(self) -> None:
        self.assertIs(runner.CustomTestRunner.resultclass, runner.ColoredTextTestResult)
