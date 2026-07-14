<<<<<<< Updated upstream
"""
http – a full‑featured HTTP client module with retries, hooks, and models

Public API:
    - HttpClient (main client)
    - HttpClientConfig (configuration dataclass)
    - HttpRequest, HttpResponse (data models)
    - Exceptions: HTTPError, ConnectionError, TimeoutError, etc.
"""

from .client import HttpClient
from .config import HttpClientConfig
from .models import HttpRequest, HttpResponse
from .exceptions import (
    HTTPError,
    ConnectionError,
    TimeoutError,
    TooManyRedirectsError,
    RequestError,
    HTTPStatusError,
    raise_for_status,
)

__all__ = [
    "HttpClient",
    "HttpClientConfig",
    "HttpRequest",
    "HttpResponse",
    "HTTPError",
    "ConnectionError",
    "TimeoutError",
    "TooManyRedirectsError",
    "RequestError",
    "HTTPStatusError",
    "raise_for_status",
]

__version__ = "0.0.1"
__author__ = "TBL"
=======
from .client import HttpClient
from .exceptions import HTTPError
from .models import HttpResponse, RequestPayload, AuthToken

__all__ = ["HttpClient", "HTTPError", "HttpResponse", "RequestPayload", "AuthToken"]
>>>>>>> Stashed changes
