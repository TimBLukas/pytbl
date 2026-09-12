from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import re
import unicodedata
from typing import Final, TypeAlias, List

TextInput: TypeAlias = str | List[str]


class TokenType(Enum):
    """Identifies the category of a token"""

    CHARACTER = "character"
    WORD = "word"
    WHITESPACE = "whitespace"
    SENTENCE = "sentence"
    PUNCTUATION = "punctuation"
    SUBWORD = "subword"
    NGRAM = "ngram"
    LINE = "line"
    SYMBOL = "symbol"


class TokenizerType(Enum):
    """Identifies the available tokenizer implementations"""

    CHARACTER = "character"
    WORD = "word"
    WHITESPACE = "whitespace"
    SENTENCE = "sentence"
    PUNCTUATION = "punctuation"
    SUBWORD = "subword"
    NGRAM = "ngram"
    LINE = "line"
    SYMBOL = "symbol"


@dataclass(frozen=True, slots=True)
class Token:
    """Represents a token and its location in the source text

    Attributes:
        type (TokenType): type of the token
        value (str): text or char represented by the token
        start (int): Inclusive character offset of the token
        end (int): Exclusive character offset of the token
        source_index: Index of the source string when tokenizing multiple strings. `None` when tokenizing a single string.

    `start` and `end` offsets follow Python's normal slice convention, meaning `source[start:end]` reconstructs  `value`
    """

    type: TokenType
    value: str
    start: int
    end: int
    source_index: int | None = None

    def __post_init__(self) -> None:
        """Validate the token's source span"""

        if self.start < 0:
            raise ValueError("Token start offset cannot be negative")

        if self.end < self.start:
            raise ValueError("Token and offset cannot be smaller than its start offset")

        if self.end - self.start != len(self.value):
            raise ValueError("Token span length must match the length of its value")

        if self.source_index is not None and self.source_index < 0:
            raise ValueError("Token span length must match the length of its value")


class Tokenizer(ABC):
    """Base class for tokenizers

    Subclass implement ``_tokenize_text`` for a single string.
    Base class handles both input forms:

    * ``str`` - one source string
    * ``List[str]`` - multiple independent source strings

    When multiple strings are supplied, each token receives a ``source_index``
    identifying the string it originated from
    """

    def tokenize(self, text: TextInput) -> List[Token]:
        """Tokenize the provided text

        Args:
            text (TextInput): A single string of list of independent strings

        Returns:
            A list of :class:`Token` objects. For a list of input strings,
            tokens are returned in order, and contain a ``source_index``

        Raises:
            TypeError: If the input is neither a string nor a list of strings
        """

        if isinstance(text, str):
            return self._tokenize_text(text, source_index=None)

        if isinstance(text, list):
            tokens: List[Token] = []

            for source_index, source_text in enumerate(text):
                if not isinstance(source_text, str):
                    raise TypeError("All items in the input need to be a string")

                tokens.extend(
                    self._tokenize_text(source_text, source_index=source_index)
                )

            return tokens

        raise TypeError(f"Expected str or List[str], got {type(text).__name__}")

    @abstractmethod
    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Tokenize a single source string

        Args:
            text (str): Source text to tokenize
            source_index: Index of the source string when the caller supplied multiple strings

        Returns:
            Tokens won from ``text``
        """
        raise NotImplementedError


class CharacterTokenizer(Tokenizer):
    """Tokenize text into individual Unicode characters

    Every Unicode code point in the source string becomes one token.
    This includes whitespace and punctuation
    """

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Tokenize a single string into character tokens"""
        return [
            Token(
                type=TokenType.CHARACTER,
                value=character,
                start=index,
                end=index + 1,
                source_index=source_index,
            )
            for index, character in enumerate(text)
        ]


