# `reporting`

Format-neutral report components and renderers for Markdown, HTML, and
Mermaid diagrams.

```python
from reporting import Heading, Paragraph, Report, render_to_string

report = Report(
    title="Release notes",
    components=[Heading("Summary", level=2), Paragraph("Ready to ship.")],
)
print(render_to_string(report, format="markdown"))
```

Compose `Table`, `ListBlock`, `CodeBlock`, links, and diagram classes from the
package exports, then use `write_report` for file output.
