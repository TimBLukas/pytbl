"""
Data models for HTTP requests and responses.

These dataclasses are used to pass information between hooks and
to provide a consistent interface for the `HttpClient`.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class HttpRequest:
    """
    Representation of an HTTP request.

    Attributes:
        method:
            HTTP method (e.g., 'GET', 'POST').

        url:
            Full URL including query parameters.

        headers:
            Request headers.

        data:
            Form-encoded request data.

        json:
            JSON-serializable request body.

        cookies:
            Cookies to send.

        files:
            Files to upload.

        auth:
            Basic authentication tuple.

        timeout:
            Timeout in seconds.

        allow_redirects:
            Whether redirects should be followed.
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
    Representation of an HTTP response.

    Attributes:
        status_code:
            HTTP status code (e.g., 200, 404).

        reason:
            HTTP reason phrase.

        headers:
            Response headers.

        text:
            Response body as decoded text.

        content:
            Response body as bytes.

        elapsed:
            Request execution time in seconds.

        request:
            The HttpRequest that produced this response.
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
        Parse response body as JSON.

        Args:
            **kwargs:
                Arguments passed to json.loads().

        Returns:
            Parsed JSON object.

        Raises:
            ValueError:
                If response content is not valid JSON.
        """

        import json

        return json.loads(
            self.text,
            **kwargs
        )


    @property
    def ok(self) -> bool:
        """
        Returns True if the HTTP status code indicates success.
        """
        return self.status_code < 400


    def raise_for_status(self) -> None:
        """
        Raise HTTPError for unsuccessful responses.
        """

        from .exceptions import raise_for_status

        raise_for_status(self)