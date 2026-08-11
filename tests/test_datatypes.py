"""Tests for the datatypes package."""

import unittest

import datatypes


class TestDatatypesPackage(unittest.TestCase):
    """Cover the package facade and public names."""

    def test_exports(self) -> None:
        self.assertIn("PathLike", datatypes.__all__)
        self.assertIn("JsonValue", datatypes.__all__)
        self.assertEqual(datatypes.__version__, "0.0.1")
        self.assertEqual(datatypes.__author__, "TBL")

    def test_aliases_exist(self) -> None:
        self.assertTrue(hasattr(datatypes, "PathLike"))
        self.assertTrue(hasattr(datatypes, "JsonObject"))
        self.assertTrue(hasattr(datatypes, "Predicate"))

