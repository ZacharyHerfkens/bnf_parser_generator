from def_parser.parser import parse, Rule
from analysis.analyzer import Analyzer, UndefinedNonTerminal
import pytest

def test_analyzer() -> None:
    analyzer = Analyzer(parse("S: 'a' | B ; B: 'b' ;"))
    assert analyzer._non_terminals == {"S", "B"}    
    assert analyzer._terminals == {"a", "b"}


def test_analyzer_bad() -> None:
    with pytest.raises(UndefinedNonTerminal):
        Analyzer(parse("S: 'a' | B ; A: 'a' ;"))


def test_nullability() -> None:
    analyzer = Analyzer(parse("S: B C | D ; B: 'b' ; C: 'c' ; D: ! ;"))
    assert analyzer.nullable("S") == True
    assert analyzer.nullable("B") == False
    assert analyzer.nullable("C") == False
    assert analyzer.nullable("D") == True


def test_first_sets() -> None:
    rules = parse("S: A B C 'd'; A: 'a' | ! ; B: 'b' C | ! ; C: 'c' | ! ;")
    analyzer = Analyzer(rules)
    assert analyzer.first("S") == {"a", "b", "c", "d"}
    assert analyzer.first("A") == {"a"}
    assert analyzer.first("B") == {"b"}
    assert analyzer.first("C") == {"c"}

def test_follow_sets() -> None:
    rules = parse("S: A B C ; A: 'a' | ! ; B: C 'b' | ! ; C: 'c' ;")
    analyzer = Analyzer(rules)
    assert analyzer.follow("S") == {"EOF"}
    assert analyzer.follow("A") == {"c"}
    assert analyzer.follow("B") == {"c"}
    assert analyzer.follow("C") == {"b", "EOF"}

def test_predict_sets() -> None:
    rules = parse("S: A | B ; A: 'a' ; B: 'b' | 'c' | ! ;")
    analyzer = Analyzer(rules)
    assert analyzer.predict(rules[0]) == {"a"}
    assert analyzer.predict(rules[1]) == {"b", "c", "EOF"}
    assert analyzer.predict(rules[5]) == {"EOF"}

def test_predict_sets2() -> None:
    rules = parse("S: A B C ; A: 'a' A | 'a' ; B: 'b' B | ! ; C: 'c' C | ! ;")
    analyzer = Analyzer(rules)
    assert analyzer.predict(rules[0]) == {"a"}
    assert analyzer.predict(rules[1]) == {"a"}
    assert analyzer.predict(rules[2]) == {"a"}
    assert analyzer.predict(rules[3]) == {"b"}
    assert analyzer.predict(rules[4]) == {"c", "EOF"}
    assert analyzer.predict(rules[5]) == {"c"}
    assert analyzer.predict(rules[6]) == {"EOF"}