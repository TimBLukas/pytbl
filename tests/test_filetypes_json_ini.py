"""Tests for JSON and INI helpers."""

import configparser
import importlib
import json
import tempfile
import unittest
from pathlib import Path

jsonx = importlib.import_module("filetypes.jsonx.json_core_functions")
inix = importlib.import_module("filetypes.inix.ini_core_functions")


class TestJsonHelpers(unittest.TestCase):
    """Cover JSON file helpers and conversions."""

    def setUp(self) -> None:
        jsonx._CACHE_PATH = None
        jsonx._CACHE_DATA = None
        jsonx._CACHE_MTIME = 0.0
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_read_write_append_delete(self) -> None:
        path = self.root / "data.json"
        data = {"user": {"name": "Ada", "roles": ["admin", "editor"]}}

        jsonx.write_json(path, data)
        self.assertEqual(jsonx.read_json(path), data)

        jsonx.append_json(path, {"active": True})
        self.assertEqual(jsonx.read_json(path), [{"user": {"name": "Ada", "roles": ["admin", "editor"]}}, {"active": True}])

        array_path = self.root / "items.json"
        jsonx.write_json(array_path, {"items": [{"name": "a"}, {"name": "b"}]})
        jsonx.delete_json(array_path, "items")
        self.assertEqual(jsonx.read_json(array_path), {})

    def test_delete_nested_and_cache_reload(self) -> None:
        path = self.root / "nested.json"
        jsonx.write_json(path, {"user": {"profile": {"name": "Ada", "city": "Paris"}}})
        jsonx.delete_json(path, "user.profile.city")
        self.assertEqual(jsonx.read_json(path), {"user": {"profile": {"name": "Ada"}}})

        path.write_text(json.dumps({"value": 2}), encoding="utf-8")
        self.assertEqual(jsonx.read_json(path, use_cache=False), {"value": 2})

    def test_validation_and_formatting(self) -> None:
        path = self.root / "valid.json"
        path.write_text('{"a": 1, "b": [true, null]}', encoding="utf-8")
        self.assertTrue(jsonx.validate_json(path))
        self.assertTrue(jsonx.validate_json('{"a": 1}'))
        self.assertFalse(jsonx.validate_json('{"a": 1'))

        self.assertEqual(jsonx.minify_json('{"a": 1, "b": 2}'), '{"a":1,"b":2}')
        self.assertEqual(jsonx.prettify_json('{"a":1,"b":2}', None, indent=2), '{\n  "a": 1,\n  "b": 2\n}')

    def test_tabular_and_tree_conversions(self) -> None:
        json_path = self.root / "rows.json"
        json_path.write_text(
            json.dumps(
                {
                    "people": [
                        {"name": "Ada", "meta": {"age": 36}},
                        {"name": "Bob", "meta": {"age": 29}},
                    ]
                }
            ),
            encoding="utf-8",
        )

        csv_path = self.root / "rows.csv"
        jsonx.json_to_csv(json_path, csv_path, array_key="people")
        csv_data = csv_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(csv_data[0], "meta.age,name")

        converted = jsonx.csv_to_json(csv_path)
        self.assertEqual(converted[0]["name"], "Ada")
        self.assertEqual(converted[1]["meta.age"], 29)

        xml_text = jsonx.json_to_xml(json_path, root_tag="people")
        self.assertIn("<people>", xml_text)

        xml_path = self.root / "rows.xml"
        xml_path.write_text(xml_text, encoding="utf-8")
        self.assertEqual(
            jsonx.xml_to_json(xml_path),
            {
                "people": {
                    "people": [
                        {"name": "Ada", "meta": {"age": "36"}},
                        {"name": "Bob", "meta": {"age": "29"}},
                    ]
                }
            },
        )

    def test_yaml_paths_raise_import_error(self) -> None:
        self.assertFalse(jsonx.YAML_AVAILABLE)
        with self.assertRaises(ImportError):
            jsonx.json_to_yaml(self.root / "data.json")
        with self.assertRaises(ImportError):
            jsonx.yaml_to_json(self.root / "data.yaml")


class TestIniHelpers(unittest.TestCase):
    """Cover INI helpers and conversions."""

    def setUp(self) -> None:
        inix._CACHE_PATH = None
        inix._CACHE_PARSER = None
        inix._CACHE_MTIME = 0.0
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_read_write_and_lookup(self) -> None:
        path = self.root / "settings.ini"
        data = {"database": {"host": "localhost", "port": "5432"}}
        inix.write_ini(path, data)

        parser = inix.read_ini(path)
        self.assertIsInstance(parser, configparser.ConfigParser)
        self.assertEqual(inix.read_ini_as_dict(path), data)
        self.assertEqual(inix.get_ini_value(path, "database", "host"), "localhost")
        self.assertEqual(inix.get_ini_value(path, "missing", "value", fallback="fallback"), "fallback")

    def test_update_flatten_and_exports(self) -> None:
        path = self.root / "settings.ini"
        inix.write_ini(path, {"database": {"host": "localhost"}})
        inix.set_ini_value(path, "database", "port", "5432")
        self.assertEqual(inix.get_ini_value(path, "database", "port"), "5432")
        self.assertEqual(inix.flatten_ini(path)["database.host"], "localhost")

        json_text = inix.to_json(path)
        self.assertIn('"database"', json_text)
        self.assertFalse(inix.YAML_AVAILABLE)
        with self.assertRaises(ImportError):
            inix.to_yaml(path)

    def test_ini_errors(self) -> None:
        path = self.root / "empty.ini"
        inix.write_ini(path, {"app": {"name": "pytbl"}})
        with self.assertRaises(configparser.NoSectionError):
            inix.set_ini_value(path, "missing", "key", "value", create_section=False)
