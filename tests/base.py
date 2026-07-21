# -----------------------------------------------------------
# base.py - extend base test case usage with patterns
# -----------------------------------------------------------
# Standard Library imports
# -----------------------------------------------------------
import unittest
import shutil
import tempfile
import json
import re
import os
import time
import datetime

from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Set,
    Optional,
    Union,
    Callable,
    Type,
    ContextManager,
    TypeVar,
    Iterator,
)
from contextlib import contextmanager
from unittest.mock import patch, MagicMock

# -----------------------------------------------------------
# Library specific imports
# -----------------------------------------------------------
from ..datatypes import PathLike

# -----------------------------------------------------------
# Optional Imports (if available)
# -----------------------------------------------------------
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# -----------------------------------------------------------
# Type aliases
# -----------------------------------------------------------
T = TypeVar("T")


class BaseTestCase(unittest.TestCase):
    """
    Extend base test case with additional assertions, patching helpers,
    temporary directory management, and other testing utils

    Features:
        - Automatic cleanup of temp directories
        - Easier patching with stop on tearDown
        - Custom assertions for containers, files, JSON, YAML, etc.
        - Helpers to mock env-variables, time and create temp files
    """

    # -----------------------------------------------------------
    # Setup / Teardown
    # -----------------------------------------------------------
    def setUp(self) -> None:
        super().setUp()
        self._patchers: List = []
        self._temp_dir: Optional[Path] = None
        self._env_vars: Dict[str, Optional[str]] = {}
        self._time_mock: Optional[MagicMock] = None

    def tearDown(self) -> None:
        # Stop all patches
        for patcher in self._patchers:
            patcher.stop()

        # Restore env vars
        for key, value in self._env_vars.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        # Cleanup temp dir
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)

        super().tearDown()

    # -----------------------------------------------------------
    # Patching helpers
    # -----------------------------------------------------------
    def patch(self, target: str, *args, **kwargs) -> MagicMock:
        """
               Patch an object and automatically stop the patch during test teardown

               (Wrapper around unittest.mock.patch)

        Args:
                   target: The target to patch (e.g., 'module.ClassName.method').
                   *args, **kwargs: Passed through to `patch`.

               Returns:
                   The mock object created by the patch.

               Example:
                   >>> mock_get = self.patch('requests.get')
                   >>> mock_get.return_value.status_code = 200
        """
        patcher = patch(target, *args, **kwargs)
        mocked = patcher.start()
        self._patchers.append(patcher)
        return mocked

    def patch_env(self, **env_vars) -> None:
        """
        Set environment variables for the duration of the test.

        All variables are restored to their original values (or removed) during teardown.

        Args:
            **env_vars: Key‑value pairs of environment variables to set.

        Example:
            >>> self.patch_env(API_KEY='test123', DEBUG='true')
        """
        for key, value in env_vars.items():
            # Store the original value for restoration
            if key not in self._env_vars:
                self._env_vars[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)

    def patch_time(
        self, fake_now: Optional[Union[float, datetime]] = None
    ) -> MagicMock:
        """
        Patch `time.time()` and optionally `datetime.datetime.now()`.

        Args:
            fake_now: If provided, sets the mocked time/now to this value.
                      Can be a timestamp (float) or a `datetime` object.

        Returns:
            The mock for `time.time()` (or `datetime.datetime` if patched).

        Example:
            >>> mock_time = self.patch_time(1609459200.0)  # 2021-01-01 00:00:00 UTC
        """
        from datetime import datetime

        # Patch time.time
        mock_time = self.patch("time.time")
        if fake_now is not None:
            if isinstance(fake_now, datetime):
                timestamp = fake_now.timestamp()
            else:
                timestamp = float(fake_now)
            mock_time.return_value = timestamp

            # Also patch datetime.datetime.now
            mock_datetime = self.patch("datetime.datetime")
            mock_now = mock_datetime.now
            mock_now.return_value = datetime.fromtimestamp(timestamp)
            self._time_mock = mock_time

        return mock_time

    # -------------------------------------------
    # Temporary file/directory helpers
    # -------------------------------------------
    @property
    def temp_dir(self) -> Path:
        """
        Provide a temporary directory path that is automatically cleaned up after the test.

        The directory is created the first time this property is accessed.

        Returns:
            Path to the temporary directory.

        Example:
            >>> file_path = self.temp_dir / 'data.txt'
            >>> file_path.write_text('content')
        """
        if not self._temp_dir:
            self._temp_dir = Path(tempfile.mkdtemp())
        return self._temp_dir

    def create_temp_file(
        self,
        content: Union[str, bytes],
        suffix: str = "",
        prefix: str = "",
        dir: Optional[PathLike] = None,
    ) -> Path:
        """
        Create a temporary file with the given content and return its path.

        The file is placed inside `self.temp_dir` (or a custom directory) and will be
        cleaned up automatically.

        Args:
            content: Content to write (string for text, bytes for binary).
            suffix: Suffix for the file name (e.g., '.txt').
            prefix: Prefix for the file name.
            dir: Custom directory (if None, uses `self.temp_dir`).

        Returns:
            Path to the created file.

        Example:
            >>> path = self.create_temp_file('{"key": "value"}', suffix='.json')
            >>> assert path.read_text() == '{"key": "value"}'
        """
        if dir is None:
            dir = self.temp_dir
        else:
            dir = Path(dir)
            dir.mkdir(parents=True, exist_ok=True)

        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=str(dir))
        with os.fdopen(fd, "wb" if isinstance(content, bytes) else "w") as f:
            f.write(content)
        return Path(path)

    def create_temp_dir(self, prefix: str = "", suffix: str = "") -> Path:
        """
        Create a temporary subdirectory inside `self.temp_dir` and return its path.

        The subdirectory will be removed when the test teardown cleans up the parent.

        Args:
            prefix: Prefix for the directory name.
            suffix: Suffix for the directory name.

        Returns:
            Path to the created subdirectory.

        Example:
            >>> subdir = self.create_temp_dir(prefix='test_')
        """
        path = Path(
            tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=str(self.temp_dir))
        )
        return path

    # -------------------------------------------
    # Custom assertions
    # -------------------------------------------
    def assertEmpty(
        self, container: Union[List, Dict, Set, str], msg: Optional[str] = None
    ) -> None:
        """
        Assert that a container (list, dict, set, or string) is empty.

        Args:
            container: The container to check.
            msg: Optional custom failure message.

        Raises:
            AssertionError: If the container is not empty.

        Example:
            >>> self.assertEmpty([])          # passes
            >>> self.assertEmpty({'a': 1})    # fails
        """
        if len(container) != 0:
            standard_msg = f"{repr(container)} is not empty (length: {len(container)})"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertNotEmpty(
        self, container: Union[List, Dict, Set, str], msg: Optional[str] = None
    ) -> None:
        """
        Assert that a container is not empty.

        Args:
            container: The container to check.
            msg: Optional custom failure message.
        """
        if len(container) == 0:
            standard_msg = f"{repr(container)} is empty"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertNotMatches(
        self, pattern: str, string: str, msg: Optional[str] = None
    ) -> None:
        """
        Assert that a string does **not** match a regular expression.

        Args:
            pattern: The regex pattern to avoid.
            string: The string to test.
            msg: Optional custom failure message.

        Example:
            >>> self.assertNotMatches(r'\d+', 'abc')
        """
        if re.search(pattern, string):
            standard_msg = f"Pattern '{pattern}' matched string '{string}'"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertMatches(
        self, pattern: str, string: str, msg: Optional[str] = None
    ) -> None:
        """
        Assert that a string matches a regular expression.

        Args:
            pattern: The regex pattern.
            string: The string to test.
            msg: Optional custom failure message.
        """
        if not re.search(pattern, string):
            standard_msg = f"Pattern '{pattern}' did not match string '{string}'"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertFileExists(self, path: PathLike, msg: Optional[str] = None) -> None:
        """
        Assert that a file exists.

        Args:
            path: Path to the file.
            msg: Optional custom failure message.
        """
        path = Path(path)
        if not path.exists():
            standard_msg = f"File does not exist: {path}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertFileNotExists(self, path: PathLike, msg: Optional[str] = None) -> None:
        """
        Assert that a file does not exist.

        Args:
            path: Path to the file.
            msg: Optional custom failure message.
        """
        path = Path(path)
        if path.exists():
            standard_msg = f"File exists: {path}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertFileContent(
        self, path: PathLike, expected: Union[str, bytes], msg: Optional[str] = None
    ) -> None:
        """
        Assert that a file contains exactly the given content (text or binary).

        Args:
            path: Path to the file.
            expected: Expected content (string or bytes).
            msg: Optional custom failure message.
        """
        path = Path(path)
        mode = "r" if isinstance(expected, str) else "rb"
        with path.open(mode) as f:
            actual = f.read()
        self.assertEqual(actual, expected, msg)

    def assertIsValidJSON(
        self, data: Union[str, PathLike], msg: Optional[str] = None
    ) -> None:
        """
        Assert that a string or file contains valid JSON.

        Args:
            data: Either a JSON string or a path to a JSON file.
            msg: Optional custom failure message.
        """
        try:
            if isinstance(data, (str, Path)):
                path = Path(data)
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                else:
                    content = data
            else:
                content = str(data)
            json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            standard_msg = f"Invalid JSON: {e}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertIsValidYAML(
        self, data: Union[str, PathLike], msg: Optional[str] = None
    ) -> None:
        """
        Assert that a string or file contains valid YAML.

        Requires PyYAML to be installed.

        Args:
            data: Either a YAML string or a path to a YAML file.
            msg: Optional custom failure message.

        Raises:
            ImportError: If PyYAML is not available.
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for YAML assertions. Install with: pip install pyyaml"
            )
        try:
            if isinstance(data, (str, Path)):
                path = Path(data)
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                else:
                    content = data
            else:
                content = str(data)
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            standard_msg = f"Invalid YAML: {e}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertDictSubset(
        self, subset: Dict, superset: Dict, msg: Optional[str] = None
    ) -> None:
        """
        Assert that all key‑value pairs in `subset` are also in `superset`.

        Args:
            subset: The dictionary that must be a subset.
            superset: The dictionary that must contain all items from `subset`.
            msg: Optional custom failure message.
        """
        missing = {}
        for key, value in subset.items():
            if key not in superset:
                missing[key] = ("missing", value)
            elif superset[key] != value:
                missing[key] = (superset[key], value)
        if missing:
            standard_msg = f"Subset mismatch: {missing}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertRaisesWithMessage(
        self,
        expected_exception: Type[Exception],
        expected_message: str,
        callable_obj: Callable,
        *args,
        **kwargs,
    ) -> None:
        """
        Assert that calling `callable_obj` raises `expected_exception` with a message
        that matches (or contains) `expected_message`.

        Args:
            expected_exception: The expected exception class.
            expected_message: A string that must appear in the exception message.
            callable_obj: The function to call.
            *args, **kwargs: Arguments to pass to `callable_obj`.

        Example:
            >>> self.assertRaisesWithMessage(ValueError, 'invalid', int, 'abc')
        """
        with self.assertRaises(expected_exception) as cm:
            callable_obj(*args, **kwargs)
        self.assertIn(expected_message, str(cm.exception))

    def assertCallCount(
        self, mock: MagicMock, count: int, msg: Optional[str] = None
    ) -> None:
        """
        Assert that a mock was called exactly `count` times.

        Args:
            mock: The mock object.
            count: Expected call count.
            msg: Optional custom failure message.
        """
        self.assertEqual(
            mock.call_count,
            count,
            msg or f"Expected {count} calls, got {mock.call_count}",
        )

    # -------------------------------------------
    # Capture output helpers
    # -------------------------------------------
    @contextmanager
    def capture_stdout(self) -> Iterator[str]:
        """
        Context manager to capture stdout output.

        Yields:
            The captured output string.

        Example:
            >>> with self.capture_stdout() as output:
            ...     print('Hello')
            ... self.assertEqual(output, 'Hello\\n')
        """
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            yield sys.stdout.getvalue
        finally:
            sys.stdout = old_stdout

    @contextmanager
    def capture_stderr(self) -> Iterator[str]:
        """Same as `capture_stdout`, but for stderr."""
        from io import StringIO
        import sys

        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            yield sys.stderr.getvalue
        finally:
            sys.stderr = old_stderr

    # -------------------------------------------
    # Assertions for common patterns
    # -------------------------------------------
    def assertIsSubclass(
        self, cls: Type, parent: Type, msg: Optional[str] = None
    ) -> None:
        """Assert that `cls` is a subclass of `parent`."""
        if not issubclass(cls, parent):
            standard_msg = f"{cls} is not a subclass of {parent}"
            self.fail(self._formatMessage(msg, standard_msg))

    def assertJSONEqual(
        self,
        first: Union[Dict, str],
        second: Union[Dict, str],
        msg: Optional[str] = None,
    ) -> None:
        """
        Assert that two JSON strings or dicts are equal after parsing.

        Args:
            first: JSON string or dict.
            second: JSON string or dict.
            msg: Optional custom failure message.
        """
        if isinstance(first, str):
            first = json.loads(first)
        if isinstance(second, str):
            second = json.loads(second)
        self.assertEqual(first, second, msg)
