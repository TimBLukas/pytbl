# `filetypes.jsonx`

JSON file utilities for reading, writing, validation, formatting, nested-key
updates, and CSV/XML/YAML conversion.

```python
from filetypes.jsonx import read_json, write_json, prettify_json

write_json("settings.json", {"server": {"port": 8080}})
settings = read_json("settings.json")
print(settings["server"]["port"])
print(prettify_json("settings.json"))
```

Use `append_json` for array files and `validate_json` to check a path or JSON
string. YAML conversion additionally requires `pyyaml`.
