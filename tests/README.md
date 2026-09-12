# `tests`

Repository test support and tests for `pytbl`. `BaseTestCase` provides
temporary files, environment patching, output capture, and useful assertions.

```python
from tests.base import BaseTestCase

class TestConfig(BaseTestCase):
    def test_file(self):
        path = self.create_temp_file("ok", suffix=".txt")
        self.assertFileContent(path, "ok")
```

Run the suite from the repository root with `python -m pytest`.
