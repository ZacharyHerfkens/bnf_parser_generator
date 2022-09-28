from def_parser.parser import parse
from def_parser.tokenizer import UnexpectedToken
from pytest import raises

def test_empty():
    rules = parse("A: ! ;")
    assert len(rules) == 1
    assert rules[0].nonterm == "A"
    assert [sym.name for sym in rules[0].productions[0]] == []


def test_single():
    rules = parse("A: B ;")
    assert [rule.nonterm for rule in rules] == ["A"]
    assert [sym.name for sym in rules[0].productions[0]] == ["B"]


def test_multi():
    rules = parse("A: B | C ;")
    assert [rule.nonterm for rule in rules] == ["A"]
    assert [sym.name for sym in rules[0].productions[0]] == ["B"]
    assert [sym.name for sym in rules[0].productions[1]] == ["C"]

def test_invalid():
    with raises(UnexpectedToken):
        parse("A: ;")
    
    with raises(UnexpectedToken):
        parse("A")
    
    with raises(UnexpectedToken):
        parse("")