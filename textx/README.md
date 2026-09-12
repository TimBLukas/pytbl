# `textx`

Text-processing helpers for case conversion, URL-friendly slugs, wrapping,
indentation, and simple tokenization.

```python
from textx import WordTokenizer, slugify, snake_case, wrap_text

print(snake_case("Release Candidate"))
print(slugify("Café menu"))
print(wrap_text("A paragraph that needs wrapping.", width=12))
print(WordTokenizer().tokenize("Hello, world!"))
```

Tokenizer classes and `create_tokenizer` are useful for lightweight parsing;
they are not intended to replace a full NLP tokenizer.
