# `logging`

Logging helpers that preserve the standard-library logging API while adding
cached logger creation, file rotation, reconfiguration, and function-call
tracing.

```python
from logging import get_logger, log_function_call

logger = get_logger("worker")

@log_function_call(logger)
def add(left: int, right: int) -> int:
    return left + right

logger.info("result=%s", add(2, 3))
```

Use `set_default_logging_config` before creating application loggers when a
shared configuration is required.