class WordTokenizer(Tokenizer):
    """Tokenize text into words while preserving punctuation separately.

    Words consist of consecutive Unicode alphanumeric characters.
    Combining marks are included with the preceding word where applicable

    Punctuation is not included in the result. Use :class:`PunctuationTokenizer`
    or :class:`WhitespaceTokenizer` when punctuation should be retained
    """

    _WORD_PATTERN: Final[re.Pattern[str]] = re.compile(
        r"[^\W\d_]+(?:[\u0300-\u036f]+)?|\d+(?:[.,]\d+)*", re.UNICODE
    )

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Extract word tokens rom a single string"""
        tokens: List[Token] = []

        for match in self._WORD_PATTERN.finditer(text):
            tokens.append(
                Token(
                    type=TokenType.WORD,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    source_index=source_index,
                )
            )

        return tokens


class WhitespaceTokenizer(Tokenizer):
    """Split text into runs of non-whitespace characters

    Whitespace itself is treated as a delimiter and is not returned as token

    E.g. ``"hello  world\\nagain"`` produces ``["hello", "world", "again"]``
    """

    _NON_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\S+", re.UNICODE)

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Extract non-whitespace runs from a single string"""
        return [
            Token(
                type=TokenType.WHITESPACE,
                value=match.group(),
                start=match.start(),
                end=match.end(),
                source_index=source_index,
            )
            for match in self._NON_WHITESPACE_PATTERN.finditer(text)
        ]


class SentenceTokenizer(Tokenizer):
    """Tokenize text into sentences

    Sentences end with ``.``, ``!``, ``?``.
    Sentence-ending punctuation is retained as part of the sentence token

    This is intentionally a lightweight rule-based tokenizer rather than a complete sentence segmentation system.
    Abbreviations, decimal numbers, and other more complex cases may require a dedicated NLP sentence segmenter.
    """

    _SENTENCE_PATTERN: Final[re.Pattern[str]] = re.compile(
        r".+?(?:[.!?]+(?=\s|$)|$)",
        re.DOTALL,
    )

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Extract sentence tokens from a single string"""
        tokens: List[Token] = []

        for match in self._SENTENCE_PATTERN.finditer(text):
            value = match.group()

            # Avoid whitespace only sentences
            if not value.strip():
                continue

            start = match.start()
            end = match.end()

            # Remove trailing/leading whitespace
            leading_whitespace = len(value) - len(value.lstrip())
            trailing_whitespace = len(value) - len(value.rstrip())

            start += leading_whitespace
            end -= trailing_whitespace

            if start >= end:
                continue

            tokens.append(
                Token(
                    type=TokenType.SENTENCE,
                    value=text[start:end],
                    start=start,
                    end=end,
                    source_index=source_index,
                )
            )

        return tokens


class PunctuationTokenizer(Tokenizer):
    """Extract Unicode punctuation characters as individual tokens"""

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Extract punctuation tokens from a single string"""
        tokens: List[Token] = []

        for index, character in enumerate(text):
            if unicodedata.category(character).startswith(("P")):
                tokens.append(
                    Token(
                        type=TokenType.PUNCTUATION,
                        value=character,
                        start=index,
                        end=index + 1,
                        source_index=source_index,
                    )
                )

        return tokens


