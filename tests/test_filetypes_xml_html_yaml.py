"""Tests for XML, HTML, and YAML-dependent helpers."""

import importlib
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

xmlx = importlib.import_module("filetypes.xmlx.xml_core_functions")
htmlx = importlib.import_module("filetypes.htmlx.html_core_functions")
yamlx = importlib.import_module("filetypes.yamlx.yaml_core_functions")


class TestXmlHelpers(unittest.TestCase):
    """Cover XML helpers and fallback behavior."""

    def setUp(self) -> None:
        xmlx._CACHE_PATH = None
        xmlx._CACHE_TREE = None
        xmlx._CACHE_MTIME = 0.0
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_read_write_and_query(self) -> None:
        path = self.root / "data.xml"
        root = xmlx.create_xml("person", {"name": "Ada", "age": "36"}, id="1")
        xmlx.write_xml(path, root)

        tree = xmlx.read_xml(path)
        self.assertIsInstance(tree, ET.ElementTree)
        self.assertEqual(xmlx.read_xml_as_dict(path)["name"], "Ada")
        self.assertEqual(xmlx.xpath_query(path, ".//name")[0].text, "Ada")

    def test_create_modify_and_merge(self) -> None:
        path = self.root / "base.xml"
        other = self.root / "other.xml"

        xmlx.write_xml(path, xmlx.create_xml("root", {"item": {"name": "Ada"}}))
        xmlx.write_xml(other, xmlx.create_xml("root", {"item": {"city": "Paris"}, "extra": "value"}))

        tree = xmlx.read_xml(path, use_cache=False)
        self.assertTrue(xmlx.set_element_text(tree, ".//name", "Grace"))
        self.assertTrue(xmlx.append_child(tree, ".//item", ET.Element("role")))
        self.assertEqual(xmlx.remove_elements(tree, ".//role"), 1)

        merged = xmlx.merge_xml(path, other)
        self.assertEqual(merged.getroot().find(".//extra").text, "value")

    def test_xml_validation_requires_lxml(self) -> None:
        self.assertFalse(xmlx.LXML_AVAILABLE)
        with self.assertRaises(ImportError):
            xmlx.validate_xml_schema(self.root / "data.xml", self.root / "schema.xsd")


class TestHtmlHelpers(unittest.TestCase):
    """Cover HTML generation and import-time dependency checks."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_generation_helpers(self) -> None:
        html = htmlx.generate_html("Title", "<p>Hello</p>", style="body { color: red; }")
        self.assertIn("<title>Title</title>", html)
        self.assertIn("<p>Hello</p>", html)
        self.assertIn("color: red", html)

        self.assertEqual(htmlx.tag("a", "Click", href="https://example.com", class_="link"), '<a href="https://example.com" class="link">Click</a>')
        self.assertIn("<th>Name</th>", htmlx.table([["Ada"]], headers=["Name"]))
        self.assertEqual(htmlx.unordered_list(["A", "B"], class_="items"), '<ul class="items"><li>A</li><li>B</li></ul>')
        self.assertEqual(htmlx.ordered_list(["A", "B"]), "<ol><li>A</li><li>B</li></ol>")

        output = self.root / "page.html"
        htmlx.write_html(output, html)
        self.assertTrue(output.exists())

    def test_html_reading_requires_beautifulsoup(self) -> None:
        self.assertFalse(htmlx.BEAUTIFULSOUP_AVAILABLE)
        with self.assertRaises(ImportError):
            htmlx.read_html(self.root / "page.html")
        with self.assertRaises(ImportError):
            htmlx.parse_html_string("<p>Hi</p>")
        with self.assertRaises(ImportError):
            htmlx.extract_text(self.root / "page.html")
        with self.assertRaises(ImportError):
            htmlx.extract_links(self.root / "page.html")
        with self.assertRaises(ImportError):
            htmlx.update_html(self.root / "page.html", "p", "Hello")


class TestYamlHelpers(unittest.TestCase):
    """Cover YAML dependency flags and failure paths."""

    def test_yaml_imports_require_pyyaml(self) -> None:
        self.assertFalse(yamlx.YAML_AVAILABLE)
        self.assertFalse(yamlx.JINJA_AVAILABLE)

        with self.assertRaises(ImportError):
            yamlx.read_yaml("config.yaml")
        with self.assertRaises(ImportError):
            yamlx.write_yaml("config.yaml", {"a": 1})
        with self.assertRaises(ImportError):
            yamlx.merge_yaml("a.yaml", "b.yaml")
        with self.assertRaises(ImportError):
            yamlx.yaml_template("template.yaml", {})
        with self.assertRaises(ImportError):
            yamlx.to_json("config.yaml")
        with self.assertRaises(ImportError):
            yamlx.from_json("config.json")

