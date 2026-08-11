"""Tests for environment variable helpers."""

import importlib
import json
import tempfile
import unittest
from pathlib import Path

envx = importlib.import_module("filetypes.envx.envx_core_functions")


class TestEnvHelpers(unittest.TestCase):
    """Cover core access, typing, validation, and redaction helpers."""

    def setUp(self) -> None:
        self.snapshot = envx.snapshot()
        envx._ENV_CACHE = None
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        envx.restore(self.snapshot)
        envx._ENV_CACHE = None
        self.tempdir.cleanup()

    def test_core_access_and_cache(self) -> None:
        dotenv = self.root / ".env"
        dotenv.write_text("DB_HOST=localhost\nTOKEN=from-file\nEMPTY=\n", encoding="utf-8")
        envx.reload_env(str(dotenv))

        envx.set("DB_HOST", "override")
        self.assertEqual(envx.get("DB_HOST"), "override")
        self.assertTrue(envx.exists("TOKEN"))
        self.assertEqual(envx.require("TOKEN"), "from-file")
        self.assertEqual(envx.get("MISSING", "fallback"), "fallback")
        self.assertEqual(envx.get_prefix("DB_")["DB_HOST"], "override")

    def test_typed_accessors(self) -> None:
        envx.set("INT_VALUE", "42")
        envx.set("FLOAT_VALUE", "3.5")
        envx.set("BOOL_VALUE", "yes")
        envx.set("LIST_VALUE", "a, b, c")
        envx.set("JSON_VALUE", json.dumps({"name": "Ada"}))

        self.assertEqual(envx.get_int("INT_VALUE"), 42)
        self.assertEqual(envx.get_float("FLOAT_VALUE"), 3.5)
        self.assertTrue(envx.get_bool("BOOL_VALUE"))
        self.assertEqual(envx.get_list("LIST_VALUE"), ["a", "b", "c"])
        self.assertEqual(envx.get_json("JSON_VALUE"), {"name": "Ada"})

    def test_merge_snapshot_restore_and_temporary(self) -> None:
        merged = envx.merge_sources(
            dotenv={"A": 1, "B": None},
            env={"A": 2, "C": 3},
            secrets={"C": 4, "D": 5},
            cli={"D": 6, "E": 7},
        )
        self.assertEqual(merged, {"A": "2", "C": "4", "D": "6", "E": "7"})

        original = envx.snapshot()
        envx.set("EXTRA", "value")
        envx.restore(original)
        self.assertIsNone(envx.get("EXTRA"))

        with envx.temporary({"TEMP_VALUE": "1", "EXTRA": None}):
            self.assertEqual(envx.get("TEMP_VALUE"), "1")
            self.assertIsNone(envx.get("EXTRA"))
        self.assertIsNone(envx.get("TEMP_VALUE"))

    def test_secret_detection_and_redaction(self) -> None:
        envx.set("API_TOKEN", "super-secret-token")
        envx.set("PUBLIC_VALUE", "visible")

        self.assertTrue(envx.is_secret("API_TOKEN"))
        self.assertFalse(envx.is_secret("PUBLIC_VALUE"))
        self.assertTrue(envx.mask("API_TOKEN").startswith("su"))
        self.assertEqual(envx.mask("PUBLIC_VALUE"), "visible")

        redacted = envx.redacted_dict()
        self.assertIn("API_TOKEN", redacted)
        self.assertNotEqual(redacted["API_TOKEN"], "super-secret-token")

    def test_require_one_of_and_validation(self) -> None:
        envx.set("PRIMARY_URL", "https://example.com")
        key, value = envx.require_one_of(["MISSING", "PRIMARY_URL"])
        self.assertEqual((key, value), ("PRIMARY_URL", "https://example.com"))

        schema = {
            "PORT": {"required": True, "type": "int", "min": 1, "max": 65535},
            "DEBUG": {"type": "bool"},
            "FEATURES": {"type": "list", "sep": ","},
            "APP_URL": {"type": "url"},
            "APP_PATH": {"type": "path"},
        }
        envx.set("PORT", "8080")
        envx.set("DEBUG", "true")
        envx.set("FEATURES", "one,two")
        envx.set("APP_URL", "https://example.com")
        envx.set("APP_PATH", str(self.root))

        validated = envx.validate(schema)
        self.assertEqual(validated["PORT"], 8080)
        self.assertTrue(validated["DEBUG"])
        self.assertEqual(validated["FEATURES"], ["one", "two"])
        self.assertEqual(validated["APP_URL"], "https://example.com")
        self.assertEqual(validated["APP_PATH"], self.root)

    def test_validation_errors(self) -> None:
        schema = {
            "PORT": {"required": True, "type": "int"},
            "MODE": {"choices": ["dev", "prod"]},
        }
        envx.set("MODE", "test")

        with self.assertRaises(envx.EnvValidationError) as cm:
            envx.validate(schema)

        self.assertIn("Missing required environment variable", str(cm.exception))
        self.assertIn("expected one of", str(cm.exception))

    def test_validation_type_errors(self) -> None:
        envx.set("BAD_BOOL", "maybe")
        with self.assertRaises(envx.EnvValidationError):
            envx.validate({"BAD_BOOL": {"type": "bool"}})

    def test_url_and_path_checks(self) -> None:
        envx.set("GOOD_URL", "https://example.com")
        envx.set("BAD_URL", "example.com")
        envx.set("GOOD_PATH", str(self.root))
        envx.set("BAD_PATH", str(self.root / "missing"))

        self.assertTrue(envx.is_valid_url("GOOD_URL"))
        self.assertFalse(envx.is_valid_url("BAD_URL"))
        self.assertTrue(envx.is_valid_path("GOOD_PATH"))
        self.assertFalse(envx.is_valid_path("BAD_PATH"))

    def test_save_env_writes_text(self) -> None:
        envx.set("SAVE_ME", "hello world")
        output = self.root / "saved.env"
        envx.save_env(str(output))
        content = output.read_text(encoding="utf-8")
        self.assertIn('SAVE_ME="hello world"', content)

