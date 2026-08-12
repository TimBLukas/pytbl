# ------------------------------------------------------------------
# tests/decorators.py - extended test decorators
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Standard Libary imports
# ------------------------------------------------------------------
import time
import functools
import os
from typing import Any, Callable, Optional, Tuple, Type
from unittest import SkipTest


# ------------------------------------------------------------------
# Core Decorators
# ------------------------------------------------------------------
def time_limit(seconds: float) -> Callable:
    """
    Decorator that fails a test if its excecution exceeds the given time limit.

    NOTE: This measures time after the test completes; it does **not** interrupt
    long-running tests. For a true timeout, consider using `pytest-timeout`
    or the `timeout` decorator below (which uses multiprocessing).

    Args:
        seconds: Maximum allowed execution time in seconds.

    Returns:
        Decorated test function

    Raises:
        AssertionError: If the test runs longer than `seconds`

    Example:
        >>> @time_limit(0.5)
        ... def test_fast()
        ...     time.sleep(0.1)
        ... # passes

        >>> @time_limit(0.5)
        ... def test_slow()
        ...     time.sleep(1.0)
        ... # raises AssertionError
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            if duration > seconds:
                raise AssertionError(
                    f"Test '{func.__name__} exceeded time limit of {seconds}s - took {duration:.4f}s"
                )
            return result

        return wrapper

    return decorator


def retry(
    attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    delay: float = 0.0,
) -> Callable:
    """
    Decorator that retries a test a specified number of times before failing

    Args:
        attempts: Maximum number of attemts (including the initial run)
        exception: Tuple of exception types t hat trigger a retry (If empty or (Exception,) all exceptions are retried
        delay: Wait time (seconds) between attempts (optional)

    Returns:
        Decorated test function

    Raises:
        AssertionError: If the test fails after all attempts
        The original exception: If an exception not in `exceptions` is raised

    Example:
        >>> @retry(attempts=3, exceptions=(ConnectionError, TimeoutError))
        ... def test_unreliable():
        ...     # flaky test that may raise transient errors
        ...     ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == attempts:
                        break
                    if delay:
                        time.sleep(delay)
                except Exception as e:
                    # If the Exception is not in the allowed lists, re-raise
                    raise e

            raise AssertionError(
                f"Test '{func.__name__}' failed after {attempts} attempt(s). - Last exception: {last_exception}"
            ) from last_exception

        return wrapper

    return decorator


# ------------------------------------------------------------------
# Extended decorators
# ------------------------------------------------------------------
def skip_if(condition: bool, reason: str = "Condition met, skipping test") -> Callable:
    """
    Decorator that skips the test if `condition` evaluates to True.

    Args:
        condition: Boolean condition (or callable that returns bool).
        reason: Explanation why the test is skipped.

    Returns:
        Decorated test function.

    Raises:
        unittest.SkipTest: If condition is true.

    Example:
        >>> @skip_if(sys.platform == 'win32', reason='not supported on Windows')
        ... def test_linux_only():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cond = condition() if callable(condition) else condition
            if cond:
                raise SkipTest(reason)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def skip_unless(
    condition: bool, reason: str = "Condition not met, skipping test"
) -> Callable:
    """
    Decorator that skips the test unless `condition` evaluates to True.

    Args:
        condition: Boolean condition (or callable that returns bool).
        reason: Explanation why the test is skipped

    Returns:
        Decorated test function.

    Example:
        >>> @skip_unless(has_internet(), reason='No internet connection')
        ... def test_api_call():
        ...     pass
    """
    return skip_if(not condition, reason)


def repeat(times: int = 2) -> Callable:
    """
    Decorator that runs the test function repeatedly
    If any repetition fails, the test fails (no further retries)

    Args:
        times: Number of times to run the test.

    Returns:
        Decorated test function.

    Example:
        >>> @repeat(5)
        ... def test_random_behavior():
        ...     # will run 5 times; if any fails, the entire test fails
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_result = None
            for i in range(times):
                try:
                    last_result = func(*args, **kwargs)
                except Exception as e:
                    raise AssertionError(
                        f"Repetition {i + 1} of '{func.__name__}' failed: {e}"
                    ) from e

            return last_result

        return wrapper

    return decorator


def require_module(module_name: str, reason: Optional[str] = None) -> Callable:
    """
    Decorator that skips the test if a required module is not importable

    Args:
        module_name: Name of the module to require
        reason: Optional custom skip message

    Returns:
        Decorated test function

    Example:
        >>> @require_module('numpy')
        ... def test_numpy_operation():
        ...     import numpy as np
        ...     ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs: Any) -> Any:
            try:
                __import__(module_name)
            except ImportError:
                skip_msg = reason or f"Module '{module_name}' not installed"
                raise SkipTest(skip_msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_env(
    key: str, value: Optional[str] = None, reason: Optional[str] = None
) -> Callable:
    """
    Decorator that skips the test if an environment variable is missing or (if `value` is given) does not equal the excpected value.
    or (if `value` is given) does not equal the expected value.

    Args:
        key: Environment variable name
        value: Optional excpected value (if not given, only checks existence)
        reason: Optional custom skip message

    Returns:
        Decorated test function

    Example:
        >>> @require_env('API_KEY')
        ... def test_api():
        ...     # will skip if API_KEY not set
        ...     pass

        >>> @require_env('ENV', 'production')
        ... def test_production_only():
        ...     # will skip unless ENV == 'production'
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            env_val = os.environ.get(key)
            if env_val is None:
                skip_msg = reason or f"Environment variable '{key}' is not set"
                raise SkipTest(skip_msg)

            if value is not None and env_val != value:
                skip_msg = (
                    reason
                    or f"Environment variable '{key}' = '{env_val}' expected '{value}'"
                )
                raise SkipTest(skip_msg)

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ------------------------------------------------------------------
# Convenience: flaky (retry with exponential backoff)
# ------------------------------------------------------------------
def flaky(
    attempts: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    delay: float = 0.5,
    backoff: float = 2.0,
) -> Callable:
    """
    Decorator that retries a test with exponential backoff
    This is a specialised version of `retry` that increases the wait time between attempts

    Args:
        attempts: Maximum number of attempts (including the first)
        exceptions: Tuple of exception types that trigger a retry
        delay: Initial wait time (seconds)
        backoff: Multiplier for delay after each failure

    Returns:
        Decorated test function

    Example:
        >>> @flaky(attempts=5, exceptions=(ConnectionError,))
        ... def test_network_call():
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    if attempt == attempts:
                        break
                    time.sleep(current_delay)
                    current_delay *= backoff

                except Exception as e:
                    raise e  # re raise unexpected exceptions

            raise AssertionError(
                f"Flaky test '{func.__name__}' failed after {attempts} attempts. Last exception: {last_exception}"
            ) from last_exception

        return wrapper

    return decorator


# ------------------------------------------------------------------
# Advanced: true timeout using multiprocessing
# ------------------------------------------------------------------
def timeout(seconds: float) -> Callable:
    """
    Decorator that forces a test to abort if it runs longer than `seconds`

    This uses a seperate process to run the test and kills it if the time limit is exceeded.
    It is more reliable than `time_limit` for catching infinite loops.

    Args:
        seconds: Max allowed execution time in seconds

    Returns:
        Decorated function

    Raises:
        AssertionError: If the test times out.
        Any exception raised by the test (if it finishes in time)

    Example:
        >>> @timeout(2)
        ... def test_long_running():
        ...     while True:
        ...         pass
        ... # raisaes AssertionError: Timeout after 2s
    """
    import multiprocessing as mp

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            q = mp.Queue()

            def target():
                try:
                    result = func(*args, **kwargs)
                    q.put(("success", result))
                except Exception as e:
                    q.put(("error", e))

            proc = mp.Process(target=target)
            proc.start()
            proc.join(timeout=seconds)

            if proc.is_alive():
                proc.terminate()
                proc.join()
                raise AssertionError(
                    f"Test '{func.__name__}' timed out after {seconds}s"
                )

            # Process finished in time:
            if q.empty():
                # Should not empty - treat as error
                raise RuntimeError("No result from child process")

            status, payload = q.get()
            if status == "error":
                raise payload  # re raise exception

            return payload

        return wrapper

    return decorator
