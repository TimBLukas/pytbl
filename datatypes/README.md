# `datatypes`

Shared type aliases for paths, JSON values, mappings, callables, time values,
HTTP data, configuration, logging, and async code. Import aliases from the
package rather than repeating complex annotations.

```python
from pathlib import Path
from datatypes import Headers, JsonObject, PathLike

def load_config(path: PathLike) -> JsonObject:
    return {"path": str(Path(path))}

headers: Headers = {"Accept": "application/json"}
```

`http_return_codes` also exposes HTTP status-code constants used by the HTTP
client.
