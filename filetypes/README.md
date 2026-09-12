# `filetypes`

The `filetypes` namespace groups helpers for common text-based formats.
Choose the format-specific package (`jsonx`, `yamlx`, `xmlx`, `htmlx`, `inix`,
or `envx`) and import its public API.

```python
from filetypes.jsonx import read_json
from filetypes.yamlx import read_yaml

data = read_json("data.json")
settings = read_yaml("settings.yaml")
```

Each child package documents its optional dependencies and format-specific
behavior.
