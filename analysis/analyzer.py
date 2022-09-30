"""
    A grammar analyser for the bnf grammar.
"""
from def_parser.parser import Rule, Terminal, NonTerminal
from def_parser.lexer import Token


class UndefinedNonTerminal(Exception):
    def __init__(self, symbol: Token, rule: Rule) -> None:
        self._symbol = symbol
        self._rule = rule
        super().__init__(f"Undefined non-terminal '{symbol.value}' in rule '{rule.name.value}'")



class Analyzer:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules
        self._non_terminals: set[str] = set()
        self._terminals: set[str] = set()
        self._nullable: dict[str, bool] = {}
        self._first: dict[str, set[str]] = {}
        self._follow: dict[str, set[str]] = {}

        self._init_sets()
        self._verify()
        self._init_dicts()
    
    def _init_sets(self) -> None:
        for rule in self._rules:
            self._non_terminals.add(rule.name.value)
            for symbol in rule.production:
                if isinstance(symbol, Terminal):
                    self._terminals.add(symbol.name.value)
    
    def _verify(self) -> None:
        for rule in self._rules:
            for symbol in rule.production:
                if isinstance(symbol, NonTerminal):
                    if symbol.name.value not in self._non_terminals:
                        raise UndefinedNonTerminal(symbol.name, rule)
    
    def _init_dicts(self) -> None:
        for non_terminal in self._non_terminals:
            self._nullable[non_terminal] = False
            self._first[non_terminal] = set()
            self._follow[non_terminal] = set()