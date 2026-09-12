# `filetypes.htmlx`

HTML parsing, text/link extraction, safe element generation, table/list
helpers, and CSS-selector updates.

```python
from filetypes.htmlx import extract_links, generate_html, write_html

page = generate_html(
    title="Links",
    body="<p>Read the <a href='https://example.com'>documentation</a>.</p>",
)
write_html("links.html", page)
print(extract_links("links.html"))
```

Generation works without optional packages; parsing and updates require
`beautifulsoup4`.
