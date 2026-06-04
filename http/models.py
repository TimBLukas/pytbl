"""
Data models for HTTP requests and responses

These dataclasses are used to pass information between hooks and
to provide a consistent interface for the `HttpClient`
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class HttpRequest:
    """
    Representation of an HTTP request

    Attributes:
        method: HTTP method (e.g., 'GET', 'POST')
        url: Full URL (including query parameters if any)
        headers: Request headers
        data: Form‑encoded data (if any)
        json: JSON‑serializable data
        cookies: Cookies to send
        files: Files to upload (dict mapping field name to file handle)
        auth: Basic auth tuple (username, password)
        timeout: Timeout in seconds
        allow_redirects: Whether to follow redirects
    """

    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Any] = None
    json: Optional[Any] = None
    cookies: Optional[Dict[str, str]] = None
    files: Optional[Dict] = None
    auth: Optional[tuple] = None
    timeout: int = 30
    allow_redirects: bool = True


@dataclass
class HttpResponse:
    """
    Representation of an HTTP response

    Attributes:
        status_code: HTTP status code (e.g., 200, 404)
        reason: Reason phrase (e.g., 'OK', 'Not Found')
        headers: Response headers
        text: Response body as text (decoded)
        content: Response body as bytes
        elapsed: Time taken for the request (seconds)
        request: The `HttpRequest` that produced this response
    """

    status_code: int
    reason: str
    headers: Dict[str, str]
    text: str
    content: bytes
    elapsed: float
    request: HttpRequest

    def json(self, **kwargs) -> Any:
        """
        Parse the response body as JSON

        Args:
            **kwargs: Additional arguments passed to `json.loads()`

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If the response body is not valid JSON
        """
        import json

        return json.loads(self.text, **kwargs)

    @property
    def ok(self) -> bool:
        """Return True if status code is < 400."""
        return self.status_code < 400

    def raise_for_status(self) -> None:
        """Raise `HTTPStatusError` if status code indicates an error"""
        from .exceptions import raise_for_status

        raise_for_status(self)
