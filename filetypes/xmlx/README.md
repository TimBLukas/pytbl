# `filetypes.xmlx`

XML parsing and generation helpers with dictionary conversion, element
searching, XPath updates, merging, and optional XSD validation.

```python
from filetypes.xmlx import create_xml_file, read_xml_as_dict

create_xml_file("users", {"user": {"name": "Ada"}}, "users.xml")
print(read_xml_as_dict("users.xml"))
```

The standard library handles basic operations. Install `lxml` for full XPath
support and `validate_xml_schema`. To edit an existing tree, use
`read_xml`, then pass its returned `ElementTree` to `set_element_text`.
