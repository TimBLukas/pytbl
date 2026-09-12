"""Tests for Markdown, HTML, and Mermaid reporting."""

import tempfile
import unittest
from pathlib import Path

import reporting


class TestReportComponents(unittest.TestCase):
    """Cover report construction and component validation."""

    def test_report_builders_and_metadata(self) -> None:
        report = reporting.Report(
            metadata={"title": "Metadata title", "author": "TBL"},
        )
        report.heading("Overview").paragraph("Details").bullet_list(["one", "two"])
        report.table(["Name", "Value"], [["answer", 42]])
        report.horizontal_rule()

        self.assertEqual(report.title, "Metadata title")
        self.assertEqual(report.author, "TBL")
        self.assertEqual(len(report.components), 5)
        self.assertIs(report.elements, report.components)

    def test_component_validation(self) -> None:
        with self.assertRaises(ValueError):
            reporting.Heading("bad", level=7)
        with self.assertRaises(ValueError):
            reporting.Table(["a"], [["a", "b"]])
        with self.assertRaises(ValueError):
            reporting.Table(["a"], [["a"]], alignments=["diagonal"])
        with self.assertRaises(ValueError):
            reporting.Link("site", "")
        with self.assertRaises(ValueError):
            reporting.Section("", [])


class TestRenderers(unittest.TestCase):
    """Cover Markdown and HTML output and file writing."""

    def _report(self) -> reporting.Report:
        return (
            reporting.Report(title="A <Report>", author="TBL")
            .heading("Details", level=2)
            .paragraph(
                [
                    "literal <text> ",
                    reporting.Bold("important"),
                    " ",
                    reporting.Link("docs", "https://example.com"),
                ]
            )
            .code("print('<value>')", language="python")
            .ordered_list(["first", reporting.ListItem("second", [reporting.ListItem("nested")])])
            .table(["Name", "Value"], [["x", "<y>"]], alignments=["left", "right"])
            .mermaid(reporting.Flowchart().node("start", "Start").edge("start", "end"))
        )

    def test_markdown_rendering(self) -> None:
        output = reporting.MarkdownRenderer().render(self._report())

        self.assertIn("# A \\<Report\\>", output)
        self.assertIn("**important**", output)
        self.assertIn("[docs](https://example.com)", output)
        self.assertIn("```python", output)
        self.assertIn("| Name | Value |", output)
        self.assertIn("```mermaid", output)
        self.assertIn("flowchart TD", output)

    def test_html_rendering_escapes_content(self) -> None:
        output = reporting.HTMLRenderer().render(self._report())

        self.assertIn("<!doctype html>", output)
        self.assertIn("&lt;Report&gt;", output)
        self.assertIn("&lt;value&gt;", output)
        self.assertIn("<ol>", output)
        self.assertIn('<table>', output)
        self.assertIn('<pre class="mermaid">', output)

    def test_render_and_write_helpers(self) -> None:
        report = reporting.Report("Report")

        self.assertIn("<!doctype html>", report.render(format="html"))
        self.assertTrue(report.render(format="markdown").startswith("# Report"))

        with tempfile.TemporaryDirectory() as directory:
            html_path = report.write(Path(directory) / "report.html")
            markdown_path = reporting.write_report(
                report, Path(directory) / "report.md"
            )
            self.assertTrue(html_path.read_text().startswith("<!doctype html>"))
            self.assertTrue(markdown_path.read_text().startswith("# Report"))

    def test_unsafe_urls_are_rejected(self) -> None:
        report = reporting.Report().paragraph(
            reporting.Link("bad", "javascript:alert(1)")
        )

        with self.assertRaises(ValueError):
            report.render()
        with self.assertRaises(ValueError):
            report.render(format="html")


class TestMermaidDiagrams(unittest.TestCase):
    """Cover the supported programmatic Mermaid representations."""

    def test_flowchart_and_subgraph(self) -> None:
        diagram = reporting.Flowchart(direction=reporting.Direction.LR)
        group = diagram.subgraph("Backend", id="backend")
        group.node("api", "API").edge("api", "db")
        output = diagram.node("db", "Database").to_mermaid()

        self.assertIn("flowchart LR", output)
        self.assertIn("subgraph backend", output)
        self.assertIn("api --> db", output)

    def test_other_diagram_types(self) -> None:
        sequence = reporting.SequenceDiagram().participant("Client").participant("Server")
        sequence.message("Client", "Server", "Request")
        self.assertIn("Client->>Server: Request", sequence.render())

        classes = reporting.ClassDiagram()
        classes.add_class("User", ["+name: str"])
        classes.add_class("Admin")
        classes.relationship("Admin", "User")
        self.assertIn("class User", classes.render())

        states = reporting.StateDiagram().state("Idle").transition("Idle", "Running", "start")
        self.assertIn("Idle --> Running : start", states.render())

        entities = reporting.ERDiagram().entity("User", [("int", "id")])
        entities.relationship("User", "||--o{", "Order", "places")
        self.assertIn("User ||--o{ Order", entities.render())

        pie = reporting.PieChart("Results").slice("Pass", 3).slice("Fail", 1)
        self.assertIn('"Pass" : 3', pie.render())


if __name__ == "__main__":
    unittest.main()
