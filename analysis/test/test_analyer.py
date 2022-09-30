from def_parser.parser import parse
from analysis.analyzer import Analyzer, UndefinedNonTerminal
import pytest

def test_analyzer() -> None:
    analyzer = Analyzer(parse("S: 'a' | B ; B: 'b' ;"))
    assert analyzer._non_terminals == {"S", "B"}    
    assert analyzer._terminals == {"a", "b"}


def test_analyzer_bad() -> None:
    with pytest.raises(UndefinedNonTerminal):
        Analyzer(parse("S: 'a' | B ; A: 'a' ;"))
    