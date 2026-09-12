# `cli`

Command-line design notes for applications built with `pytbl`. `args.py`
currently records planned abstractions for typed arguments, subcommands,
validation, configuration precedence, standardized output, and testing. It
does not yet expose a stable parser API.

Until that API is implemented, use Python's standard `argparse` module:

```python
import argparse

parser = argparse.ArgumentParser(description="Example command")
parser.add_argument("--verbose", action="store_true")
options = parser.parse_args()
```

Consult `args.py` before building integrations against this experimental area.