class SubwordTokenizer(Tokenizer):
    """Split words into fixed-length subword pieces

    This is a lightweight deterministic subword tokenizer. It is not a BPE,
    WordPiece or SentencePiece implementation.

    Args:
        subword_length (int): Maximum number of chars in each subword

    Example:
        A ``subword_length`` of ``3`` tokenizes ``"tokenizer"`` into ``["tok", "eni", "zer"]``
    """

    def __init__(self, subword_length: int = 3) -> None:
        """Initialize a subword tokenizer

        Args:
            subword_length: Maximum number of characters in each subword

        Raises:
            ValueError: If ``subword_length`` is less than one
        """
        if subword_length < 1:
            raise ValueError("subword length must be at least 1")

        self.subword_length = subword_length

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Split words into fixed-length subword tokens"""
        tokens: List[Token] = []

        for match in re.finditer(r"\S+", text, re.UNICODE):
            word = match.group()
            word_start = match.start()

            for offset in range(0, len(word), self.subword_length):
                value = word[offset : offset + self.subword_length]
                start = word_start + offset
                end = start + len(value)

                tokens.append(
                    Token(
                        type=TokenType.SUBWORD,
                        value=value,
                        start=start,
                        end=end,
                        source_index=source_index,
                    )
                )

        return tokens


class NgramTokenizer(Tokenizer):
    """Generate character n-grams from text

    Args:
        n (int): Number of characters in each n-gram
        include_whitespace (bool): Whether whitespace should participate in n-grams.

    Example:
        ``NgramTokenizer(3)`` applied to ``"hello"`` produces ``["hel", "ell", "llo"]
    """

    def __init__(self, n: int = 2, *, include_whitespace: bool = False) -> None:
        """Initialize an n-gram tokenizer.

        Args:
            n: Number of characters per n-gram.
            include_whitespace: Whether whitespace characters should be
                included when creating n-grams.

        Raises:
            ValueError: If ``n`` less than one.
        """
        if n < 1:
            raise ValueError("n must be at least 1")

        self.n = n
        self.include_whitespace = include_whitespace

    def _tokenize_text(self, text: str, source_index: int | None) -> List[Token]:
        """Generate character n-grams from a single string"""

        if not self.include_whitespace:
            positions = [
                index for index, character in enumerate(text) if not character.isspace()
            ]

            tokens: List[Token] = []

            for offset in range(len(positions) - self.n + 1):
                selected_positions = positions[offset : offset + self.n]
                start = selected_positions[0]
                end = selected_positions[-1] + 1

                tokens.append(
                    Token(
                        type=TokenType.NGRAM,
                        value=text[start:end],
                        start=start,
                        end=end,
                        source_index=source_index,
                    )
                )

            return tokens

        return [
            Token(
                type=TokenType.NGRAM,
                value=text[start : start + self.n],
                start=start,
                end=start + self.n,
                source_index=source_index,
            )
            for start in range(len(text) - self.n + 1)
        ]


class LineTokenizer(Tokenizer):
    """Tokenize text into lines.

    Line-ending characters such as ``\\n`` and ``\\r\\n`` are treated as
    delimiters and not included in the resulting tokens
    """

    def _tokenize_text(
        self,
        text: str,
        source_index: int | None,
    ) -> list[Token]:
        """Extract lines from a string"""
        tokens: list[Token] = []
        offset = 0

        for line in text.splitlines(keepends=True):
            value = line.rstrip("\r\n")
            end = offset + len(value)

            if value:
                tokens.append(
                    Token(
                        type=TokenType.LINE,
                        value=value,
                        start=offset,
                        end=end,
                        source_index=source_index,
                    )
                )

            offset += len(line)

        return tokens


class SymbolTokenizer(Tokenizer):
    """Extract Unicode symbols as individual tokens.

    Unicode categories beginning with ``S`` are considered symbols. This
    includes categories such as mathematical, currency, modifier, and other
    symbols.
    """

    def _tokenize_text(
        self,
        text: str,
        source_index: int | None,
    ) -> list[Token]:
        """Extract symbol tokens from a single string."""
        tokens: list[Token] = []

        for index, character in enumerate(text):
            if unicodedata.category(character).startswith("S"):
                tokens.append(
                    Token(
                        type=TokenType.SYMBOL,
                        value=character,
                        start=index,
                        end=index + 1,
                        source_index=source_index,
                    )
                )

        return tokens


_TOKENIZER_REGISTRY: Final[dict[TokenizerType, type[Tokenizer]]] = {
    TokenizerType.CHARACTER: CharacterTokenizer,
    TokenizerType.WORD: WordTokenizer,
    TokenizerType.WHITESPACE: WhitespaceTokenizer,
    TokenizerType.SENTENCE: SentenceTokenizer,
    TokenizerType.PUNCTUATION: PunctuationTokenizer,
    TokenizerType.SUBWORD: SubwordTokenizer,
    TokenizerType.NGRAM: NgramTokenizer,
    TokenizerType.LINE: LineTokenizer,
    TokenizerType.SYMBOL: SymbolTokenizer,
}


def create_tokenizer(tokenizer_type: TokenizerType) -> Tokenizer:
    """Create a tokenizer for the requested tokenizer type

    Args:
        tokenizer_type: Type of tokenizer to instantiate

    Returns:
        A new tokenizer isntance corresponding to ``tokenizer_type``

    Raises:
        ValueError: If the requested tokenizer type is not registered
        TypeError: if ``tokenizer_type`` is not a :class:`TokenizerType`
    """
    if not isinstance(tokenizer_type, TokenizerType):
        raise TypeError(
            f"```tokenizer_type``` must be of type :class:`TokenizerType`, was {type(tokenizer_type).__name__}"
        )

    if tokenizer_type not in _TOKENIZER_REGISTRY.keys():
        raise ValueError(
            "provided tokenizer type is not regiestered, check the provided type"
        )

    tokenizer_class = _TOKENIZER_REGISTRY[tokenizer_type]

    return tokenizer_class()


def _test() -> None:
    """Run a manual test of a tokenizer"""
    tokenizer = create_tokenizer(TokenizerType.WORD)

    text = (
        "This is a sentence. "
        "This is another sentence! "
        "This? Is a interrupted sentence; ok?"
    )

    for token in tokenizer.tokenize(text):
        print(token)


if __name__ == "__main__":
    _test()
