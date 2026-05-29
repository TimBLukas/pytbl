import requests
from .exceptions import HTTPError


class HttpClient:
    def __init__(
        self, base_url: str = "", timeout: int = 10, headers: dict | None = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(headers or {})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"
