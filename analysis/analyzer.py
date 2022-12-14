"""
    A grammar analyser for the bnf grammar.
"""
from def_parser.parser import Rule, Terminal, NonTerminal
from def_parser.lexer import Token


class UndefinedNonTerminal(Exception):
    def __init__(self, symbol: Token, rule: Rule) -> None:
        self._symbol = symbol
        self._rule = rule
        super().__init__(f"Undefined non-terminal '{symbol.value}' in rule '{rule.id}'")


class Analyzer:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules
        self._non_terminals: set[str] = set()
        self._terminals: set[str] = set()
        self._nullable: dict[str, bool] = {}
        self._first: dict[str, set[str]] = {}
        self._follow: dict[str, set[str]] = {}
        self._predict: dict[Rule, set[str]] = {}
        self._predict_non_term: dict[str, set[str]] = {}
        self._ambiguous: dict[str, set[Rule]] = {}

        self._init_sets()
        self._verify()
        self._init_dicts()

        self._compute_nullable()
        self._compute_first()
        self._compute_follow()
        self._compute_predict()

    def _init_sets(self) -> None:
        for rule in self._rules:
            self._non_terminals.add(rule.id)
            for symbol in rule.production:
                if isinstance(symbol, Terminal):
                    self._terminals.add(symbol.id)

    def _verify(self) -> None:
        for rule in self._rules:
            for symbol in rule.production:
                if isinstance(symbol, NonTerminal):
                    if symbol.id not in self._non_terminals:
                        raise UndefinedNonTerminal(symbol.name, rule)

    def _init_dicts(self) -> None:
        for non_terminal in self._non_terminals:
            self._nullable[non_terminal] = False
            self._first[non_terminal] = set()
            self._follow[non_terminal] = set()
            self._predict_non_term[non_terminal] = set()
            self._ambiguous[non_terminal] = set()

        self._follow[self._rules[0].id].add("EOF")

    def _compute_nullable(self) -> None:
        while True:
            changed = False
            for rule in self._rules:
                if self.nullable(rule.id):
                    continue
                for symbol in rule.production:
                    if isinstance(symbol, NonTerminal):
                        if not self.nullable(symbol.id):
                            break
                    else:
                        break
                else:  # no break
                    self._nullable[rule.id] = True
                    changed = True
            if not changed:
                break

    def _compute_first(self) -> None:
        while True:
            changed = False
            for rule in self._rules:
                rule_first = self.first_of(rule.production)
                if len(rule_first - self.first(rule.id)) > 0:
                    self._first[rule.id].update(rule_first)
                    changed = True
            if not changed:
                break

    def _compute_follow(self) -> None:
        while True:
            changed = False
            for rule in self._rules:
                if not rule.production:
                    continue
                for idx, symbol in enumerate(rule.production):
                    if isinstance(symbol, Terminal):
                        continue
                    follow = set()
                    if idx < len(rule.production) - 1:
                        follow.update(self.first_of(rule.production[idx + 1 :]))
                        if self.is_nullable(rule.production[idx + 1 :]):
                            follow.update(self.follow(rule.id))
                    else:
                        follow.update(self.follow(rule.id))

                    if len(follow - self.follow(symbol.id)) > 0:
                        self._follow[symbol.id].update(follow)
                        changed = True
            if not changed:
                break

    def _compute_predict(self) -> None:
        for rule in self._rules:
            self._predict[rule] = self.first_of(rule.production)
            if self.is_nullable(rule.production):
                self._predict[rule].update(self.follow(rule.id))

        for non_terminal in self.non_terminals:
            for rule in self.rules(non_terminal):
                predict = self.predict_rule(rule)
                if len(predict.intersection(self.predict_non_term(non_terminal))) > 0:
                    self._ambiguous[non_terminal].add(rule)
                self._predict_non_term[non_terminal].update(predict)

    def is_nullable(self, prod: tuple[Terminal | NonTerminal]) -> bool:
        for symbol in prod:
            if isinstance(symbol, NonTerminal):
                if not self.nullable(symbol.id):
                    return False
            else:
                return False
        return True

    def first_of(self, prod: tuple[Terminal | NonTerminal]) -> set[str]:
        first = set()
        for symbol in prod:
            if isinstance(symbol, Terminal):
                first.add(symbol.id)
                break
            else:
                first.update(self.first(symbol.id))
                if not self.nullable(symbol.id):
                    break
        return first

    def first(self, non_terminal: str) -> set[str]:
        return self._first[non_terminal]

    def follow(self, non_terminal: str) -> set[str]:
        return self._follow[non_terminal]

    def nullable(self, non_terminal: str) -> bool:
        return self._nullable[non_terminal]

    def predict_rule(self, rule: Rule) -> set[str]:
        return self._predict[rule]

    def predict_non_term(self, non_terminal: str) -> set[str]:
        return self._predict_non_term[non_terminal]

    def rules(self, non_terminal: str) -> list[Rule]:
        return [rule for rule in self._rules if rule.id == non_terminal]

    def is_ambiguous(self) -> bool:
        return any(self._ambiguous.values())
    
    def ambiguous(self) -> dict[str, set[Rule]]:
        return self._ambiguous

    @property
    def non_terminals(self) -> set[str]:
        return self._non_terminals

    @property
    def start(self) -> str:
        return self._rules[0].id
