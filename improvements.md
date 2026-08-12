# Improvements

## Improvements to make

### Critical

- Make package metadata consistent across `setup.py`, `pyproject.toml`, and `LICENSE`.

### Important

- Add module-level docstrings and short examples for public APIs.
- Normalize naming (`read_*`, `write_*`, `to_*`, `from_*`) across modules.
- Reduce optional dependency confusion by documenting extras.

### Nice to have

- Add richer type hints throughout the codebase.
- Add CLI entry points for common conversions.
- Add benchmark or smoke-test coverage for large file operations.
- Add a top-level facade module for easier importing.

## Suggested priority order

1. Conflict cleanup
2. Bug fixes
3. Tests
4. Packaging/documentation consistency
5. API polish
