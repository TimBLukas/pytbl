# -----------------------------------------------------
# Standard Library Imports
# -----------------------------------------------------
import os
import json
import csv 
import io
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, TextIO, overload
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString as parse_xml_string
import time
from datetime import datetime
import tempfile
from collections import defaultdict

# -----------------------------------------------------
# Standard Library Imports
# -----------------------------------------------------
from datatypes import PathLike

# -----------------------------------------------------
# External Imports
# -----------------------------------------------------
try:
        import yaml
        YAML_AVAILABLE = True
except ImportError:
        YAML_AVAILABLE = False

# -----------------------------------------------------
# Globals
# -----------------------------------------------------
# Cache stores: (path, data, mtime)
_CACHE_PATH: Optional[Path] = None
_CACHE_DATA: Any = None
_CACHE_MTIME: float = 0.0


# -----------------------------------------------------
# Private Helpers
# -----------------------------------------------------
def _normalize_path(path: PathLike) -> Path:
        """
        Convert a PathLike object to a Path object

        Args:
                path: PathLike (str or Path)
        
        Returns:
                Path: Normalized Path object

        Raises:
                TypeError: If path is not a string or Path
        """
        return Path(path) if isinstance(path, str) else path

def _ensure_cache(path: PathLike, reload: bool = False) -> Any:
        """
        Load or reload a JSON file into the global cache 

        The cache is keyed by the absolute path and file modification time
        If the file has changed on disk or reload=True, the cache is refreshed

        Args:
                path: Path to the JSON file
                reload: Force reload even if the cache version seems up-to-date
        
        Reurns:
                Parsed JSON data (dict, list, etc.)
        
        Raises:
                FileNotFoundError: If the file does not exist
                json.JSONDecodeError: If the file is not valid JSON
        """
        global _CACHE_PATH, _CACHE_DATA, _CACHE_MTIME
        target = _normalize_path(path).resolve()
        current_mtime = target.stat().st_mtime if target.exists() else 0

        cache_valid = (
                _CACHE_PATH == target
                and (not reload)
                and (current_mtime == _CACHE_MTIME)
        )

        if not cache_valid:
                if not target.exists():
                        raise FileNotFoundError(f"JSON File not found: {target}")

                with target.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                
                _CACHE_PATH = target
                _CACHE_DATA = data
                _CACHE_MTIME = current_mtime

        return _CACHE_DATA

def _write_json_data(
        data: Any,
        path: PathLike,
        indent: Optional[int] = None,
        atomic: bool = True
) -> None:
        """
        Write JSON data to a file, optionally atomically

        Args:
                data: JSON-serializable data         
                path: Destination file path
                indent: Number of spaces for pretty printing (None for compact)
                atomic: If True, write to a temprary file then rename
        """
        target = _normalize_path(path)

        target.parent.mkdir(parents=True, exist_ok=True)

        if atomic:
                fd, temp_path = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=indent)
                os.replace(temp_path, target) 
        else:
                with target.open('w', encoding='utf-8') as f:
                        json.dump(data, f, indent=indent)

        global _CACHE_PATH, _CACHE_DATA, _CACHE_MTIME
        if _CACHE_PATH == target:
                _CACHE_DATA = None


def _get_nested_value(data: Any, key_path: str) -> Any:
        """
        Retrieve a value from nested dict/list using dot notation
        Support list indices: "users.0.name"

        Args:
                data: JSON data (dict/list)
                key_path: Dot-seperated path (e.g., "database.host" or "users.0.email")

        Returns:
                value at the path

        Raises:
                KeyError: if a dictionary key is missing
                IndexError: If a list index is out of range
        """
        parts = key_path.split('.')
        current = data

        for part in parts:
                if isinstance(current, dict):
                        if part not in current:
                                raise KeyError(f"Key '{part}' not found")
                        current = current[part]
                elif isinstance(current, list):
                        try:
                                idx = int(part)
                        except ValueError:
                                raise KeyError(f"Cannot traverse into non-container: {type(current)}")
                        current = current[idx]
                else:
                        raise TypeError(f"Cannott traverse into non-container: {type(current)}")
        return current

