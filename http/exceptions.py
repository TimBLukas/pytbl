"""
Custom exceptions for the HTTP client module

Hierarchy:
    HTTPError (base)
    ├── ConnectionError
    ├── TimeoutError
    ├── TooManyRedirectsError
    └── RequestError
        └── HTTPStatusError (for 4xx/5xx responses)
"""

# ------------------------------------------
# Standard Library imports
# ------------------------------------------
from typing import Optional

# ------------------------------------------
# Local imports
# ------------------------------------------
from .models import HttpResponse


class HTTPError(Exception):
    """Base exception for all HTTP client errors"""

    pass


class ConnectionError(HTTPError):
    """Raised when a connection cannot be established"""

    pass


class TimeoutError(HTTPError):
    """Raised when a request times out"""

    pass


class TooManyRedirectsError(HTTPError):
    """Raised when the request exceeds the maximum number of redirects"""

    pass


class RequestError(HTTPError):
    """Base for request‑related errors (including status code errors)"""

    pass


class HTTPStatusError(RequestError):
    """
    Raised for HTTP responses with a 4xx or 5xx status code

    Attributes:
        response: The `HttpResponse` object that caused the error
        status_code: HTTP status code
        message: Error message
    """

    def __init__(self, response: HttpResponse, message: Optional[str] = None):
        self.response = response
        self.status_code = response.status_code
        self.message = message or f"HTTP {response.status_code}: {response.reason}"
        super().__init__(self.message)


def raise_for_status(response: HttpResponse) -> None:
    """
    Raise `HTTPStatusError` if the response status code indicates an error

    Args:
        response: `HttpResponse` object

    Raises:
        HTTPStatusError: If status code is 400 or higher
    """
    if 400 <= response.status_code < 600:
        raise HTTPStatusError(response)
