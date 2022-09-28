"""
    Tokenize a bnf file. 
    The tokens are:
        - NonTerm   a non-terminal symbol
        - Term      a terminal symbol
        - Colon     a colon
        - SemiColon a semicolon
        - Pipe      a pipe
        - Empty     an empty string given by '!'
        - EOF       end of file
    
    Non-Terminals may contain letters, digits, and underscores. Terminals
    are enclosed in single quotes and may contain any characters except
    single quotes and newlines.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True, eq=True)
class Loc:
    pos: int
    line: int
    col: int

    def next(self, s: str) -> "Loc":
        new_pos = self.pos
        new_line = self.line
        new_col = self.col

        for c in s:
            if c == "\n":
                new_line += 1
                new_col = 1
            else:
                new_col += 1
            new_pos += 1

        return Loc(new_pos, new_line, new_col)
    
    def __sub__(self, other: "Loc") -> int:
        return self.pos - other.pos

    def __str__(self) -> str:
        return f"<ln {self.line}, col {self.col}>"


class TokenType(Enum):
    NonTerm = "nonterm"
    Term = "term"
    Colon = ":"
    Semicolon = ";"
    Pipe = "|"
    Empty = "!"
    EOF = "eof"


@dataclass(frozen=True, eq=True)
class Token:
    type: TokenType
    value: str
    loc: Loc
    len: int = 1


class InvalidCharacter(Exception):
    def __init__(self, char: str, pos: Loc) -> None:
        self._char = char
        self._loc = pos

    def __str__(self) -> str:
        return f"Invalid character '{self._char}' at {self._loc}"


class UnclosedTerminal(Exception):
    def __init__(self, pos: Loc) -> None:
        self._loc = pos
    
    def __str__(self) -> str:
        return f"Unclosed terminal starting at {self._loc}"
    

class UnexpectedToken(Exception):
    def __init__(self, expected: set[TokenType], actual: Token) -> None:
        self._expected = expected
        self._actual = actual
    
    def __str__(self) -> str:
        return f"Expected {self._expected}, got {self._actual.type} at {self._actual.loc}"


class Tokenizer(Iterator[Token]):
    def __init__(self, text: str) -> None:
        self._text: str = text
        self._loc: Loc = Loc(0, 1, 1)
        self._eof: bool = False
        self._peek: Token | None = self._next()

    def _cur_char(self) -> str | None:
        if self._loc.pos >= len(self._text):
            return None
        return self._text[self._loc.pos]

    def _next_char(self) -> str | None:
        chr = self._cur_char()
        if chr is None:
            return None
        self._loc = self._loc.next(chr)
        return chr
    
    def _nonterm(self) -> Token:
        start = self._loc
        value = ""
        while True:
            chr = self._cur_char()
            if chr is None:
                break
            if chr.isalnum() or chr == "_":
                value += chr
                self._next_char()
            else:
                break
        return Token(TokenType.NonTerm, value, start, len(value))
    
    def _term(self) -> Token:
        start = self._loc
        value = ""
        self._next_char() # skip the opening quote
        while True:
            chr = self._cur_char()
            if chr is None:
                raise UnclosedTerminal(start)
            if chr == "'":
                self._next_char()
                break
            elif chr == "\n":
                raise UnclosedTerminal(start)
            else:
                value += chr
                self._next_char()
        
        return Token(TokenType.Term, value, start, self._loc - start)
    
    def _skip_whitespace(self) -> None:
        while (chr := self._cur_char()) is not None and chr.isspace():
            self._next_char()
    
    def _skip_comment(self) -> None:
        while (chr := self._cur_char()) is not None and chr not in "\n":
            self._next_char()
    
    def _skip(self) -> None:
        while True:
            self._skip_whitespace()
            if self._cur_char() == "#":
                self._skip_comment()
            else:
                break

    def _next(self) -> Token | None:
        if self._eof:
            return None
        
        self._skip()
        cur = self._cur_char()
        if cur is None:
            self._eof = True
            return Token(TokenType.EOF, "", self._loc)
        
        start = self._loc

        if cur.isalnum() or cur == "_":
            return self._nonterm()
        elif cur == "'":
            return self._term()
        elif cur == ":":
            self._next_char()
            return Token(TokenType.Colon, ":", start)
        elif cur == ";":
            self._next_char()
            return Token(TokenType.Semicolon, ";", start)
        elif cur == "|":
            self._next_char()
            return Token(TokenType.Pipe, "|", start)
        elif cur == "!":
            self._next_char()
            return Token(TokenType.Empty, "!", start)
        else:
            raise InvalidCharacter(cur, start)
    
    def has(self, types: set[TokenType]) -> bool:
        return self._peek is not None and self._peek.type in types
    
    def expect(self, types: set[TokenType]) -> Token:
        token = self.next()
        assert token is not None
        if token.type not in types:
            raise UnexpectedToken(types, token)
        return token
    
    def peek(self) -> Token | None:
        return self._peek
    
    def next(self) -> Token | None:
        cur = self._peek
        self._peek = self._next()
        return cur
    
    def __iter__(self) -> Iterator[Token]:
        return self
    
    def __next__(self) -> Token:
        next = self.next()
        if next is None:
            raise StopIteration
        return next