def _set_nested_value(data: Any, key_path: str, value: Any) -> None:
        """
        Set a value in nested dict/list using dot notation, creating intermediate dicts if needed 
        Does NOT create mmissing list elements

        Args:
                data: JSON data (dict/list)
                key_path: Dot-seperated path
                value: Value to set

        Raises:
                IndexError: If a list index is out of range
        """
        parts = key_path.split('.')
        current = data

        for i, part in enumerate(parts[:-1]):
                if isinstance(current, dict):
                        if part not in current or not isinstance(current[part], (dict, list)):
                                current[part] = {}
                        current = current[part]

                elif isinstance(current, list):
                        try:
                                idx = int(part)
                        except ValueError:
                                raise KeyError(f"Cannot use non-integer: '{part}' on list")
                        if idx >= len(current):
                                raise IndexError(f"List Index {idx} out of range")

                        current = current[idx]

                else:
                        raise TypeError(f"Cannot traverse into non-container: {type(current)}")

        last = parts[-1]
        if isinstance(current, dict):
                current[last] = value

        elif isinstance(current, list):
                try:
                        idx = int(last)

                except ValueError:
                        raise KeyError(f"Cannot use non-integer '{last}' on list")
                if idx >= len(current):
                        raise IndexError(f"List index {idx} out of range")
                current[idx] = value
        else:
                raise TypeError(f"Cannot set value on non-container: {type(current)}")

        
def _delete_nested_value(data: Any, key_path: str) -> None:
        """
        Delete a key or list elent from nested JSON using dot notation.

        Args:
                data: JSON data
                key_path: Dot seperated path 

        Raises:
                KeyError: if a dictionary key is missing
                IndexError: If a list index is out of range
        """
        parts = key_path.split('.')
        current = data

        for i, part in enumerate(parts[:-1]):
                if isinstance(current, dict):
                        if part not in current:
                                raise KeyError(f"Key '{part}' not found")

                        current =  current[part]
                elif isinstance(current, list):
                        try:
                                idx = int(part)
                        except ValueError:
                                raise KeyError(f"Cannot use non-integer '{part}' on list")
                        current = current[idx]

                else:
                        raise TypeError(f"Cannot traverse into non-container: {type(current)}")

        last = parts[-1]
        if isinstance(current, dict):
                del current[last]
        elif isinstance(current, list):
                try:
                        idx = int(last)
                except ValueError:
                        raise KeyError(f"Cannot use non-integer '{last}' on list")
                del current[idx]
        else:
                raise TypeError(f"Cannot delete value on non-container: {type(current)}")



# -----------------------------------------------------
# Public Facing API
# -----------------------------------------------------
def read_json(
        path: PathLike,
        use_cache: bool = True
) -> Any:
        """
        Read and parse a JSON File

        Args:
                path: Path to the JSON file
                use_cache: If True, use a cache keyed by file modification time
        
        Returns:
                Parsed JSON data (dict, list, etc.)
        
        Raises:
                FileNotFoundErrro: If the file does not exist
                json.JSONDecodeError: If the file is not valid JSON

        Example:
                >>> data = read_json("config.json")
                >>> data["database"]["host"]
                'localhost'
        """
        if use_cache:
                return _ensure_cache(path)
        else:
                target = _normalize_path(path)
                with target.open('r', encoding='utf-8') as f:
                        return json.load(f)


def write_json(
        path: PathLike,
        data: Any,
        indent: Optional[int] = 2,
        atomic: bool = True
) -> None:
        """
        Write JSON data to a file

        Args:
                path: Destination file path
                data: JSON-serializable data
                indent: Number of spaces for pretty-printing (None for compact) default = 2
                atatomic: If True, write atomically via temporary file

        Example:
                >>> write_json("output.json", {"name": "Alice", "age": 20})
        """
        _write_json_data(data, path, indent=indent, atomic=atomic)

def append_json(
        path: PathLike,
        item: Any,
        *,
        ensure_list: bool = True
) -> None:
        """
        Append an item to a JSON array stored in a file.

        If the file does not exist, a new array containing `item` is created
        If the file exists butt its root is not an array, behaviour depends on `ensure_list`

        Args:
                path: Path to the JSON file
                item: Item to append (any JSON-serializable value)
                ensure_list: If True and the root is not an array, replace the root with a new array `[existing_root, item]`.
                                If False, raises TypeError

        Raises:
                TypeError: If the root is not an array and ensure_list is False
                json.JSONDecodeError: if the file is not valid JSON
        
        Example:
                >>> append_json("log.json", {"event": "start", "time": 12345})
                >>> append_json("log.json", {"event": "stop", "time": 12350})
        """
        target = _normalize_path(path)
        data = None
        if target.exists():
                with target.open('r', encoding='utf-8') as f:
                        data = json.load(f)

        if data is None:
                # New file: create array with item
                new_data = [item]

        elif isinstance(data, list):
                new_data = data + [item]
        
        else:
                if ensure_list:
                        new_data = [data, item]        
                else:
                        raise TypeError("JSON root is not an array; cannot append. Set ensure_list=True to wrap")
                
        _write_json_data(new_data, target, indent=2)


