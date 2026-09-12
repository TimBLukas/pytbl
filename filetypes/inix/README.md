# `filetypes.inix`

INI configuration helpers for parsing, writing, accessing individual values,
flattening sections, and exporting to JSON or YAML.

```python
from filetypes.inix import get_ini_value, read_ini_as_dict, set_ini_value

settings = read_ini_as_dict("settings.ini")
host = settings.get("server", {}).get("host", "localhost")
set_ini_value("settings.ini", "server", "host", host)
print(get_ini_value("settings.ini", "server", "host"))
```

INI values are strings, as they are in `configparser`. YAML export requires
`pyyaml`.
