# -----------------------------------------------------
# Standard Library Imports
# -----------------------------------------------------
import os
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString as parse_xml_string

# -----------------------------------------------------
# Library Specific Imports
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

try:
        from jinja2 import Template, Environment, FileSystemLoader
        JINJA_AVAILABLE = True
except ImportError:
        JINJA_AVAILABLE = False

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
        """Convert PathLike to a Path object"""
        return Path(path) if isinstance(path, str) else path

def _ensure_cache(path: PathLike, reload: bool = False) -> Any:
        """
        Load or reload a YAML file into the global cache

        Args:
                path: Path to the YAML file
                reload: Force reload even if cached version seems up to date

        Returns:
                Parsed YAML data (dict, list, etc.)
        """
        global _CACHE_DATA, _CACHE_MTIME, _CACHE_PATH
        target = _normalize_path(path).resolve()
        current_mtime = target.stat().st_mtime if target.exists() else 0

        cache_valid = (
                _CACHE_PATH == target
                and _CACHE_MTIME == current_mtime
                and not reload
        )

        if not cache_valid:
                if not target.exists():
                        raise FileNotFoundError(f"YAML file not found: {target}")
                
                with target.open('r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)

                _CACHE_DATA = data
                _CACHE_MTIME = current_mtime
                _CACHE_PATH = target

        return _CACHE_DATA

def _write_yaml_data(
        data: Any,
        path: PathLike,
        indent: Optional[int] = 2,
        atomic: bool = True,
        default_flow_style: bool = False
) -> None:
        """
        Write YAML data to a file, optionally atomically        

        Args:
                data: YAML serializable data
                path: Destination file path
                indent: Indentation spaces (None for extra indentation)
                atomic: If True, write via a temporary file, then rename
                default_flow_stye: Passed to yaml.dump (False for block style)
        """
        if not YAML_AVAILABLE:
                raise ImportError(f"PyYAML is required for YAML operations, Install with pip install pyyaml")
        
        target = _normalize_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        yaml_str =  yaml.dump(data, indent=indent, default_flow_style=default_flow_style, allow_unicode=True)

        if atomic:
                fd, temp_path = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        f.write(yaml_str)
                os.replace(temp_path, target)
        else:
                target.write_text(temp_path, target)

        # invalidate cache
        global _CACHE_DATA, _CACHE_MTIME, _CACHE_PATH
        if _CACHE_PATH == target:
                _CACHE_PATH = None


def _deep_merge(base: Dict, override: Dict) -> Dict:
        """
        Recursively merge two dictionaries 

        Args:
                base: Base dictionary
                override: Dictionary whose values override those in base

        Returns:
                Dict: Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = _deep_merge(result[key], value)

                else:
                        result[key] = value

        return result


def _dict_to_xml(data: Any, root_tag: str = "root") -> ET.Element:
        """
        Convert a dictionary to an XML Element.

        Args:
                data: Dictionary (or list) to convert
                root_tag: Tag name for the root Element

        Returns:
                XML Element
        """
        def build(parent, obj):
                if isinstance(obj, dict):
                        for key, val in obj.items():
                                if isinstance(val, list):
                                        for item in val:
                                                child = ET.SubElement(parent, key)
                                                build(child, item)
                                elif isinstance(val, dict):
                                        child = ET.SubElement(parent, key)
                                        build(child, val)

                                else:
                                        child = ET.SubElement(parent, key)
                                        child.text = str(val)

                elif isinstance(obj, list):
                        for item in obj:
                                build(parent, item)
                
                else:
                        parent.text = str(obj)

        root = ET.Element(root_tag)
        build(root, data)

        return root


def _xml_to_dict(element: ET.Element) -> Any:
        """
        Convert an XML Element to a dictionary 

        Args:
                element: XML Element

        Returns:
                Dictionary representation
        """
        result = {}
        for child in element:
                if len(child) == 0:
                        # Leaf element
                        result[child.tag] = child.text
                else:
                        # Nested element
                        child_dict = _xml_to_dict(child)
                        if child.tag in result:
                                if not isinstance(result[child.tag], list):
                                        result[child.tag] = [result[child.tag]]
                                result[child.tag].append(child_dict)

                        else:
                                result[child.tag] = child.dict

        return result or element.text




# -------------------------------------------------------------
# Public Facing API
# -------------------------------------------------------------
def read_yaml(path: PathLike, use_cache: bool = True) -> Any:
        """
        Read and parse a YAML file

        Args:
                path: Path to the YAML file
                use_cache: if True, use a cache keyed by file modification time

        Returns:
                Parsed YAML data (dict, list, etc.)

        Raises:
                FileNotFoundError: If the file does not exist
                ImportError: If PyYaml is not installed
                yaml.YAMLError: If the file is not valid Yaml

        Example:
                >>> data = read_yaml("config.yaml")
                >>> data['database']['host']
                'localhost'
        """
        if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required. Install via pip install pyyaml")

        if use_cache:
                return _ensure_cache(path)

        target = _normalize_path(path)
        with target.open('r', encoding='utf-8') as f:
                return yaml.safe_load(f)


def write_yaml(
        path: PathLike,
        data: Any,
        indent: Optional[int] = 2,
        atomic: bool = True,
        default_flow_style: bool = False
) -> None:
        """
        Write YAML data to a file 

        Args:
                path: Destination file path
                data: YAML-serializable data
                atomic: If True, write atomically via temporary file
                default_flow_style: If False, use block style, if True, use flow style

        Example:
                >>> write_yaml("output.yaml", {"name": "Alice", "age": 30})
        """
        _write_yaml_data(data, path, indent=indent, atomic=atomic, default_flow_style=default_flow_style)


def merge_yaml(
        base_path: PathLike,
        override_path: PathLike,
        output_path: Optional[PathLike] = None,
        *,
        inplace: bool = False
):
        """
        Merge two YAML files, with the second overriding the first 

        Args:
                base_path: Base YAML file
                override_path: Override YAML file
                output_path: If provided, write the merged result to this file
                inplace: If True, write back to base_path (ignored if output_path is set)

        Returns:
                If output_path is None, returns the merged dictionary, otherwise None

        Example:
                >>> merged = merge_yaml("defaults.yaml", "local.yaml")
                >>> merge_yaml("defaults.yaml", "local.yaml", output_path="merged.yaml")
        """
        base_data = read_yaml(base_path)
        override_data = read_yaml(override_path)


        if not isinstance(base_data, dict) or not isinstance(override_data, dict):
                raise TypeError("Both YAML files must contain dictionaries at the root for merging.")

        merged = _deep_merge(base_data, override_data)

        if output_path:
                write_yaml(output_path, merged)
                return None
        elif inplace:
                write_yaml(base_path, merged)
                return None
        return merged


def yaml_template(
        template_path: PathLike,
        context: Dict[str, Any],
        output_path: Optional[PathLike] = None
) -> Optional[str]:
        """
        Render a YAML file as a Jinja2 template.

        Args:
                template_path: Path to the YAML template file.
                context: Variables to substitute in the template.
                output_path: If provided, write the rendered YAML to this file.

        Returns:
                Rendered YAML string (if output_path is None), otherwise None.

        Raises:
                ImportError: If Jinja2 is not installed.
                FileNotFoundError: If template file does not exist.
                yaml.YAMLError: If the rendered content is not valid YAML.

        Example:
                >>> context = {'app_name': 'MyApp', 'port': 8080}
                >>> yaml_template("config.tmpl.yaml", context, "config.yaml")
                """
        if not JINJA_AVAILABLE:
                raise ImportError("Jinja2 is required for templating. Install with: pip install jinja2")

        template_path = _normalize_path(template_path)
        if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")

        env = Environment(loader=FileSystemLoader(template_path.parent))
        template = env.get_template(template_path.name)
        rendered = template.render(**context)

        # Validate the rendered YAML
        try:
                yaml.safe_load(rendered)
        except yaml.YAMLError as e:
                raise ValueError(f"Rendered template is not valid YAML: {e}")

        if output_path:
                output_path = _normalize_path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(rendered, encoding='utf-8')
                return None
        return rendered


def yaml_to_dict(path: PathLike) -> Dict:
        """
        Read a YAML file and return it as a dictionary (convenience wrapper).

        Args:
                path: Path to the YAML file.

        Returns:
                Dictionary representation.

        Raises:
                TypeError: If the YAML root is not a dictionary.
        """
        data = read_yaml(path)
        if not isinstance(data, dict):
                raise TypeError(f"Expected a dictionary, got {type(data)}")
        return data


# ------------------------------------------
# Conversion functions
# ------------------------------------------
def to_json(yaml_path: PathLike, json_path: Optional[PathLike] = None, indent: int = 2) -> Optional[str]:
        """
        Convert a YAML file to JSON.

        Args:
                yaml_path: Path to the input YAML file.
                json_path: If provided, write JSON to this file; otherwise return JSON string.
                indent: Indentation for the JSON output.

        Returns:
                JSON string if json_path is None, otherwise None.
        """
        data = read_yaml(yaml_path)
        json_str = json.dumps(data, indent=indent, ensure_ascii=False)

        if json_path:
                json_path = _normalize_path(json_path)
                json_path.parent.mkdir(parents=True, exist_ok=True)
                json_path.write_text(json_str, encoding='utf-8')
                return None
        return json_str


def to_yaml(yaml_path: PathLike, output_path: Optional[PathLike] = None, indent: int = 2) -> Optional[str]:
        """
        Read a YAML file and write it back (essentially a pretty-print / format operation).

        Args:
                yaml_path: Path to the input YAML file.
                output_path: If provided, write formatted YAML to this file; otherwise return YAML string.
                indent: Indentation spaces.

        Returns:
                YAML string if output_path is None, otherwise None.
        """
        data = read_yaml(yaml_path)
        yaml_str = yaml.dump(data, indent=indent, allow_unicode=True, default_flow_style=False)

        if output_path:
                _write_yaml_data(data, output_path, indent=indent)
                return None
        return yaml_str


def to_xml(yaml_path: PathLike, xml_path: Optional[PathLike] = None, root_tag: str = "root") -> Optional[str]:
        """
        Convert a YAML file to XML.

        Args:
                yaml_path: Path to the input YAML file.
                xml_path: If provided, write XML to this file; otherwise return XML string.
                root_tag: Tag name for the root XML element.

        Returns:
                XML string if xml_path is None, otherwise None.
        """
        data = read_yaml(yaml_path)
        root = _dict_to_xml(data, root_tag)
        xml_str = ET.tostring(root, encoding='unicode')
        # Pretty-print
        dom = parse_xml_string(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        if xml_path:
                xml_path = _normalize_path(xml_path)
                xml_path.parent.mkdir(parents=True, exist_ok=True)
                xml_path.write_text(pretty_xml, encoding='utf-8')
                return None
        return pretty_xml


def from_json(json_path: PathLike, yaml_path: Optional[PathLike] = None, indent: int = 2) -> Optional[str]:
        """
        Convert a JSON file to YAML.

        Args:
                json_path: Path to the input JSON file.
                yaml_path: If provided, write YAML to this file; otherwise return YAML string.
                indent: Indentation for the YAML output.

        Returns:
                YAML string if yaml_path is None, otherwise None.
        """
        with open(_normalize_path(json_path), 'r', encoding='utf-8') as f:
                data = json.load(f)
        yaml_str = yaml.dump(data, indent=indent, allow_unicode=True, default_flow_style=False)

        if yaml_path:
                _write_yaml_data(data, yaml_path, indent=indent)
                return None
        return yaml_str


def from_yaml(yaml_path: PathLike, output_path: Optional[PathLike] = None) -> Optional[Dict]:
        """
        Read a YAML file and return the parsed data (alias for yaml_to_dict with return).
        This is mainly for symmetry with from_json/from_xml.

        Args:
                yaml_path: Path to the input YAML file.
                output_path: If provided, write the data back as YAML (no conversion).

        Returns:
                Parsed dictionary if output_path is None, otherwise None.
        """
        data = read_yaml(yaml_path)
        if output_path:
                write_yaml(output_path, data)
                return None
        return data


def from_xml(xml_path: PathLike, yaml_path: Optional[PathLike] = None, indent: int = 2) -> Optional[str]:
        """
        Convert an XML file to YAML.

        Args:
                xml_path: Path to the input XML file.
                yaml_path: If provided, write YAML to this file; otherwise return YAML string.
                indent: Indentation for the YAML output.

        Returns:
                YAML string if yaml_path is None, otherwise None.
        """
        tree = ET.parse(_normalize_path(xml_path))
        root = tree.getroot()
        data = {root.tag: _xml_to_dict(root)}
        yaml_str = yaml.dump(data, indent=indent, allow_unicode=True, default_flow_style=False)

        if yaml_path:
                _write_yaml_data(data, yaml_path, indent=indent)
                return None
        return yaml_str
