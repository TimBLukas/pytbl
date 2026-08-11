# ------------------------------------------
# Standard Library imports
# ------------------------------------------
import os
import tempfile
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString as parse_minidom_string
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator, Callable
from collections import defaultdict

# ------------------------------------------
# Library specific imports
# ------------------------------------------
from datatypes import PathLike

# ------------------------------------------
# External Imports (optional)
# ------------------------------------------
try:
    from lxml import etree as lxml_etree

    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

# ------------------------------------------
# Globals (caching)
# ------------------------------------------
_CACHE_PATH: Optional[Path] = None
_CACHE_TREE: Optional[ET.ElementTree] = None
_CACHE_MTIME: float = 0.0


# ------------------------------------------
# Private Helper Functions
# ------------------------------------------
def _normalize_path(path: PathLike) -> Path:
    return Path(path) if isinstance(path, str) else path


def _ensure_cache(path: PathLike, reload: bool = False) -> ET.ElementTree:
    """
    Load XML file and cache Element Tree
    """
    global _CACHE_PATH, _CACHE_MTIME, _CACHE_TREE
    target = _normalize_path(path).resolve()
    current_mtime = target.stat().st_mtime

    cache_valid = target == _CACHE_PATH and current_mtime == _CACHE_MTIME and not reload

    if not cache_valid:
        if not target.exists():
            raise FileNotFoundError(f"XML file not found: {target}")

        tree = ET.parse(target)
        _CACHE_PATH = target
        _CACHE_TREE = tree
        _CACHE_MTIME = current_mtime

    return _CACHE_TREE


def _element_to_dict(element: ET.Element) -> Dict:
    """
    Recursively convert an XML Element to a dictionary.
    Repeated tags become lists.
    """
    result = {}

    if element.attrib:
        result["@attributes"] = element.attrib

    # Process children
    children = list(element)

    if children:
        child_dict = {}
        for child in children:
            child_data = _element_to_dict(child)
            if child.tag in child_dict:
                if not isinstance(child_dict[child.tag], list):
                    child_dict[child.tag] = [child_dict[child.tag]]
                child_dict[child.tag].append(child_data)

            else:
                child_dict[child.tag] = child_data

        result.update(child_dict)

    else:
        # Leaf node
        text = element.text.strip() if element.text else ""

        if text:
            result["#text"] = text

    # if the element has only text and no attributes / children, return just the text
    if len(result) == 1 and "#text" in result and not element.attrib:
        return result["#text"]

    return result


def _dict_to_element(tag: str, data: Any) -> ET.Element:
    """Convert a dictionary or primitive to an XML Element."""
    element = ET.Element(tag)

    if isinstance(data, dict):
        # handle attributes
        if "@attributes" in data:
            for attr, value in data["@attributes"].items():
                element.set(attr, str(value))
            data.pop("@attributes")

        # Process children
        for key, value in data.items():
            if key == "#text":
                element.text = str(value)

            else:
                if isinstance(value, list):
                    for item in value:
                        child = _dict_to_element(key, item)
                        element.append(child)

                else:
                    child = _dict_to_element(key, value)
                    element.append(child)

    else:
        # primitive data -> use text
        element.text = str(data)

    return element


def _pretty_xml(xml_str: str) -> str:
    """Pretty-print an XML string using minidom."""
    dom = parse_minidom_string(xml_str)
    return dom.toprettyxml(indent="  ")


def _xpath_with_lxml(
    tree: ET.ElementTree, xpath_expr: str, namespaces: Optional[Dict] = None
) -> List[Any]:
    """Use lxml for full xpath support"""
    if not LXML_AVAILABLE:
        raise ImportError(
            "lxml is required for full XPath support. Install with pip install lxml"
        )

    # convert ElementTree to lxml
    root = tree.getroot()
    lxml_root = lxml_etree.fromstring(ET.tostring(root))

    result = lxml_root.xpath(xpath_expr, namespaces=namespaces or {})
    # convert lxml back to Etree for consistency

    converted = []
    for node in result:
        if isinstance(node, lxml_etree._Element):
            converted.append(ET.fromstring(lxml_etree.tostring(node)))
        else:
            converted.append(node)
    return converted


