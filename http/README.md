# `http`

An HTTP client built on `requests` with base URLs, default headers, retries,
timeouts, hooks, typed request/response models, and focused exceptions.

```python
from http import HttpClient, HttpClientConfig

client = HttpClient(
    "https://api.example.com",
    config=HttpClientConfig(timeout=10, max_retries=2),
)
response = client.get("/health")
print(response.status_code, response.json())
```

Install `requests` before importing this package. Transport and HTTP status
failures are surfaced through the exceptions exported by `http`.
