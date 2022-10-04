from parser.parser import Parser, Lexer, Token, ParseTree, UnexpectedToken
from def_parser.parser import parse

class TestLexer(Lexer):
    def __init__(self, string: str) -> None:
        self._string = string
        self._pos = 0
    
    def peek(self) -> Token:
        if self._pos >= len(self._string):
            return Token("EOF", "", self._pos)
        return Token(self._string[self._pos], self._string[self._pos], self._pos)
    
    def has(self, tokens: set[str]) -> bool:
        return self.peek().type in tokens
    
    def expect(self, tokens: set[str]) -> Token:
        token = self.peek()
        if token.type not in tokens:
            raise UnexpectedToken(token, tokens)
        self._pos += 1
        return token


def test_parser() -> None:
    rules = parse("s: 'a' s 'b' | ! ;")
    parser = Parser(rules)
    lexer = TestLexer("ab")
    tree = parser.parse(lexer)
    assert tree == ParseTree(
        "s", 
        [
            Token("a", "a", 0), 
            ParseTree("s", []),
            Token("b", "b", 1)
        ]
    )

def test_parser2() -> None:
    rules = parse("e: p et; et: '+' p et | !; p: '1';")
    parser = Parser(rules)
    lexer = TestLexer("1+1")
    tree = parser.parse(lexer)
    assert tree == ParseTree(
        "e",
        [
            ParseTree(
                "p",
                [ Token("1", "1", 0) ]
            ),
            ParseTree(
                "et",
                [
                    Token("+", "+", 1),
                    ParseTree(
                        "p",
                        [ Token("1", "1", 2) ]
                    ),
                    ParseTree("et", [])
                ]
            )
        ]
    )