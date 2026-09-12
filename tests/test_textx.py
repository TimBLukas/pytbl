"""Tests for the text processing helpers."""

import unittest

import textx


class TestCaseConversion(unittest.TestCase):
    """Cover the public case conversion helpers."""

    def test_common_case_conversions(self) -> None:
        value = "HTTP response-code"

        self.assertEqual(textx.words(value), ["http", "response", "code"])
        self.assertEqual(textx.to_snake_case(value), "http_response_code")
        self.assertEqual(textx.to_kebab_case(value), "http-response-code")
        self.assertEqual(textx.to_camel_case(value), "httpResponseCode")
        self.assertEqual(textx.to_pascal_case(value), "HttpResponseCode")
        self.assertEqual(textx.to_constant_case(value), "HTTP_RESPONSE_CODE")
        self.assertEqual(textx.to_title_case(value), "Http Response Code")
        self.assertEqual(textx.to_sentence_case(value), "Http response code")

    def test_case_aliases_and_empty_values(self) -> None:
        self.assertEqual(textx.snake_case("One Thing"), "one_thing")
        self.assertEqual(textx.camel_case("one thing"), "oneThing")
        self.assertEqual(textx.to_camel_case(""), "")
        self.assertEqual(textx.to_upper_case("MiXeD"), "MIXED")
        self.assertEqual(textx.to_lower_case("MiXeD"), "mixed")


class TestSluggingAndWrapping(unittest.TestCase):
    """Cover slug and text wrapping behavior."""

    def test_slugify_normalizes_text(self) -> None:
        self.assertEqual(textx.slugify("Café au lait!"), "cafe-au-lait")
        self.assertEqual(textx.slugify("A  B", separator="_"), "a_b")
        self.assertEqual(textx.slugify("A long title", max_length=6), "a-long")

        with self.assertRaises(ValueError):
            textx.slugify("value", separator=" ")
        with self.assertRaises(ValueError):
            textx.slugify("value", max_length=0)

    def test_wrapping_helpers(self) -> None:
        self.assertEqual(textx.wrap_text("one two three", 7), "one two\nthree")
        self.assertEqual(textx.wrap_words("one two three", 7), ["one two", "three"])
        self.assertEqual(textx.indent("a\nb", "> "), "> a\n> b")
        self.assertEqual(textx.dedent("  a\n  b"), "a\nb")

        with self.assertRaises(ValueError):
            textx.wrap_text("value", 0)


class TestTokenizers(unittest.TestCase):
    """Cover token values, spans, multiple sources, and factory behavior."""

    def test_tokenizer_types_and_spans(self) -> None:
        self.assertEqual(
            [token.value for token in textx.CharacterTokenizer().tokenize("a!")],
            ["a", "!"],
        )
        words = textx.WordTokenizer().tokenize("Hi, 42!")
        self.assertEqual([token.value for token in words], ["Hi", "42"])
        self.assertEqual((words[0].start, words[0].end), (0, 2))
        self.assertEqual(
            [token.value for token in textx.PunctuationTokenizer().tokenize("Hi,!")],
            [",", "!"],
        )
        self.assertEqual(
            [token.value for token in textx.LineTokenizer().tokenize("a\r\nb")],
            ["a", "b"],
        )
        self.assertEqual(
            [token.value for token in textx.SymbolTokenizer().tokenize("a€+")],
            ["€", "+"],
        )

    def test_tokenizer_options_and_multiple_sources(self) -> None:
        self.assertEqual(
            [token.value for token in textx.SubwordTokenizer(3).tokenize("token")],
            ["tok", "en"],
        )
        self.assertEqual(
            [token.value for token in textx.NgramTokenizer(2).tokenize("abc")],
            ["ab", "bc"],
        )
        tokens = textx.CharacterTokenizer().tokenize(["a", "bc"])
        self.assertEqual([token.source_index for token in tokens], [0, 1, 1])
        self.assertEqual(
            [token.value for token in textx.SentenceTokenizer().tokenize("One. Two!")],
            ["One.", "Two!"],
        )
        self.assertIsInstance(
            textx.create_tokenizer(textx.TokenizerType.WORD),
            textx.WordTokenizer,
        )

    def test_tokenizer_validation(self) -> None:
        with self.assertRaises(TypeError):
            textx.WordTokenizer().tokenize(42)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            textx.NgramTokenizer(0)
        with self.assertRaises(TypeError):
            textx.create_tokenizer("word")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
