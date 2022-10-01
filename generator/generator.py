"""
    Generate a python file containing a recursive decent parser for the given
    ll(1) grammar.
"""
from analysis.analyzer import Analyzer
from def_parser.parser import Rule


class ParserGenerator:
    def __init__(self, rules: list[Rule]) -> None:
        self._analysis = Analyzer(rules)
        self._indent_count = 0
        self._indent_str = " " * 4
        self._output = ""

        self._generate()

    def _write(self, line: str) -> None:
        indent = self._indent_str * self._indent_count
        self._output += f"{indent}{line}\n"

    def _write_lines(self, lines: list[str]) -> None:
        for line in lines:
            self._write(line)

    def _method(
        self, name: str, args: list[tuple[str, str]], ret: str, body: list[str]
    ) -> None:
        arg_str = ", ".join([f"{arg}: {type}" for arg, type in args])
        self._write(f"def {name}(self, {arg_str}) -> {ret}:")
        self._indent()
        self._write_lines(body)
        self._dedent()
        self._write("")

    def _indent(self) -> None:
        self._indent_count += 1

    def _dedent(self) -> None:
        assert self._indent_count > 0
        self._indent_count -= 1

    def _generate(self) -> None:
        self._write_lines(["from dataclasses import dataclass", "", ""])

        self._token_def()
        self._cst_def()
        self._lexer_def()
        self._parser_def()

    def _token_def(self) -> None:
        self._write_lines(
            [
                "@dataclass(frozen=True, eq=True)",
                "class Token:",
            ]
        )
        self._indent()
        self._write_lines(
            [
                "type: str",
                "value: str",
                "pos: int",
            ]
        )
        self._dedent()
        self._write_lines(["", ""])
    
    def _cst_def(self) -> None:
        self._write_lines(["@dataclass(frozen=True, eq=True)", "class CST:"])
        self._indent()
        self._write_lines(
            [
                "non_term: str",
                "children: list[CST | Token]"
            ]
        )
        self._dedent()
        self._write_lines(["", ""])

    def _lexer_def(self) -> None:
        self._write("class Lexer:")
        self._indent()
        self._method("has", [("tokens", "set[str]")], "bool", ["pass"])
        self._method("expect", [("tokens", "set[str]")], "Token", ["pass"])
        self._write("")

    def _parser_def(self) -> None:
        self._write("class Parser[Lexer]:")
        self._indent()
        self._method(
            "__init__", 
            [("lexer", "Lexer")], 
            "None", 
            ["self._lexer = lexer"]
        )
        self._method("parse", [], "CST", [f"self._parse_{self._analysis.start}()"])
        
        for non_term in self._analysis.non_terminals:
            self._generate_non_term(non_term)
        
        self._dedent()
        self._write_lines(["", ""])
    
    def _generate_non_term(self, non_term: str) -> None:
        body = []
        for rule in self._analysis.productions(non_term):
            pass




def generate_parser(rules: list[Rule]) -> str:
    analsis = Analyzer(rules)
