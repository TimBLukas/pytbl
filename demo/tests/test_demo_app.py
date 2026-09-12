"""Tests for the demo application in the demo/ package."""

import os
import tempfile
import unittest
from pathlib import Path

from demo.app import build_report, build_demo_data, ensure_demo_data, summarise_records


class TestDemoApp(unittest.TestCase):
    def test_demo_data_shape(self) -> None:
        data = build_demo_data()
        self.assertGreater(len(data), 0)
        self.assertIn("score", data[0])
        self.assertIn("title", data[0])

    def test_summary_metrics(self) -> None:
        summary = summarise_records(build_demo_data())
        self.assertEqual(summary["count"], len(build_demo_data()))
        self.assertIn("average_score", summary)
        self.assertIn("median_score", summary)
        self.assertIn("top_category", summary)

    def test_report_contains_metrics(self) -> None:
        report = build_report("Demo report", build_demo_data(), summarise_records(build_demo_data()))
        self.assertEqual(report.title, "Demo report")
        self.assertGreater(len(report.components), 0)

    def test_ensure_demo_data_creates_and_reads_json(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / "records.json"
            records = ensure_demo_data(target)
            self.assertTrue(target.exists())
            self.assertEqual(len(records), 6)
            self.assertEqual(records[0]["title"], "Data cleanup")


if __name__ == "__main__":
    unittest.main()
