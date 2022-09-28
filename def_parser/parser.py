"""
    Parser for bnf grammar files.
    The grammar is:
        - grammar: rule { rule } ;
        - rule: nonterm ":" productions ";" ;
        - productions: production { "|" production } ;
        - production: empty | symbol { symbol } ;
        - symbol: nonterm | term ;
"""

from def_parser.tokenizer import Tokenizer, TokenType, UnexpectedToken
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Symbol:
    name: str
    is_nonterm: bool


@dataclass(frozen=True, eq=True)
class Rule:
    nonterm: str
    productions: list[list[Symbol]]

    def __str__(self) -> str:
        prods = " | ".join(" ".join(s.name for s in prod) for prod in self.productions)
        return f"{self.nonterm}: {prods} ;"

def _parse_production(tok: Tokenizer) -> list[Symbol]:
    if tok.has({TokenType.Empty}):
        tok.expect({TokenType.Empty})
        return []
    
    symbols: list[Symbol] = []
    while tok.has({TokenType.NonTerm, TokenType.Term}):
        sym = tok.expect({TokenType.NonTerm, TokenType.Term})
        symbols.append(Symbol(sym.value, sym.type == TokenType.NonTerm))
    
    if len(symbols) == 0:
        peek = tok.peek()
        assert peek is not None
        raise UnexpectedToken({TokenType.Empty, TokenType.NonTerm, TokenType.Term}, peek)
    
    return symbols

    
def _parse_productions(tok: Tokenizer) -> list[list[Symbol]]:
    prods = [_parse_production(tok)]
    while tok.has({TokenType.Pipe}):
        tok.expect({TokenType.Pipe})
        prods.append(_parse_production(tok))
    
    return prods


def _parse_rule(tok: Tokenizer) -> Rule:
    nonterm = tok.expect({TokenType.NonTerm}).value
    tok.expect({TokenType.Colon})
    productions = _parse_productions(tok)
    tok.expect({TokenType.Semicolon})
    return Rule(nonterm, productions)


def parse(text: str) -> list[Rule]:
    tok = Tokenizer(text)
    rules: list[Rule] = [_parse_rule(tok)]
    while tok.has({TokenType.NonTerm}):
        rules.append(_parse_rule(tok))
    tok.expect({TokenType.EOF})
    return rules