"""Tests for the HTTP client package."""

import importlib.util
import sys
import types
import unittest
from dataclasses import dataclass
from pathlib import Path


class FakeRequestException(Exception):
    pass


class FakeConnectionError(FakeRequestException):
    pass


class FakeTimeout(FakeRequestException):
    pass


class FakeTooManyRedirects(FakeRequestException):
    pass


class FakeRetry:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeHTTPAdapter:
    def __init__(self, max_retries=None):
        self.max_retries = max_retries


@dataclass
class FakeResponse:
    status_code: int = 200
    reason: str = "OK"
    headers: dict[str, str] | None = None
    text: str = "{}"
    content: bytes = b"{}"

    def __post_init__(self) -> None:
        if self.headers is None:
            self.headers = {"Content-Type": "application/json"}


class FakeSession:
    response = FakeResponse()
    exception = None

    def __init__(self):
        self.headers = {}
        self.mounted = {}
        self.calls = []
        self.closed = False

    def mount(self, prefix, adapter):
        self.mounted[prefix] = adapter

    def request(self, **kwargs):
        self.calls.append(kwargs)
        if self.exception is not None:
            raise self.exception
        return self.response

    def close(self):
        self.closed = True


def load_http_package():
    repo_root = Path(__file__).resolve().parents[1]
    package_dir = repo_root / "http"

    requests_pkg = types.ModuleType("requests")
    adapters_pkg = types.ModuleType("requests.adapters")
    exceptions_pkg = types.ModuleType("requests.exceptions")
    packages_pkg = types.ModuleType("requests.packages")
    urllib3_pkg = types.ModuleType("requests.packages.urllib3")
    urllib3_util_pkg = types.ModuleType("requests.packages.urllib3.util")
    retry_pkg = types.ModuleType("requests.packages.urllib3.util.retry")

    requests_pkg.Session = FakeSession
    requests_pkg.adapters = adapters_pkg
    requests_pkg.exceptions = exceptions_pkg
    requests_pkg.packages = packages_pkg

    adapters_pkg.HTTPAdapter = FakeHTTPAdapter
    exceptions_pkg.ConnectionError = FakeConnectionError
    exceptions_pkg.Timeout = FakeTimeout
    exceptions_pkg.TooManyRedirects = FakeTooManyRedirects
    exceptions_pkg.RequestException = FakeRequestException
    retry_pkg.Retry = FakeRetry
    urllib3_util_pkg.retry = retry_pkg
    urllib3_pkg.util = urllib3_util_pkg
    packages_pkg.urllib3 = urllib3_pkg

    modules = {
        "requests": requests_pkg,
        "requests.adapters": adapters_pkg,
        "requests.exceptions": exceptions_pkg,
        "requests.packages": packages_pkg,
        "requests.packages.urllib3": urllib3_pkg,
        "requests.packages.urllib3.util": urllib3_util_pkg,
        "requests.packages.urllib3.util.retry": retry_pkg,
    }

    spec = importlib.util.spec_from_file_location(
        "pytbl_http",
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    original = {name: sys.modules.get(name) for name in modules}
    try:
        sys.modules.update(modules)
        sys.modules["pytbl_http"] = module
        spec.loader.exec_module(module)
    finally:
        for name, value in original.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value

    return module


http_pkg = load_http_package()


class TestHttpModelsAndErrors(unittest.TestCase):
    """Cover request/response models and HTTP errors."""

    def test_config_defaults(self) -> None:
        config = http_pkg.HttpClientConfig()
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertTrue(config.raise_for_status)

    def test_response_helpers(self) -> None:
        request = http_pkg.HttpRequest("GET", "https://example.com")
        response = http_pkg.HttpResponse(
            status_code=200,
            reason="OK",
            headers={"Content-Type": "application/json"},
            text='{"name": "Ada"}',
            content=b'{"name": "Ada"}',
            elapsed=0.1,
            request=request,
        )

        self.assertTrue(response.ok)
        self.assertEqual(response.json(), {"name": "Ada"})

        error_response = http_pkg.HttpResponse(
            status_code=404,
            reason="Not Found",
            headers={},
            text="{}",
            content=b"{}",
            elapsed=0.1,
            request=request,
        )
        with self.assertRaises(http_pkg.HTTPStatusError) as cm:
            error_response.raise_for_status()
        self.assertIn("HTTP 404", str(cm.exception))

    def test_module_exports(self) -> None:
        self.assertIn("HttpClient", http_pkg.__all__)
        self.assertIn("raise_for_status", http_pkg.__all__)


class TestHttpClient(unittest.TestCase):
    """Cover client creation, hooks, and error translation."""

    def setUp(self) -> None:
        FakeSession.response = FakeResponse()
        FakeSession.exception = None

    def test_client_builds_requests_and_makes_calls(self) -> None:
        client = http_pkg.HttpClient(
            base_url="https://api.example.com",
            headers={"X-Test": "1"},
            timeout=7,
            max_retries=2,
            retry_backoff_factor=0.5,
        )

        request_events = []
        response_events = []
        client.add_request_hook(request_events.append)
        client.add_response_hook(response_events.append)

        response = client.get("/users", params={"page": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.method, "GET")
        self.assertEqual(response.request.url, "https://api.example.com/users?page=1")
        self.assertEqual(response.request.headers["X-Test"], "1")
        self.assertEqual(request_events[0].url, response.request.url)
        self.assertEqual(response_events[0].status_code, 200)
        self.assertIn("http://", client.session.mounted)
        self.assertIn("https://", client.session.mounted)

        posted = client.post("/submit", json_data={"name": "Ada"})
        self.assertEqual(posted.request.method, "POST")
        self.assertEqual(posted.request.json, {"name": "Ada"})
        client.close()
        self.assertTrue(client.session.closed)

    def test_client_translates_request_exceptions(self) -> None:
        client = http_pkg.HttpClient(base_url="https://api.example.com")
        FakeSession.exception = FakeTimeout("timeout")

        with self.assertRaises(http_pkg.TimeoutError):
            client.get("/slow")

    def test_raise_for_status_helper(self) -> None:
        request = http_pkg.HttpRequest("GET", "https://example.com")
        response = http_pkg.HttpResponse(
            status_code=500,
            reason="Server Error",
            headers={},
            text="{}",
            content=b"{}",
            elapsed=0.1,
            request=request,
        )

        with self.assertRaises(http_pkg.HTTPStatusError):
            http_pkg.raise_for_status(response)
