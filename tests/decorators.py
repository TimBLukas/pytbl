# my_library/testing/decorators.py
import time
import functools
import unittest


def time_limit(seconds: float):
    """Fails the test if it takes longer than the specified limit."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            if duration > seconds:
                raise AssertionError(
                    f"Test exceeded time limit of {seconds}s (took {duration:.4f}s)"
                )
            return result

        return wrapper

    return decorator


def retry(attempts: int = 3):
    """Retries a test case a set number of times before letting it fail."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
            raise AssertionError(
                f"Test failed after {attempts} attempts"
            ) from last_exception

        return wrapper

    return decorator
