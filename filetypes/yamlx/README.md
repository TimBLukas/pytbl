# `filetypes.yamlx`

YAML helpers for reading, writing, deep merging, Jinja2 templating, and
conversion to JSON or XML.

```python
from filetypes.yamlx import merge_yaml, read_yaml, write_yaml

write_yaml("base.yaml", {"service": {"host": "localhost", "port": 8000}})
write_yaml("local.yaml", {"service": {"port": 8080}})
merge_yaml("base.yaml", "local.yaml", "settings.yaml")
print(read_yaml("settings.yaml"))
```

Install `pyyaml` for all operations and `jinja2` when using `yaml_template`.
