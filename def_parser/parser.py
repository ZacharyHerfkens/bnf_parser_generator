"""
    Parser for bnf grammar files.
    The grammar is:
        - grammar: rule { rule } ;
        - rule: non-terminal ":" production { "|" production } ";" ;
        - production: term { term } | "!" ;
        - term: non-terminal | terminal ;
"""
from def_parser.lexer import Lexer, TokenType, Token
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class NonTerminal:
    name: Token

    @property
    def id(self) -> str:
        return self.name.value


@dataclass(frozen=True, eq=True)
class Terminal:
    name: Token

    @property
    def id(self) -> str:
        return self.name.value


@dataclass(frozen=True, eq=True)
class Rule:
    name: Token
    production: tuple[Terminal | NonTerminal, ...]

    @property
    def id(self) -> str:
        return self.name.value


def _parse_term(lex: Lexer) -> Terminal | NonTerminal:
    tok = lex.expect({TokenType.NON_TERMINAL, TokenType.TERMINAL})
    if tok.type == TokenType.NON_TERMINAL:
        return NonTerminal(tok)
    return Terminal(tok)


def _parse_production(lex: Lexer) -> list[Terminal | NonTerminal]:
    if lex.has({TokenType.EMPTY}):
        lex.expect({TokenType.EMPTY})
        return []
    terms: list[Terminal | NonTerminal] = [_parse_term(lex)]
    while lex.has({TokenType.NON_TERMINAL, TokenType.TERMINAL}):
        terms.append(_parse_term(lex))
    return terms


def _parse_rule(lex: Lexer) -> list[Rule]:
    name = lex.expect({TokenType.NON_TERMINAL})
    lex.expect({TokenType.COLON})
    productions: list[list[Terminal | NonTerminal]] = [_parse_production(lex)]
    while lex.has({TokenType.PIPE}):
        lex.expect({TokenType.PIPE})
        productions.append(_parse_production(lex))
    lex.expect({TokenType.SEMICOLON})
    return [Rule(name, tuple(prod)) for prod in productions]


def parse(string: str) -> list[Rule]:
    lex = Lexer(string)
    rules: list[Rule] = _parse_rule(lex)
    while lex.has({TokenType.NON_TERMINAL}):
        rules.extend(_parse_rule(lex))
    lex.expect({TokenType.EOF})
    return rules