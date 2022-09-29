from def_parser.parser import parse, Rule, Terminal, NonTerminal
from def_parser.lexer import Token, TokenType

def test_parse() -> None:
    rules = parse("S: 'a' | 'b' ;")
    assert rules == [
        Rule(
            Token(TokenType.NON_TERMINAL, "S", 0, 1),
            [Terminal(Token(TokenType.TERMINAL, "a", 3, 3))]
        ),
        Rule(
            Token(TokenType.NON_TERMINAL, "S", 0, 1),
            [Terminal(Token(TokenType.TERMINAL, "b", 9, 3))]
        )
    ]