def delete_json(
        path: PathLike,
        key_path: str,
        *,
        use_cache: bool = True
) -> None:
        """
        Delete a key or list element from a JSON file using dot notation

        The key_path supports:
                - Dictionary key: "database.host"
                - List indices: "users.0.email"
                - Mixed: "users.0.adress.city"
        
        Args:
                path: Path to the JSON file
                key_path: Dot-seperated path to the element to delete.
                use_cache: Use cached version of the file

        Raises:
                KeyError: If a dictionary key does not exists
                IndexError: If a list index is out of range
                FileNotFoundError: If the file does not exist

        Example:
                >>> delete_json("config.json", "database.password")
                >>> delete_json("data.json", "users.2")
        """
        data = read_json(path, use_cache=use_cache)
        _delete_nested_value(data, key_path)
        write_json(path, data)


def validate_json(source: Union[PathLike, str]) -> bool:
        """
        Check if a string or file contains valid JSON

        Args:
                source: Either a file or a string        

        Returns:
                True if the JSON is valid, False otherwise

        Example:
                >>> validate_json('{"name": "Alice"}')        
                True
                >>> validate_json('{"name": "Alice"') # missing closing bracket        
                False
                >>> validate_json("data.json")        
                True
        """
        try:
                if isinstance(source, (str, Path)):
                        # Try file                   
                        try:
                                with open(source, 'r', encoding='utf-8') as f:
                                        json.load(f)
                                return True
                        except (FileNotFoundError, IsADirectoryError, PermissionError):
                                # Try as string
                                json.loads(source)
                                return True

                else:
                        # Assume string
                        json.loads(source)
                        return True
        except json.JSONDecodeError:
                return False


def minify_json(
        source: Union[PathLike, str],
        output_path: Optional[PathLike] = None
) -> Optional[str]:
        """
        Remove all optional whitespace from a JSON file or string

        Args:
                source: Path to a JSON file, or JSON string
                output_path: if provided, write minified JSON to this file, otherwise return minified JSON as string

        Returns:
                if output_path is None, returns the minified string, otherwise returns None
        
        Example:
                >>> minify_json("pretty.json", "minified.json")
                >>> compact = minify_json('{"a": 1, "b": 2}')
                '{"a": 1, "b": 2}'
        """
        if isinstance(source, (str, Path)) and (Path(source).exists()):
                data = read_json(source)
        else:
                data = json.loads(source)

        minified = json.dumps(data, separators=(',', ':'))

        if output_path is not None:
                _write_json_data(data, output_path, indent=None)
                return None
        return minified


def prettify_json(
        source: Union[PathLike, str],
        output_path: Optional[PathLike],
        indent: int = 2
) -> Optional[str]:
        """
        Format JSON with indentation for readability

        Args:
                source: Path to JSON file or a JSON string
                output_path: If provided, write prettified jSON to this file
                                Otherwise return the prettified string
                indent: Number of spaces per indent level
        
        Returns:
                If output_path is None, returns the prettified JSON string, else returns None
        
        Example:
                >>> prettify_json("minified.json", "pretty.json")
                >>> pretty = prettify_json('{"a":1,"b":2}')        
                '{\\n "a": 1,\\n "b": 2\\n}'
        """
        if isinstance(source, (str, Path)) and Path(source).exists():
                data = read_json(source)

        else:
                data = json.loads(source)

        pretty = json.dumps(data, indent=indent)

        if output_path is not None:
                _write_json_data(data, output_path, indent=indent)
                return None
        return pretty


