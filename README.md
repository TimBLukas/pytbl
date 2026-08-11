# pytbl

Personal utility library for repeated Python tasks.

It currently includes helpers for:
- file formats: `jsonx`, `yamlx`, `xmlx`, `htmlx`, `inix`, `envx`
- math: `maths`
- networking: `http`
- shared typing helpers: `datatypes`
- lightweight test running: `tests`

## Current state

**Rating: 4/10**

The library has useful breadth and a clear personal-use goal, but it is not yet in a stable, polished state. Some modules are functional and well-scoped, while others contain merge-conflict markers, inconsistent APIs, and correctness bugs that need cleanup before the package is dependable.

## What works well

- Good collection of small, practical utility modules
- Reasonable separation by domain
- Caching support in several file helpers
- Some modules already expose a usable public API

## Main issues

- Merge-conflict markers still exist in source files
- Several modules have inconsistent naming and export patterns
- Some functions appear incomplete or incorrect
- Packaging metadata is inconsistent (`MIT` in setup, `GPL-3.0-or-later` in `pyproject.toml`)
- There is little evidence of automated test coverage

## Module overview

| Module | Status |
| --- | --- |
| `datatypes` | Solid foundation for shared aliases |
| `maths` | Useful, but still basic |
| `jsonx` / `yamlx` / `xmlx` / `htmlx` / `inix` | Promising, but several functions need cleanup |
| `http` | Incomplete / unresolved conflict state |
| `tests` | Minimal runner utilities, not a full test suite |

## Recommended next improvements

1. Resolve all merge conflicts and syntax issues.
2. Add tests for each module’s public API.
3. Standardize packaging metadata and versioning.
4. Document import paths and examples for every module.
5. Tighten error handling and fix broken helpers.
6. Add top-level `__init__.py` exports for stable entry points.

## Usage

See `USAGE.md` for the short package description.

