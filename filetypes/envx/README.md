# `filetypes.envx`

Environment and `.env` helpers with typed accessors, required-value checks,
validation, snapshots, scoped overrides, and secret redaction.

```python
from filetypes.envx import get_int, redacted_dict, temporary

with temporary({"PORT": "8080"}):
    assert get_int("PORT") == 8080

safe_for_logs = redacted_dict()
```

Use `require` for mandatory configuration and never print `as_dict()` when it
may contain credentials; use `redacted_dict()` instead.
