"""
    A ll(1) parser for the language defined in the grammar file.
"""
from dataclasses import dataclass
from typing import Union
from def_parser.parser import Rule, Terminal, NonTerminal
from analysis.analyzer import Analyzer


@dataclass(frozen=True)
class Token:
    """A token in the input."""

    type: str
    value: str
    pos: int


@dataclass(frozen=True, eq=True)
class ParseTree:
    id: str
    children: list[Union[Token, "ParseTree"]]


class UnexpectedToken(Exception):
    """Exception raised when the parser encounters an unexpected token."""

    def __init__(self, token: Token, expected: set[str]) -> None:
        self.token = token
        self.expected = expected

    def __str__(self) -> str:
        return f"Unexpected token {self.token} at position {self.token.pos}, expected {self.expected}"


class Lexer:
    """Abstract lexer class."""

    def peek(self) -> Token:
        """Return the next token without consuming it."""
        raise NotImplementedError

    def has(self, tokens: set[str]) -> bool:
        """Return True if the next token is in tokens."""
        raise NotImplementedError
    
    def expect(self, tokens: set[str]) -> Token:
        """Return the next token if it is in tokens. Raise UnexpectedToken otherwise."""
        raise NotImplementedError


class Parser:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules
        self._analysis = Analyzer(rules)
        if self._analysis.is_ambiguous():
            raise
    
    def parse(self, lexer: Lexer) -> ParseTree:
        return self._parse(lexer, self._analysis.start)
    
    def _parse(self, lexer: Lexer, nonterm: str) -> ParseTree:
        """Parse the input using the given nonterminal."""
        if not lexer.has(self._analysis.predict_non_term(nonterm)):
            raise UnexpectedToken(lexer.peek(), self._analysis.predict_non_term(nonterm))
        
        for rule in self._analysis.rules(nonterm):
            if lexer.has(self._analysis.predict_rule(rule)):
                return self._parse_rule(lexer, rule)
        
        assert False, "Unreachable"
    
    def _parse_rule(self, lexer: Lexer, rule: Rule) -> ParseTree:
        children = []
        for symbol in rule.production:
            if isinstance(symbol, Terminal):
                children.append(lexer.expect({symbol.id}))
            else:
                children.append(self._parse(lexer, symbol.id))
        
        return ParseTree(rule.id, children)