def json_to_csv(
        json_path: PathLike,
        csv_path: PathLike,
        *,
        array_key: Optional[str] = None,
        flatten: bool = True
) -> None:
        """
        Convert a JSON file to CSV

        The JSON should be an array of objects (each object becomes a row)
        If the JSON root is an object, specify `array_key` to extract the array
        Nested objects are falttened with dot notation (e.g., "adress.city")

        Args:
                json_path: Path to the input JSON file
                csv_path: Path to the output CSV file
                array_key: If the JSON root is an object, the key containing the array
                flatten: If True, flatten nested objects, if False, raise on nested data

        Raises:
                TypeError: If JSON root is not an array and array_key is not provided.
                ValueError: If flatten=False and any row contains a nested dict or list        

        Example:
                >>> json_to_csv("users.join", "users.csv", array_key="users")        
        """
        data = read_json(json_path)

        if isinstance(data, dict) and array_key:
                rows = data[array_key]
        elif isinstance(data, list):
                rows = data

        else:
                raise TypeError("JSON root must be an array or an object with array_key")

        if not rows:
                # Empty array -> write nothing
                return

        def get_keys(obj, parent=''):
                keys = set()
                for k, v in obj.items():
                        full = f"{parent}.{k}" if parent else k
                        if flatten and isinstance(v, dict):
                                keys.update(get_keys(v, full))
                        else:
                                keys.add(full)

                return keys

        fieldnames = set()

        for row in rows:
                if not isinstance(row, dict):
                        raise  TypeError(f"Each row must be a dict, got {type(row)}")
                fieldnames.update(get_keys(row))

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()

                for row in rows:
                        flat_row = {}

                        def flatten_row(obj, parent=''):
                                for k, v in obj.items():
                                        full = f"{parent}.{k}" if parent else k
                                        if flatten and isinstance(v, dict):
                                                flatten_row(v, full)
                                        else:
                                                if isinstance(v, (dict, list)):
                                                        v = json.dumps(v)
                                                flat_row[full] = v
                        flatten_row(row)
                        writer.writerow(flat_row)


