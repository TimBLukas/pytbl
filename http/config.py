"""
Configuration module for the HTTP client
Provides a dataclass with sensible defaults for timeouts, retries, headers, etc.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ------------------------------------------
# Standard Library imports
# ------------------------------------------
from datatypes.http_return_codes import (
    RETRYABLE_STATUS_CODES,
)  # example: {429, 500, 502, 503, 504}


@dataclass
class HttpClientConfig:
    """
    Configuration for `HttpClient`.

    Attributes:
        timeout: Default request timeout in seconds.
        max_retries: Number of retries for retryable errors (0 to disable).
        retry_backoff_factor: Exponential backoff factor (seconds).
        retry_status_codes: HTTP status codes that trigger a retry.
        retry_methods: HTTP methods that are retried.
        default_headers: Default headers sent with every request.
        raise_for_status: If True, automatically raise `HTTPError` on 4xx/5xx.
    """

    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 1.0
    retry_status_codes: List[int] = field(
        default_factory=lambda: RETRYABLE_STATUS_CODES
    )
    retry_methods: List[str] = field(
        default_factory=lambda: ["GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "User-Agent": "MyLib-HttpClient/1.0",
            "Accept": "application/json",
        }
    )
    raise_for_status: bool = True
