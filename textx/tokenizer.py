from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

import re


type TextInput = str | List[str]


class TokenType(Enum):
    pass


class TokenizerType(Enum):
    CHARACTER = "character"
    WORD = "word"
    WHITESPACE = "whitespace"
    SENTENCE = "sentence"
    PUNCTUATION = "punctuation"
    SUBWORD = "subword"
    NGRAM = "ngram"
    LINE = "line"
    SYMBOL = "symbol"


@dataclass
class Token:
    type: TokenType
    value: str
    start: Optional[int]
    end: Optional[int]


class Tokenizer:
    def tokenize(self, input: TextInput) -> List:
        """To be defined in child classes"""
        pass


class CharacterTokenizer(Tokenizer):
    def tokenize(self, input: TextInput) -> List[str]:
        """
        Splits provided TextInput into a List of chars

        Args:
            input (TextInput): text to be split by character

        Returns:
            List[str]: List of chars representing every char of the TextInput
        """
        tokens = []
        if isinstance(input, str):
            for c in input:
                tokens.append(c)

        else:
            for outer in input:
                for c in outer:
                    tokens.append(c)

        return tokens


class WordTokenizer(Tokenizer):
    def _split_by_words(self, text: str) -> List[str]:
        tokens = []
        words = text.split(" ")
        # remove punctuation
        for word in words:
            punctuation = [",", "!", ".", ";", "?", "'", '"']
            tokens.append("".join(c for c in word if c not in punctuation))

        return tokens

    def tokenize(self, input: TextInput) -> List[str]:
        """
        Splits provided TextInput into a List of strings, each representing a word

        Args:
            input (TextInput): text to be split by word

        Returns:
            List[str]: List of words representing every word of the TextInput
        """
        if isinstance(input, str):
            return self._split_by_words(input)

        else:
            tokens = []
            for subtext in input:
                tokens.append(self._split_by_words(subtext))

            return tokens


class WhitespaceTokenizer(Tokenizer):
    def _split_by_whitespace(self, text: str) -> List[str]:
        tokens = []
        words = text.split(" ")
        for word in words:
            if len(word.strip()) > 0:
                tokens.append(word.strip())

        return tokens

    def tokenize(self, input: TextInput) -> List[str]:
        """
        Splits provided TextInput into a List of strings, using whitespace to split

        Args:
            input (TextInput): text to be split by whitespace

        Returns:
            List[str]: List of strings representing the provided input being split by whitespace
        """
        if isinstance(input, str):
            return self._split_by_whitespace(input)

        else:
            tokens = []
            for subtext in input:
                tokens.append(self._split_by_whitespace(subtext))

            return tokens


class SentenceTokenizer(Tokenizer):
    def _split_by_punctuation_chars(self, text: str) -> List[str]:
        return [token for token in re.split(r"[.!?]", text) if token]

    def tokenize(self, input: TextInput) -> List[str]:
        """
        Splits provided TextInput into a List of strings, using whitespace to split

        Args:
            input (TextInput): text to be split by whitespace

        Returns:
            List[str]: List of strings representing the provided input being split by whitespace
        """
        if isinstance(input, str):
            return self._split_by_punctuation_chars(input)

        else:
            tokens = []
            for subtext in input:
                tokens.append(self._split_by_punctuation_chars(subtext))

            return tokens


def create_tokenizer(type: TokenizerType) -> Tokenizer:
    """
    Factory to generate a Tokenizer object of the provided tpye

    Args:
        type (TokenizerType): type of Tokenizer object to return

    Returns:
        Tokenizer: Matching Tokenizer based on provided type, defaults to CharacterTokenizer
    """
    match type:
        case TokenizerType.CHARACTER:
            return CharacterTokenizer()

        case TokenizerType.WORD:
            return WordTokenizer()

        case TokenizerType.WHITESPACE:
            return WhitespaceTokenizer()

        case TokenizerType.SENTENCE:
            return SentenceTokenizer()

    return CharacterTokenizer()


def _test():
    tokenizer = create_tokenizer(TokenizerType.SENTENCE)
    tokenized = tokenizer.tokenize(
        "This is a sentence. This is another sentence! this? is a interrupted sentence; ok?"
    )
    print(tokenized)


if __name__ == "__main__":
    _test()