def xpath_with_etree(tree: ET.ElementTree, xpath_expr: str) -> List[Any]:
    """Limited XPath support using Etree"""
    # ET supports only a subset: tag names, wildcard, attributes, predicates
    try:
        return tree.findall(xpath_expr)

    except SyntaxError:
        # Fallback
        if xpath_expr.startswith("."):
            xpath_expr = xpath_expr[1:]
        if xpath_expr.startswith("/"):
            xpath_expr = xpath_expr[1:]
        return tree.findall(f".//{xpath_expr}")


# ------------------------------------------
# Public Facing API – Reading & Parsing
# ------------------------------------------


def read_xml(path: PathLike, use_cache: bool = True) -> ET.ElementTree:
    """
    Read an XML file and return an ElementTree.

    Args:
        path: Path to the XML file.
        use_cache: If True, cache by file modification time.

    Returns:
        xml.etree.ElementTree.ElementTree object.

    Raises:
        FileNotFoundError: If the file does not exist.
        ET.ParseError: If the XML is malformed.
    """
    if use_cache:
        return _ensure_cache(path)

    target = _normalize_path(path)
    return ET.parse(target)


def parse_xml_string(xml_string: str) -> ET.Element:
    """
    Parse an XML string and return the root Element.

    Args:
        xml_string: XML content as string.

    Returns:
        Root Element.
    """
    return ET.fromstring(xml_string)


def read_xml_as_dict(path: PathLike) -> Dict:
    """
    Read XML and convert to dictionary.

    Args:
        path: Path to the XML file.

    Returns:
        Dictionary representation.
    """
    tree = read_xml(path)
    return _element_to_dict(tree.getroot())


def xpath_query(
    path: PathLike, xpath_expr: str, namespaces: Optional[Dict] = None
) -> List[Any]:
    """
    Execute an XPath query on an XML file.

    Args:
        path: Path to the XML file.
        xpath_expr: XPath expression.
        namespaces: Optional namespace mapping.

    Returns:
        List of matching nodes (strings or elements).

    Requires lxml (if not available, falls back to limited ET support).
    """
    tree = read_xml(path)
    if LXML_AVAILABLE:
        return _xpath_with_lxml(tree, xpath_expr, namespaces)

    else:
        # ElementTree doesn't support namespaces well, ignore them
        return xpath_with_etree(tree, xpath_expr)


# ------------------------------------------
# Public Facing API – Writing & Creating
# ------------------------------------------
def write_xml(
    path: PathLike,
    root_element: Union[ET.Element, ET.ElementTree],
    pretty: bool = True,
    atomic: bool = True,
) -> None:
    """
    Write an XML element or tree to a file.

    Args:
        path: Destination file path.
        root_element: Element or ElementTree to write.
        pretty: If True, format the XML with indentation.
        atomic: If True, write atomically via temporary file.
    """
    target = _normalize_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Convert to ElementTree if needed
    if isinstance(root_element, ET.Element):
        tree = ET.ElementTree(root_element)

    else:
        tree = root_element

    # Generate XML string
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8")
    xml_str = xml_bytes.decode("utf-8")
    if pretty:
        xml_str = _pretty_xml(xml_str)

    if atomic:
        fd, temp_path = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(xml_str)
        os.replace(temp_path, target)

    else:
        target.write_text(xml_str, encoding="utf-8")

    # Invalidate cache if written file matches cached path
    global _CACHE_PATH, _CACHE_TREE
    if _CACHE_PATH == target:
        _CACHE_TREE = None


def create_xml(root_tag: str, data: Optional[Dict] = None, **attributes) -> ET.Element:
    """
    Create an XML Element from a dictionary (nested dicts become child elements).

    Args:
        root_tag: Tag name for the root element.
        data: Nested dictionary representing the XML structure.
        **attributes: Attributes for the root element.

    Returns:
        Element object.

    Example:
        >>> root = create_xml('person', {'name': 'Alice', 'age': 30}, id='123')
        >>> ET.tostring(root)
        b'<person id="123"><name>Alice</name><age>30</age></person>'
    """
    root = _dict_to_element(root_tag, data or {})
    for attr, value in attributes.items():
        root.set(attr, str(value))

    return root


def create_xml_file(
    root_tag: str, data: Dict, output_path: PathLike, pretty: bool = True
) -> None:
    """
    Create an XML file from a dictionary (wrapper).

    Args:
        root_tag: Root element name.
        data: Dictionary representation.
        output_path: Destination file path.
        pretty: Whether to format the output.
    """
    root = create_xml(root_tag, data)
    write_xml(output_path, root, pretty=pretty)