def csv_to_json(
    csv_path: PathLike,
    json_path: Optional[PathLike] = None,
    *,
    array_name: str = "items",
    encoding: str = 'utf-8'
) -> Optional[List[Dict]]:
        """
        Convert a CSV file to JSON.

        The first row is used as headers. Each subsequent row becomes a JSON object.
        If json_path is provided, the result is written to a JSON file; otherwise
        the list of objects is returned.

        Args:
                csv_path: Path to the input CSV file.
                json_path: If provided, write JSON to this file; otherwise return data.
                array_name: Name of the root array key (only when writing to file).
                encoding: File encoding.

        Returns:
                If json_path is None, returns a list of dicts (the JSON array).
                Otherwise returns None.

        Example:
                >>> data = csv_to_json("data.csv")
                >>> csv_to_json("data.csv", "output.json", array_name="records")
        """
        result = []
        with open(csv_path, 'r', newline='', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                        converted = {}
                        for k, v in row.items():
                                if v.lower() == 'true':
                                        converted[k] = True
                                elif v.lower() == 'false':
                                        converted[k] = False
                                elif v.lower() == 'null' or v == '':
                                        converted[k] = None
                                else:
                                        try:
                                                converted[k] = int(v)
                                        except ValueError:
                                                try:
                                                        converted[k] = float(v)
                                                except ValueError:
                                                        converted[k] = v
                        result.append(converted)

        if json_path is not None:
                write_json(json_path, {array_name: result})
                return None
        return result


def json_to_xml(
        json_path: PathLike,
        xml_path: Optional[PathLike] = None,
        root_tag: str = "root"
) -> Optional[str]:
        """
        Convert a JSON file to XML.

        The JSON structure is mapped:
                - Objects become XML elements with child elements.
                - Arrays become repeated elements with the same tag (plural -> singular).
                - Primitive values become text content.

        For arrays, the tag name is inferred from the parent key (e.g., "users" -> "user").
        If no plural→singular rule is found, the array key is used for each element.

        Args:
                json_path: Path to the input JSON file.
                xml_path: If provided, write XML to this file; otherwise return XML string.
                root_tag: Tag name for the root element.

        Returns:
                If xml_path is None, returns the XML string; otherwise None.

        Example:
                >>> json_to_xml("data.json", "data.xml", root_tag="configuration")
        """
        data = read_json(json_path)

        def build_xml(parent, obj, tag=None):
                if isinstance(obj, dict):
                        for key, value in obj.items():
                                if isinstance(value, list):
                                        # Convert plural to singular for element tag
                                        if key.endswith('ies'):
                                                child_tag = key[:-3] + 'y'
                                        elif key.endswith('s'):
                                                child_tag = key[:-1]
                                        else:
                                                child_tag = key
                                        for item in value:
                                                child = ET.SubElement(parent, child_tag)
                                                build_xml(child, item, child_tag)
                                elif isinstance(value, dict):
                                        child = ET.SubElement(parent, key)
                                        build_xml(child, value, key)
                                else:
                                        child = ET.SubElement(parent, key)
                                        child.text = str(value)
                else:
                        parent.text = str(obj)

        root = ET.Element(root_tag)
        build_xml(root, data)

        xml_str = ET.tostring(root, encoding='unicode')

        dom = parse_xml_string(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        if xml_path is not None:
                _normalize_path(xml_path).write_text(pretty_xml, encoding='utf-8')
                return None
        return pretty_xml


def xml_to_json(
        xml_path: PathLike,
        json_path: Optional[PathLike] = None,
        *,
        preserve_array_hints: bool = True
) -> Optional[Any]:
        """
        Convert an XML file to JSON.

        The conversion is symmetrical to json_to_xml:
                - Elements become dict keys.
                - Repeated sibling elements become arrays.
                - Attributes are stored with an "@" prefix (optional, but not implemented).

        Args:
                xml_path: Path to the input XML file.
                json_path: If provided, write JSON to this file; otherwise return data.
                preserve_array_hints: If True, convert plural element names to arrays.
                                Otherwise treat all repeated tags as arrays regardless of name.

        Returns:
                If json_path is None, returns the JSON data (dict/list); otherwise None.

        Example:
                >>> data = xml_to_json("config.xml")
                >>> xml_to_json("config.xml", "config.json")
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        def parse_element(elem):
                result = {}
                children = list(elem)
                if not children:
                        return elem.text or ''
                groups = defaultdict(list)
                for child in children:
                        groups[child.tag].append(parse_element(child))

                for tag, values in groups.items():
                        if len(values) == 1 and (not preserve_array_hints or not tag.endswith('s')):
                                result[tag] = values[0]
                        else:
                                result[tag] = values
                return result

        data = {root.tag: parse_element(root)}
        if json_path is not None:
                write_json(json_path, data)
                return None
        return data


def json_to_yaml(
        json_path: PathLike,
        yaml_path: Optional[PathLike] = None,
        *,
        default_flow_style: bool = False
) -> Optional[str]:
        """
        Convert a JSON file to YAML.

        Requires PyYAML.

        Args:
                json_path: Path to the input JSON file.
                yaml_path: If provided, write YAML to this file; otherwise return YAML string.
                default_flow_style: Passed to yaml.dump (True for flow, False for block).

        Returns:
                If yaml_path is None, returns the YAML string; otherwise None.

        Raises:
                ImportError: If PyYAML is not installed.

        Example:
                >>> yaml_str = json_to_yaml("data.json")
                >>> json_to_yaml("data.json", "data.yaml")
        """
        if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required for json_to_yaml(). Install with: pip install pyyaml")

        data = read_json(json_path)
        yaml_str = yaml.dump(data, default_flow_style=default_flow_style, allow_unicode=True)

        if yaml_path is not None:
                _normalize_path(yaml_path).write_text(yaml_str, encoding='utf-8')
                return None
        return yaml_str


def yaml_to_json(
        yaml_path: PathLike,
        json_path: Optional[PathLike] = None,
        *,
        indent: Optional[int] = 2
) -> Optional[Any]:
        """
        Convert a YAML file to JSON.

        Requires PyYAML.

        Args:
                yaml_path: Path to the input YAML file.
                json_path: If provided, write JSON to this file; otherwise return data.
                indent: Indentation for the JSON output (if writing to file).

        Returns:
                If json_path is None, returns the parsed JSON data; otherwise None.

        Raises:
                ImportError: If PyYAML is not installed.

        Example:
                >>> data = yaml_to_json("config.yaml")
                >>> yaml_to_json("config.yaml", "config.json")
        """
        if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required for yaml_to_json(). Install with: pip install pyyaml")

        with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

        if json_path is not None:
                write_json(json_path, data, indent=indent)
                return None
        return data
