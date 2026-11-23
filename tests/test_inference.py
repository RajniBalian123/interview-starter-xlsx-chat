"""Checks for type inference, coercion, and the chat tools."""

import unittest
from pathlib import Path

from src.chat import answer
from src.parse_spreadsheet import (coerce_value, coerced_rows,
                                   discover_column_schema, infer_type,
                                   parse_spreadsheet)
from src.store import Store

ROOT = Path(__file__).resolve().parents[1]


class TestInference(unittest.TestCase):
    def test_each_type(self):
        self.assertEqual(infer_type(["1", "2", "30"]), "integer")
        self.assertEqual(infer_type(["4.5", "3.0"]), "float")
        self.assertEqual(infer_type(["true", "false", "yes"]), "boolean")
        self.assertEqual(infer_type(["2022-03-14", "2021-11-02"]), "date")
        self.assertEqual(infer_type(["2022-03-14 10:00:00"]), "datetime")
        self.assertEqual(infer_type(["$125,000.00", "$98,500.00"]), "currency")

    def test_empty_cells_are_skipped(self):
        self.assertEqual(infer_type(["", "5", ""]), "integer")
        self.assertEqual(infer_type(["", ""]), "string")

    def test_mixed_types_fall_back_to_string(self):
        self.assertEqual(infer_type(["12", "hello"]), "string")
        self.assertEqual(infer_type(["$100.00", "200"]), "string")

    def test_locale_numbers(self):
        self.assertEqual(infer_type(["1,250.00", "98,500.00"]), "float")

    def test_one_and_zero_are_integers_not_booleans(self):
        self.assertEqual(infer_type(["1", "0", "1"]), "integer")

    def test_sample_spreadsheet_schema(self):
        headers, rows = parse_spreadsheet(ROOT / "data" / "sample_employees.csv")
        schema = discover_column_schema(headers, rows)
        self.assertEqual(schema["salary"]["type"], "currency")
        self.assertEqual(schema["hire_date"]["type"], "date")
        self.assertEqual(schema["active"]["type"], "boolean")
        self.assertEqual(schema["rating"]["type"], "float")
        self.assertEqual(schema["notes"]["type"], "string")  # mixed text + "12"

    def test_coercion(self):
        self.assertEqual(coerce_value("$125,000.00", "currency"), 125000.0)
        self.assertEqual(coerce_value("4.5", "float"), 4.5)
        self.assertEqual(coerce_value("yes", "boolean"), True)
        self.assertIsNone(coerce_value("", "integer"))


class TestChat(unittest.TestCase):
    def _store(self):
        headers, rows = parse_spreadsheet(ROOT / "data" / "sample_employees.csv")
        schema = discover_column_schema(headers, rows)
        store = Store()
        store.add_source("sample_employees.csv", headers,
                         coerced_rows(headers, rows, schema))
        return store

    def test_list_files(self):
        self.assertIn("sample_employees.csv", answer(self._store(), "what files do I have?"))

    def test_show_rows(self):
        out = answer(self._store(), "show me 2 rows from sample_employees.csv")
        self.assertIn("2 row(s)", out)

    def test_average_salary(self):
        out = answer(self._store(), "average of salary in sample_employees.csv")
        self.assertIn("104,775.00", out)

    def test_how_many_rows(self):
        out = answer(self._store(), "how many rows in sample_employees.csv")
        self.assertIn("8 row(s)", out)


if __name__ == "__main__":
    unittest.main()
