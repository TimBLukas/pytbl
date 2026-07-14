"""
HTTP client module - configurable HTTP client with retries and hooks.

Provides an HTTP client built on `requests.Session` with:
- automatic retries
- request/response hooks for logging, auth, etc.
- support for JSON, form data and file uploads
"""

import time
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urljoin, urlencode

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError as e:
    raise ImportError(
        "The `requests` library is required. Install it with: pip install requests"
    ) from e


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


# ------------------------------------------------------------------
# Private helper functions
# ------------------------------------------------------------------

def _merge_dicts(
    base: Dict[str, Any],
    override: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge two dictionaries.

    Used mainly for headers where a shallow merge is sufficient.
    """
    result = base.copy()
    result.update(override)
    return result


def _build_query_params(
    params: Optional[Union[Dict, List[tuple], str]]
) -> str:
    """
    Convert query parameters to URL encoded string.
    """
    if not params:
        return ""

    if isinstance(params, str):
        return params if params.startswith("?") else f"?{params}"

    if isinstance(params, (dict, list)):
        return f"?{urlencode(params)}"

    raise TypeError(
        f"Unsupported query parameter type: {type(params)}"
    )


# ------------------------------------------------------------------
# HttpClient
# ------------------------------------------------------------------

class HttpClient:
    """
    Robust HTTP client with retries, hooks, and session management.

    Example:
        client = HttpClient("https://api.example.com")
        response = client.get("/users")
        print(response.json())
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
        Initialize HTTP client.

        Args:
            base_url:
                Base URL for all requests.

            config:
                Client configuration object.

            headers:
                Default headers.

            timeout:
                Default request timeout.

            max_retries:
                Number of retries.

            retry_backoff_factor:
                Retry delay multiplier.
        """

        self.config = config or HttpClientConfig()

        self.base_url = base_url.rstrip("/")

        self.timeout = (
            timeout
            if timeout is not None
            else self.config.timeout
        )

        max_retries = (
            max_retries
            if max_retries is not None
            else self.config.max_retries
        )

        backoff = (
            retry_backoff_factor
            if retry_backoff_factor is not None
            else self.config.retry_backoff_factor
        )

        self.session = requests.Session()

        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=backoff,
                status_forcelist=self.config.retry_status_codes,
                allowed_methods=self.config.retry_methods,
            )

            adapter = HTTPAdapter(
                max_retries=retry_strategy
            )

            self.session.mount(
                "http://",
                adapter
            )

            self.session.mount(
                "https://",
                adapter
            )

        default_headers = self.config.default_headers.copy()

        if headers:
            default_headers.update(headers)

        self.session.headers.update(default_headers)

        self._request_hooks: List[
            Callable[[HttpRequest], None]
        ] = []

        self._response_hooks: List[
            Callable[[HttpResponse], None]
        ] = []


    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        """
        Join base URL and endpoint path.
        """
        return urljoin(
            self.base_url + "/",
            path.lstrip("/")
        )


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

        full_url = self._url(url)

        if params:
            full_url += _build_query_params(params)

        final_headers = _merge_dicts(
            self.session.headers,
            headers or {}
        )

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


    def _execute_request(
        self,
        request: HttpRequest
    ) -> HttpResponse:

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
            raise ConnectionError(str(e)) from e

        except requests.exceptions.Timeout as e:
            raise TimeoutError(str(e)) from e

        except requests.exceptions.TooManyRedirects as e:
            raise TooManyRedirectsError(str(e)) from e

        except requests.exceptions.RequestException as e:
            raise RequestError(str(e)) from e


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


        for hook in self._response_hooks:
            hook(http_response)


        if self.config.raise_for_status:
            raise_for_status(http_response)


        return http_response


    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def get(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("GET", url, **kwargs)
        )


    def post(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("POST", url, **kwargs)
        )


    def put(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("PUT", url, **kwargs)
        )


    def patch(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("PATCH", url, **kwargs)
        )


    def delete(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("DELETE", url, **kwargs)
        )


    def head(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("HEAD", url, **kwargs)
        )


    def options(self, url: str, **kwargs) -> HttpResponse:
        return self._execute_request(
            self._build_request("OPTIONS", url, **kwargs)
        )


    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def add_request_hook(
        self,
        hook: Callable[[HttpRequest], None]
    ) -> None:
        self._request_hooks.append(hook)


    def add_response_hook(
        self,
        hook: Callable[[HttpResponse], None]
    ) -> None:
        self._response_hooks.append(hook)


    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self):
        return self


    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        self.close()


    def close(self) -> None:
        """
        Close HTTP session.
        """
        self.session.close()