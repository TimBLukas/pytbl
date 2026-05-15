# ------------------------------------------
# Library specific imports
# ------------------------------------------
from datatypes import PathLike

# ------------------------------------------
# Standard Library imports
# ------------------------------------------
import configparser
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, overload
import time
from datetime import datetime

# ------------------------------------------
# External Imports
# ------------------------------------------

try:
    import yaml # PyYAML required for to_yaml()
    YAML_AVAILABLE = True

except ImportError:
    YAML_AVAILABLE = False


# ------------------------------------------
# Globals
# ------------------------------------------

_CACHE_PATH: Optional[Path] = None
_CACHE_PARSER: Optional[configparser.ConfigParser] = None
_CACHE_MTIME: float = 0.0


# ------------------------------------------
# Private Helper Functions 
# ------------------------------------------

def _normalize_path(path: PathLike) -> Path:
    """
    Convert a PathLike Object to a Path object 

    Args:
        path: PathLike (str or Path)
    
    Returns:
        Path: Normalized Path Object
    """
    if isinstance(path, str):
        return Path(path)
    return path

def _ensure_cache(path: PathLike, reload: bool=False) -> configparser.ConfigParser:
    """
    Load or reload INI file into the global cache

    The cache is keyed by the absolute path and file modification time.
    If the file has  changed on disk or reload=True, the cache is refreshed.

    Args:
        path: Path to the INI File
    
    Returns:
        configparser.ConfigParser: Cached ConfigParser Object.
    
    Raises:
        FileNotFoundError: If the file does not exist
        configparser.Error: If the INI file is malformed
    """
    global _CACHE_PATH, _CACHE_PARSER, _CACHE_MTIME

    target = _normalize_path(path)
    current_mtime = target.stat().st_mtime if target.exists() else 0

    cache_valid = (
        _CACHE_PATH == target
        and _CACHE_PARSER is not None
        and (not reload)
        and current_mtime == _CACHE_MTIME
    )

    if not cache_valid:
        if not target.exists():
            raise FileNotFoundError(f"INI File not found: {target}")
        parser = configparser.ConfigParser()
        parser.read(target)

        _CACHE_PARSER = parser
        _CACHE_MTIME = current_mtime
        _CACHE_PATH = target

    return _CACHE_PARSER

def _validate_section_key(section: str, key: str) -> None:
    """
    Validate that section and key names are non-empty strings.

    Args:
        section: SEction name
        key: Key name

    Raises:
        ValueError: If either is empty or not a string
    """
    if not isinstance(section, str) or not section.strip():
        raise ValueError("Section name must be a non-empty String")

    if not isinstance(key, str) or not key.strip():
        raise ValueError("Key name must be a non-empty String")

def _write_config_to_file(parser: configparser.ConfigParser, path: PathLike) -> None:
    """
    Write a ConfigParser object to a file atomically (via temporary file).

    Args:
        parser: ConfigParser to write
        path: Destination file path
    """
    target = _normalize_path(path)

    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open('w', encoding='utf-8') as f:
        parser.write(f)


# ------------------------------------------
# Public Facing API
# ------------------------------------------
def read_ini(path: PathLike) -> configparser.ConfigParser:
    """
    Read an INI file and return a ConfigParser object (with caching).

    The result is cached by file path and modification time. Subsequent
    calls with the same unchanged file return the cached object.

    Args:
        path: Path to the INI file (string or Path).

    Returns:
        configparser.ConfigParser: Parser containing all sections and keys.

    Raises:
        FileNotFoundError: If the file does not exist.
        configparser.Error: If the file is not a valid INI.

    Example:
        >>> config = read_ini("settings.ini")
        >>> config["database"]["host"]
        'localhost'
    """
    return _ensure_cache(path)


def read_ini_as_dict(path: PathLike) -> Dict[str, Dict[str, str]]:
    """
    Read an INI file and return its content as a nested dictionary 

    The dictionary structure: {section: {key: value, ...}, ...}
    All values are strings read from the file

    Args:
        path: Path to the INI File
    
    Returns:
        dict: Nested dictionary representation

    Example:
        >>> data = read_ini_as_dict("config.ini")
        >>> data["logging"]["level"]
        'INFO'
    """
    parser = read_ini(path)
    return {section: dict(parser[section]) for section in parser.sections()}


