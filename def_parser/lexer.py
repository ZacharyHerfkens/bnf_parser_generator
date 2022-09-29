"""
    Lexer for bnf grammars. 
    The tokens are:
        - NonTerminal   - a non-terminal symbol
        - Terminal      - a terminal symbol
        - Colon         - the colon symbol
        - Pipe          - the pipe symbol
        - Semicolon     - the semicolon symbol
        - Empty         - the empty symbol ('!')

    Comments and whitespaces are ignored.

    Terminal symbols are enclosed in single quotes and may contain any characters
    but single quotes and newlines. Non-Terminal symbols are any sequence of 
    alphanumeric characters and underscores.

    Single-line comments start with a '#' and end with a newline.
    Multi-line comments start with a ~# and end with a #~.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class TokenType(Enum):
    NON_TERMINAL = "non-terminal"
    TERMINAL = "terminal"
    COLON = ":"
    PIPE = "|"
    SEMICOLON = ";"
    EMPTY = "!"
    EOF = "eof"


@dataclass(frozen=True, eq=True)
class Token:
    type: TokenType
    value: str
    pos: int
    len: int


class Chars:
    def __init__(self, text: str) -> None:
        self._text = text
        self._pos = 0

    @property
    def done(self) -> bool:
        return self._pos >= len(self._text)

    @property
    def pos(self) -> int:
        return self._pos

    def peek(self) -> str:
        return self._text[self._pos]

    def next(self) -> str:
        char = self._text[self._pos]
        self._pos += 1
        return char

    def has(self, pred: Callable[[str], bool]) -> bool:
        return not self.done and pred(self.peek())

    def has_str(self, string: str) -> bool:
        return self._text.startswith(string, self._pos)

    def next_while(self, pred: Callable[[str], bool]) -> str:
        result = ""
        while self.has(pred):
            result += self.next()
        return result

    def next_str(self, string: str) -> bool:
        if self.has_str(string):
            self._pos += len(string)
            return True
        return False

    def next_until(self, string: str) -> str:
        start = self._pos
        while not self.done and not self.next_str(string):
            self.next()
        return self._text[start : self._pos]


class UnexpectedCharacter(Exception):
    def __init__(self, char: str, pos: int) -> None:
        self.char = char
        self.pos = pos
        super().__init__(f"Unexpected character '{char}' at position {pos}")


class UnexpectedToken(Exception):
    def __init__(self, expected: set[TokenType], actual: Token, pos: int) -> None:
        self.expected = expected
        self.actual = actual
        self.pos = pos
        super().__init__(f"Expected {expected} but got {actual} at <{pos}>")



class Lexer:
    def __init__(self, string: str) -> None:
        self._chars: Chars = Chars(string)
        self._peek: Token = self._next_token()

    def _skip(self) -> None:
        """Skip whitespace and comments."""
        while True:
            self._chars.next_while(str.isspace)
            if self._chars.next_str("#"):
                self._chars.next_while(lambda c: c != "\n")
            elif self._chars.next_str("~#"):
                self._chars.next_until("#~")
            else:
                break

    def _next_token(self) -> Token:
        self._skip()
        if self._chars.done:
            return Token(TokenType.EOF, "", self._chars.pos, 0)
        pos = self._chars.pos
        if self._chars.has(lambda c: c.isalnum() or c == "_"):
            value = self._chars.next_while(lambda c: c.isalnum() or c == "_")
            return Token(TokenType.NON_TERMINAL, value, pos, len(value))
        if self._chars.next_str("'"):
            value = self._chars.next_until("'")[:-1]  # remove trailing '
            return Token(TokenType.TERMINAL, value, pos, len(value) + 2)
        if self._chars.next_str(":"):
            return Token(TokenType.COLON, ":", pos, 1)
        if self._chars.next_str("|"):
            return Token(TokenType.PIPE, "|", pos, 1)
        if self._chars.next_str(";"):
            return Token(TokenType.SEMICOLON, ";", pos, 1)
        if self._chars.next_str("!"):
            return Token(TokenType.EMPTY, "!", pos, 1)

        raise UnexpectedCharacter(self._chars.peek(), self._chars.pos)

    @property
    def eof(self) -> bool:
        return self._peek is None

    def peek(self) -> Token:
        return self._peek

    def next(self) -> Token:
        token = self.peek()
        self._peek = self._next_token()
        return token

    def has(self, types: set[TokenType]) -> bool:
        return not self.eof and self.peek().type in types

    def expect(self, type: TokenType) -> Token:
        if self.has({type}):
            return self.next()
        raise UnexpectedToken({type}, self.peek(), self._chars.pos)