# ------------------------------------------
# Public Facing API – Modifying & Searching
# ------------------------------------------
def find_elements(tree: ET.ElementTree, tag: str) -> List[ET.Element]:
    """
    Find all elements with a given tag name (recursive).
    """
    return tree.findall(f".//{tag}")


def set_element_text(tree: ET.ElementTree, xpath: str, new_text: str) -> bool:
    """
    Set the text of the first element matching an XPath.

    Returns:
        True if an element was found and modified, False otherwise.
    """
    if LXML_AVAILABLE:
        root = tree.getroot()
        lxml_root = lxml_etree.fromstring(ET.tostring(root))
        elements = lxml_root.xpath(xpath)

        if elements:
            elements[0].text = new_text
            # Convert back to ET
            new_root = ET.fromstring(lxml_etree.tostring(lxml_root))
            tree._setroot(new_root)
            return True

    else:
        # Use ET's limited find
        elem = tree.find(xpath)
        if elem is not None:
            elem.text = new_text
            return True

    return False


def append_child(
    tree: ET.ElementTree, parent_xpath: str, new_element: ET.Element
) -> bool:
    """
    Append a child element to the first parent matching XPath.

    Returns:
        True if parent was found, False otherwise.
    """
    parent = tree.find(parent_xpath)
    if parent is not None:
        parent.append(new_element)
        return True

    return False


def remove_elements(tree: ET.ElementTree, xpath: str) -> int:
    """
    Remove all elements matching an XPath.

    Returns:
        Number of removed elements.
    """
    removed = 0

    # Find all matching elements (use findall with limited XPath or lxml)
    if LXML_AVAILABLE:
        root = tree.getroot()
        lxml_root = lxml_etree.fromstring(ET.tostring(root))
        matches = lxml_root.xpath(xpath)
        for match in matches:
            parent = match.getparent()

            if parent is not None:
                parent.remove(match)
                removed += 1

        if removed > 0:
            # Convert back to ET
            new_root = ET.fromstring(lxml_etree.tostring(lxml_root))
            tree._setroot(new_root)

    else:
        # ET: limited support, assume xpath is a simple tag
        for elem in tree.findall(xpath):
            parent = tree.getroot().find(f".//{elem.tag}/..")

            if parent is not None:
                parent.remove(elem)
                removed += 1

    return removed


def merge_xml(
    base_path: PathLike, override_path: PathLike, output_path: Optional[PathLike] = None
) -> Optional[ET.ElementTree]:
    """
    Merge two XML files (naive: override replaces overlapping elements).

    Returns:
        Merged tree if output_path is None, else None.
    """
    base_tree = read_xml(base_path)
    override_tree = read_xml(override_path)

    base_root = base_tree.getroot()
    override_root = override_tree.getroot()

    def merge_element(target: ET.Element, source: ET.Element):
        """Recursively merge source into target."""
        source_children = {child.tag: child for child in source}

        for target_child in list(target):
            if target_child.tag in source_children:
                merge_element(target_child, source_children[target_child.tag])
                # Remove from source dict so we know it was processed
                del source_children[target_child.tag]

        for tag, child in source_children.items():
            target.append(child)

    merge_element(base_root, override_root)

    if output_path:
        write_xml(output_path, base_tree)
        return None

    return base_tree


# ------------------------------------------
# Public Facing API – Validation
# ------------------------------------------
def validate_xml_schema(xml_path: PathLike, xsd_path: PathLike) -> bool:
    """
    Validate an XML file against an XSD schema.

    Requires lxml.

    Args:
        xml_path: Path to XML file.
        xsd_path: Path to XSD schema.

    Returns:
        True if valid, False otherwise.

    Raises:
        ImportError: If lxml is not installed.
    """
    if not LXML_AVAILABLE:
        raise ImportError(
            "lxml is required for schema validation. Install with: pip install lxml"
        )

    try:
        with open(xsd_path, "rb") as f:
            schema_root = lxml_etree.XML(f.read())

        schema = lxml_etree.XMLSchema(schema_root)

        with open(xml_path, "rb") as f:
            xml_doc = lxml_etree.XML(f.read())

        return schema.validate(xml_doc)

    except Exception:
        return False