def write_ini(path: PathLike, data: Dict[str, Dict[str, str]]) -> None:
    """
    Write a dictionary to an INI File.

    The dictionary must have the structure {section: {key: value, ...}, ...}
    All values will be written as strings

    Args:
        path: Destionation file path
        data: Dictionary to write
    
    Raises:
        TypeError: If data is not a dictionary of dictionaries
        ValueError: If section or key names are invalid

    Example:
        >>> data = {"database": {"host": "localhost", "port": "5432"}}
        >>> write_ini("config.ini", data)
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary of dictionaries")

    parser = configparser.ConfigParser()
    for section, values in data.items():
        if not isinstance(section, str):
            raise TypeError(f"Section '{section}' must be a string, got {type(section).__name__}")
        if not isinstance(values, dict):
            raise TypeError(f"Section '{section}' must contain a dictionary of key-value pairs")

        parser[section] = {str(k): str(v) for k, v in values.items()}
    _write_config_to_file(parser, path)

    # invalidate cache because file has changed
    global _CACHE_PATH, _CACHE_PARSER, _CACHE_MTIME
    if _CACHE_PATH == _normalize_path(path).resolve():
        _CACHE_PARSER = None


def get_ini_value(
    path: PathLike,
    section: str,
    key: str,
    fallback: Any = None,
    *,
    use_cache: bool = True
) -> Any:
    """
    Get a single Value from an INI File, with an optional Fallback

    This functinoi uses the internal cache for efficency. If the key or section does not exist, the fallback is returned (default: None)

    Args:
        path: Path to the INI File
        section: Section name in the INI file
        key: Key name within the section
        fallback: Value to return if section or key is not found (default: None)
        use_cache: Whether to use the internal cache (default: True), if False bypasses the cache and reads directly from disk, useful for testing or when you know the file has changed outside of this module.

    Returns:
        The value as a string (or fallback if missing)

    Example:
        >>> host = get_ini_value("config.ini", "database", "host", "localhost")
        'localhost'
    """
    _validate_section_key(section, key)
    if use_cache:
        parser = _ensure_cache(path)

    else:
        parser = configparser.ConfigParser()
        parser.read(_normalize_path(path))

    try:
        return parser.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return fallback


def set_ini_value(
    path: PathLike,
    section: str,
    key: str,
    value: str,
    *,
    create_section: bool = True
) -> None:
    """
    Set a single value in an INI File and write back to disk

    The file is read into memory  (using the cache), the value is updated and then
    the entire file is rewritten 

    Args:
        path: Path to the INI File
        section: SEction name
        key: key name
        value: Value to write (will be converted to a string)
        create_section: If True, create the section fi it does not exist
                        Otherwise raises an error if section is missing

    Returns:
        configparser.NoSectionError: If section does not exist and create_section=False
        FileNotFoundError: If the file does not exist and cannot be created

    Example:
        >>> set_ini_value("config.ini", "database", "port", "5432")
    """
    _validate_section_key(section, key)
    target = _normalize_path(path)

    if target.exists():
        parser = _ensure_cache(target)
    else:
        parser = configparser.ConfigParser()

    if not parser.has_section(section):
        if create_section:
            parser.add_section(section)
        else:
            raise configparser.NoSectionError(section)
        
    parser.set(section, key, str(value))
    _write_config_to_file(parser, target)

def flatten_ini(
    path_or_parser: Union[PathLike, configparser.ConfigParser]
) -> Dict[str, str]:
    """
    Flatten an INI File or Config Parser into a single dictionary with dotted keys
    {"section.key": value}

    Useful for easy lookups and merging with other config sources

    Args:
        path_or_parser: Either a PathLike to and INI File, or a ConfigParser instance

    Returns:
        dict: Flattened dictionary with keys like "section.option"
    
    Example:
        >>> flat = flatten_ini("settings.ini")
        >>> flat["database.host"]
        'localhost'
    """
    if isinstance(path_or_parser, (str, Path)):
        parser = read_ini(path_or_parser)
    else:
        parser = path_or_parser

    result = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            result[f"{section}.{key}"] = value

    return result


def to_json(
        ini_path: PathLike,
        json_path: Optional[PathLike] = None,
        *,
        indent: int = 2,
) -> Optional[str]:
    """
    Convert and INI file to JSON.

    Args:
        ini_path: Path to the input INI File 
        json_path: If provided, write JSON to this file, otherwise return JSON string
        indent: Number of spaces for pretty-printing (default = 2)

    Returns:
        if json_path is None, retursn the JSON string, otherwise returns Noen
    
    Raises:
        TypeError: If ini_path does not point to a valid INI    

    Example:
        >>> json_str = to_json("config.ini")
        >>> to_json = ("config.ini", "config.json")
    """
    data = read_ini_as_dict(ini_path)
    json_output = json.dumps(data, indent=indent)

    if json_path:
        target = _normalize_path(json_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json_output, encoding="utf-8")
        return None

    return json_output


def to_yaml(
    ini_path: PathLike,
    yaml_path: Optional[PathLike] = None,
    *,
    default_flow_style: bool = False
) -> Optional[str]:
    """
    Convert an INI File to YAML
    
    Requires the PyYAML library (install with `pip install pyyaml`)

    Args:
        ini_path: Path to the input INI file
        yaml_path: If provided,d write YAML to this file, otherwise return YAML string
        default_flow_style: Passed to yaml.dump (False for block style, True for flow)

    Returns:
        if yaml_path is None, returns the YAML string, else returns None

    Raises:
        ImportError: If PyYAML is not installed    
        TypeError: if ini_path does not point to a valid INI

    Example:
        >>> yaml_str = to_yaml("config.ini")
        >>> to_yaml("config.ini", "config.yaml")
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYaml is required for to_yaml(). Install with pip install pyyaml")

    data = read_ini_as_dict(ini_path)
    yaml_output = yaml.dump(data, default_flow_style=default_flow_style)

    if yaml_path:
        target = _normalize_path(yaml_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml_output, encoding="utf-8")
        return None

    return yaml_output
    

