"""Small helpers for loading application configuration from files and environment variables."""

from __future__ import annotations

import json
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


class ConfigError(ValueError):
    """Raised when a configuration file cannot be loaded."""


def _read_json_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ConfigError(f"JSON configuration in {path} must contain an object.")
    return loaded


def _read_ini_config(path: Path) -> dict[str, Any]:
    parser = ConfigParser()
    parser.read(path, encoding="utf-8")
    config: dict[str, Any] = {}
    for section in parser.sections():
        config[section] = {key: value for key, value in parser.items(section)}
    return config


def _read_toml_config(path: Path) -> dict[str, Any]:
    if tomllib is None:
        raise ConfigError("TOML support requires Python 3.11+ or tomli to be installed.")
    with path.open("rb") as handle:
        loaded = tomllib.load(handle)
    if not isinstance(loaded, dict):
        raise ConfigError(f"TOML configuration in {path} must contain a table.")
    return loaded


def _read_yaml_config(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ConfigError(f"YAML support requires PyYAML: {exc}") from exc

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ConfigError(f"YAML configuration in {path} must contain a mapping.")
    return loaded


def read_config_file(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a config file from JSON, INI, TOML, or YAML."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration file does not exist: {config_path}")

    suffix = config_path.suffix.lower()
    if suffix == ".json":
        return _read_json_config(config_path)
    if suffix in {".ini", ".cfg"}:
        return _read_ini_config(config_path)
    if suffix == ".toml":
        return _read_toml_config(config_path)
    if suffix in {".yaml", ".yml"}:
        return _read_yaml_config(config_path)
    raise ConfigError(f"Unsupported config format: {config_path.suffix or 'unknown'}")


def merge_dicts(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge nested dictionaries."""

    merged = {**base}
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def _env_mapping(prefix: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        normalized = key[len(prefix):].lower().replace("__", ".")
        values[normalized] = value
    return values


def load_config(
    path: str | os.PathLike[str] | None = None,
    *,
    defaults: Mapping[str, Any] | None = None,
    env_prefix: str | None = None,
) -> dict[str, Any]:
    """Load configuration from defaults, file, and environment variables.

    Precedence is: CLI values > environment variables > config file > defaults.
    """

    config: dict[str, Any] = {}
    if defaults:
        config = dict(defaults)
    if path is not None:
        config = merge_dicts(config, read_config_file(path))
    if env_prefix:
        config = merge_dicts(config, _env_mapping(env_prefix))
    return config


def resolve_config(
    *,
    defaults: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
    env: Mapping[str, Any] | None = None,
    cli: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve configuration with the precedence CLI > ENV > file > defaults."""

    merged: dict[str, Any] = {}
    if defaults:
        merged = dict(defaults)
    if config:
        merged = merge_dicts(merged, dict(config))
    if env:
        merged = merge_dicts(merged, dict(env))
    if cli:
        merged = merge_dicts(merged, dict(cli))
    return merged
