"""
HTTP client module - configurable HTTP client with retries and hooks.

Provides an HTTP client build on `request.Session` with:
automatic retries, request/response hooks for logging, auth, etc., support for json, form data and file uploads.
"""

# ---------------------------------------------------------------
# Standard library imports
# --------------------------------------------------------------
import time
import json
from typing import Any, Dict, List, Optional, Union, Callable, Iterator
from urllib.parse import urljoin, urlencode

# ---------------------------------------------------------------
# Library specific imports
# --------------------------------------------------------------
from datatypes.http_return_codes import HTTP_RETURN_CODES
from .exceptions import (
    HTTPError,
    ConnectionError,
    TimeoutError,
    TooManyRedirectsError,
    RequestError,
    raise_for_status,
)
from .config import HttpClientConfig
from .models import HttpRequest, HttpResponse


# ---------------------------------------------------------------
# External Imports
# --------------------------------------------------------------
try:
    import requests
    from requests.adaptars import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError as e:
    raise ImportError(
        "The `requests` library is required, install with pip install requests"
    ) from e


# ------------------------------------------
# Private Helper Functions
# ------------------------------------------
def _merge_dicts(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries (simple shallow merge is enough for headers"""
    result = base.copy()
    result.update(override)
    return result


def _build_query_params(params: Optional[Union[Dict, List[tuple], str]]) -> str:
    """Convert query parameters to a URL‑encoded string."""
    if not params:
        return ""
    if isinstance(params, str):
        return params if params.startswith("?") else f"?{params}"
    if isinstance(params, dict):
        return f"?{urlencode(params)}"
    if isinstance(params, list):
        return f"?{urlencode(params)}"
    raise TypeError(f"Unsupported query parameter type: {type(params)}")


def _default_hook(
    request: HttpRequest, response: Optional[HttpResponse] = None
) -> None:
    """Default no‑op hook."""
    pass


# ------------------------------------------
# Public API – HttpClient
# ------------------------------------------
class HttpClient:
    """
    A robust HTTP client with retries, hooks, and session management.

    Example:
        >>> client = HttpClient("https://api.example.com")
        >>> response = client.get("/users")
        >>> print(response.json())
    """

    def __init__(
        self,
        base_url: str = "",
        config: Optional[HttpClientConfig] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_backoff_factor: Optional[float] = None,
    ):
        """
        Initialise the HTTP client.

        Args:
            base_url: Base URL for all requests (e.g., "https://api.example.com/v1").
            config: Configuration object (overrides individual parameters).
            headers: Default headers to send with every request.
            timeout: Default timeout in seconds (if None, uses config default).
            max_retries: Maximum number of retries for retryable errors.
            retry_backoff_factor: Exponential backoff factor (seconds).
        """
        self.config = config or HttpClientConfig()
        self.base_url = base_url.rstrip("/")

        # Override config with explicit arguments
        self.timeout = timeout if timeout is not None else self.config.timeout
        max_retries = (
            max_retries if max_retries is not None else self.config.max_retries
        )
        backoff = (
            retry_backoff_factor
            if retry_backoff_factor is not None
            else self.config.retry_backoff_factor
        )

        # Create a session with retry strategy
        self.session = requests.Session()
        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=backoff,
                status_forcelist=self.config.retry_status_codes,
                allowed_methods=self.config.retry_methods,
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

        # Set default headers
        default_headers = self.config.default_headers.copy()
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)

        # Hooks
        self._request_hooks: List[Callable[[HttpRequest], None]] = []
        self._response_hooks: List[Callable[[HttpResponse], None]] = []

    def _url(self, path: str) -> str:
        """Join base URL with a path."""
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _build_request(
        self,
        method: str,
        url: str,
        params: Optional[Union[Dict, List, str]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None,
        auth: Optional[tuple] = None,
        timeout: Optional[int] = None,
        allow_redirects: bool = True,
    ) -> HttpRequest:
        """Construct an HttpRequest object from arguments."""
        full_url = self._url(url)
        if params:
            full_url += _build_query_params(params)

        final_headers = _merge_dicts(self.session.headers, headers or {})

        return HttpRequest(
            method=method.upper(),
            url=full_url,
            headers=final_headers,
            data=data,
            json=json_data,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout or self.timeout,
            allow_redirects=allow_redirects,
        )

    def _execute_request(self, request: HttpRequest) -> HttpResponse:
        """Execute a request using the session, apply hooks, and raise errors."""
        # Pre‑request hooks
        for hook in self._request_hooks:
            hook(request)

        start_time = time.time()
        try:
            response = self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                data=request.data,
                json=request.json,
                cookies=request.cookies,
                files=request.files,
                auth=request.auth,
                timeout=request.timeout,
                allow_redirects=request.allow_redirects,
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection error: {e}") from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except requests.exceptions.TooManyRedirects as e:
            raise TooManyRedirectsError(f"Too many redirects: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {e}") from e

        elapsed = time.time() - start_time
        http_response = HttpResponse(
            status_code=response.status_code,
            reason=response.reason,
            headers=dict(response.headers),
            text=response.text,
            content=response.content,
            elapsed=elapsed,
            request=request,
        )

        # Post‑response hooks
        for hook in self._response_hooks:
            hook(http_response)

        # Raise HTTPError for 4xx/5xx unless configured otherwise
        if self.config.raise_for_status:
            raise_for_status(http_response)

        return http_response

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
    def get(
        self,
        url: str,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a GET request."""
        request = self._build_request(
            "GET", url, params=params, headers=headers, **kwargs
        )
        return self._execute_request(request)

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a POST request."""
        request = self._build_request(
            "POST",
            url,
            params=params,
            data=data,
            json_data=json,
            headers=headers,
            files=files,
            **kwargs,
        )
        return self._execute_request(request)

    def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a PUT request."""
        request = self._build_request(
            "PUT",
            url,
            params=params,
            data=data,
            json_data=json,
            headers=headers,
            **kwargs,
        )
        return self._execute_request(request)

    def patch(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a PATCH request."""
        request = self._build_request(
            "PATCH",
            url,
            params=params,
            data=data,
            json_data=json,
            headers=headers,
            **kwargs,
        )
        return self._execute_request(request)

    def delete(
        self,
        url: str,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a DELETE request."""
        request = self._build_request(
            "DELETE", url, params=params, headers=headers, **kwargs
        )
        return self._execute_request(request)

    def head(
        self,
        url: str,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform a HEAD request."""
        request = self._build_request(
            "HEAD", url, params=params, headers=headers, **kwargs
        )
        return self._execute_request(request)

    def options(
        self,
        url: str,
        params: Optional[Union[Dict, List, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Perform an OPTIONS request."""
        request = self._build_request(
            "OPTIONS", url, params=params, headers=headers, **kwargs
        )
        return self._execute_request(request)

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------
    def add_request_hook(self, hook: Callable[[HttpRequest], None]) -> None:
        """
        Add a hook that is called before each request.

        Args:
            hook: Function that accepts an `HttpRequest` object.
        """
        self._request_hooks.append(hook)

    def add_response_hook(self, hook: Callable[[HttpResponse], None]) -> None:
        """
        Add a hook that is called after each response (before error checking).

        Args:
            hook: Function that accepts an `HttpResponse` object.
        """
        self._response_hooks.append(hook)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()
