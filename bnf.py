from parser.parser import Parser, Lexer, ParseTree
from def_parser.parser import parse, Rule


class Grammar:
    def __init__(self, string: str) -> None:
        self._rules = parse(string)
        self._parser = Parser(self._rules)
    
    def parse(self, lexer: Lexer) -> ParseTree:
        return self._parser.parse(lexer)