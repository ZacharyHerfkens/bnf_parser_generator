from def_parser.tokenizer import *
from pytest import raises


def test_simple() -> None:
    tokenizer = Tokenizer("ab: 'cd' ;")
    assert tokenizer.next() == Token(TokenType.NonTerm, "ab", Loc(0, 1, 1), 2)
    assert tokenizer.next() == Token(TokenType.Colon, ":", Loc(2, 1, 3), 1)
    assert tokenizer.next() == Token(TokenType.Term, "cd", Loc(4, 1, 5), 4)
    assert tokenizer.next() == Token(TokenType.Semicolon, ";", Loc(9, 1, 10), 1)
    assert tokenizer.next() == None


def test_comment() -> None:
    tok = Tokenizer("# comment \n ab")
    assert (t := tok.next()) is not None and t.type == TokenType.NonTerm


def test_invalid() -> None:
    with raises(InvalidCharacter):
        list(Tokenizer("ab: %"))

    with raises(UnclosedTerminal):
        list(Tokenizer("'ab"))


def test_toks() -> None:
    toks = [t.type for t in Tokenizer("ab: 'cd' | 'ef' ;")]
    expected = [
        TokenType.NonTerm,
        TokenType.Colon,
        TokenType.Term,
        TokenType.Pipe,
        TokenType.Term,
        TokenType.Semicolon,
    ]

    assert toks == expected
