"""NovaLang: a small, readable interpreted language.

The implementation is intentionally kept in one file for approachability:
source -> tokens -> AST -> evaluated values.
"""
from dataclasses import dataclass
import re
from typing import Any


class NovaError(Exception):
    """A user-facing language error."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: Any
    line: int
    column: int


KEYWORDS = {"let", "fn", "return", "if", "else", "while", "for", "break", "true", "false", "nil"}
TOKEN_RE = re.compile(
    r"(?P<space>[ \t\r]+)|(?P<comment>//[^\n]*)|(?P<newline>\n)|"
    r"(?P<number>\d+(?:\.\d+)?)|(?P<string>\"(?:\\.|[^\"\\])*\")|"
    r"(?P<identifier>[A-Za-z_][A-Za-z0-9_]*)|(?P<operator>==|!=|<=|>=|&&|\|\||[+\-*/%<>=!])|"
    r"(?P<punct>[(){},;:\[\]])"
)


def lex(source: str) -> list[Token]:
    tokens, position, line, column = [], 0, 1, 1
    while position < len(source):
        match = TOKEN_RE.match(source, position)
        if not match:
            raise NovaError(f"Unexpected character {source[position]!r} at {line}:{column}")
        kind, text = match.lastgroup, match.group()
        start_line, start_column = line, column
        position = match.end()
        if kind in {"space", "comment"}:
            column += len(text)
            continue
        if kind == "newline":
            line += 1
            column = 1
            continue
        column += len(text)
        if kind == "number":
            value = float(text) if "." in text else int(text)
            tokens.append(Token("number", value, start_line, start_column))
        elif kind == "string":
            try:
                value = bytes(text[1:-1], "utf-8").decode("unicode_escape")
            except UnicodeDecodeError as error:
                raise NovaError(f"Invalid string at {start_line}:{start_column}") from error
            tokens.append(Token("string", value, start_line, start_column))
        elif kind == "identifier":
            tokens.append(Token(text if text in KEYWORDS else "identifier", text, start_line, start_column))
        else:
            tokens.append(Token(text, text, start_line, start_column))
    tokens.append(Token("EOF", "", line, column))
    return tokens


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens, self.index = tokens, 0

    def current(self) -> Token:
        return self.tokens[self.index]

    def match(self, *kinds: str) -> Token | None:
        if self.current().kind in kinds:
            token = self.current()
            self.index += 1
            return token
        return None

    def expect(self, kind: str, message: str) -> Token:
        token = self.match(kind)
        if not token:
            current = self.current()
            raise NovaError(f"{message} at {current.line}:{current.column}")
        return token

    def parse(self) -> list[tuple]:
        statements = []
        while self.current().kind != "EOF":
            statements.append(self.statement())
        return statements

    def block(self) -> list[tuple]:
        self.expect("{", "Expected '{'")
        statements = []
        while self.current().kind not in {"}", "EOF"}:
            statements.append(self.statement())
        self.expect("}", "Expected '}'")
        return statements

    def statement(self) -> tuple:
        if self.match("let"):
            name = self.expect("identifier", "Expected a variable name").value
            self.expect("=", "Expected '=' after variable name")
            value = self.expression()
            self.expect(";", "Expected ';' after declaration")
            return ("let", name, value)
        if self.match("fn"):
            name = self.expect("identifier", "Expected a function name").value
            self.expect("(", "Expected '('")
            parameters = []
            if self.current().kind != ")":
                while True:
                    parameters.append(self.expect("identifier", "Expected parameter name").value)
                    if not self.match(","):
                        break
            self.expect(")", "Expected ')'")
            return ("fn", name, parameters, self.block())
        if self.match("return"):
            value = None if self.current().kind == ";" else self.expression()
            self.expect(";", "Expected ';' after return")
            return ("return", value)
        if self.match("if"):
            return self.if_statement()
        if self.match("while"):
            self.expect("(", "Expected '('")
            condition = self.expression()
            self.expect(")", "Expected ')'")
            return ("while", condition, self.block())
        if self.match("for"):
            return self.for_statement()
        if self.match("break"):
            self.expect(";", "Expected ';' after break")
            return ("break",)
        if self.match("{"):
            self.index -= 1
            return ("block", self.block())
        value = self.expression()
        self.expect(";", "Expected ';' after expression")
        return ("expr", value)

    def for_statement(self) -> tuple:
        self.expect("(", "Expected '('")
        if self.match("let"):
            name = self.expect("identifier", "Expected a variable name").value
            self.expect("=", "Expected '=' after variable name")
            initializer = ("let", name, self.expression())
        else:
            initializer = ("expr", self.expression())
        self.expect(";", "Expected ';' after for initializer")
        condition = self.expression()
        self.expect(";", "Expected ';' after for condition")
        increment = self.expression()
        self.expect(")", "Expected ')'")
        return ("for", initializer, condition, increment, self.block())

    def if_statement(self) -> tuple:
        self.expect("(", "Expected '('")
        condition = self.expression()
        self.expect(")", "Expected ')'")
        body = self.block()
        alternate = []
        if self.match("else"):
            alternate = [self.if_statement()] if self.match("if") else self.block()
        return ("if", condition, body, alternate)

    def expression(self, minimum_precedence: int = 0) -> tuple:
        left = self.unary()
        precedence = {"=": 0, "||": 1, "&&": 2, "==": 3, "!=": 3, "<": 4, "<=": 4, ">": 4, ">=": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6}
        while self.current().kind in precedence and precedence[self.current().kind] >= minimum_precedence:
            operator = self.current().kind
            level = precedence[operator]
            self.index += 1
            right = self.expression(level if operator == "=" else level + 1)
            if operator == "=" and left[0] not in {"variable", "index"}:
                raise NovaError("Assignment must target a variable or index")
            left = ("binary", operator, left, right)
        return left

    def unary(self) -> tuple:
        if self.current().kind in {"!", "-"}:
            operator = self.current().kind
            self.index += 1
            return ("unary", operator, self.unary())
        return self.postfix(self.primary())

    def postfix(self, expression: tuple) -> tuple:
        while True:
            if self.match("("):
                arguments = []
                if self.current().kind != ")":
                    while True:
                        arguments.append(self.expression())
                        if not self.match(","):
                            break
                self.expect(")", "Expected ')'")
                expression = ("call", expression, arguments)
            elif self.match("["):
                index = self.expression()
                self.expect("]", "Expected ']'")
                expression = ("index", expression, index)
            else:
                return expression

    def primary(self) -> tuple:
        token = self.current()
        if self.match("number", "string"):
            return ("literal", token.value)
        if self.match("true"):
            return ("literal", True)
        if self.match("false"):
            return ("literal", False)
        if self.match("nil"):
            return ("literal", None)
        if self.match("identifier"):
            return ("variable", token.value)
        if self.match("["):
            items = []
            if self.current().kind != "]":
                while True:
                    items.append(self.expression())
                    if not self.match(","):
                        break
            self.expect("]", "Expected ']'")
            return ("array", items)
        if self.match("{"):
            entries = []
            if self.current().kind != "}":
                while True:
                    key = self.match("string", "identifier")
                    if not key:
                        current = self.current()
                        raise NovaError(f"Expected a map key at {current.line}:{current.column}")
                    self.expect(":", "Expected ':' after map key")
                    entries.append((key.value, self.expression()))
                    if not self.match(","):
                        break
            self.expect("}", "Expected '}'")
            return ("map", entries)
        if self.match("("):
            value = self.expression()
            self.expect(")", "Expected ')'")
            return value
        raise NovaError(f"Expected an expression at {token.line}:{token.column}")


class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self.values: dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise NovaError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            self.values[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise NovaError(f"Undefined variable '{name}'")


@dataclass
class Function:
    parameters: list[str]
    body: list[tuple]
    closure: Environment


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class BreakSignal(Exception):
    """Internal signal used to leave the nearest while loop."""


class Interpreter:
    def __init__(self, output: list[str] | None = None):
        self.output = output if output is not None else []
        self.globals = Environment()
        self.globals.define("print", lambda *values: self.output.append(" ".join(format_value(v) for v in values)))
        self.globals.define("length", lambda value: len(value))
        self.globals.define("range", lambda end: list(range(int(end))))
        self.globals.define("keys", lambda value: list(value.keys()))
        self.globals.define("has", lambda value, key: key in value)

    def run(self, statements: list[tuple]) -> None:
        for statement in statements:
            self.execute(statement, self.globals)

    def execute(self, statement: tuple, environment: Environment) -> None:
        kind = statement[0]
        if kind == "let":
            environment.define(statement[1], self.evaluate(statement[2], environment))
        elif kind == "fn":
            environment.define(statement[1], Function(statement[2], statement[3], environment))
        elif kind == "return":
            raise ReturnSignal(None if statement[1] is None else self.evaluate(statement[1], environment))
        elif kind == "break":
            raise BreakSignal
        elif kind == "expr":
            self.evaluate(statement[1], environment)
        elif kind == "block":
            self.execute_block(statement[1], Environment(environment))
        elif kind == "if":
            branch = statement[2] if truthy(self.evaluate(statement[1], environment)) else statement[3]
            self.execute_block(branch, Environment(environment))
        elif kind == "while":
            guard = 0
            while truthy(self.evaluate(statement[1], environment)):
                guard += 1
                if guard > 100_000:
                    raise NovaError("Loop exceeded 100,000 iterations")
                try:
                    self.execute_block(statement[2], Environment(environment))
                except BreakSignal:
                    break
        elif kind == "for":
            loop_environment = Environment(environment)
            self.execute(statement[1], loop_environment)
            guard = 0
            while truthy(self.evaluate(statement[2], loop_environment)):
                guard += 1
                if guard > 100_000:
                    raise NovaError("Loop exceeded 100,000 iterations")
                try:
                    self.execute_block(statement[4], Environment(loop_environment))
                except BreakSignal:
                    break
                self.execute(statement[3], loop_environment)

    def execute_block(self, statements: list[tuple], environment: Environment) -> None:
        for statement in statements:
            self.execute(statement, environment)

    def evaluate(self, expression: tuple, environment: Environment) -> Any:
        kind = expression[0]
        if kind == "literal":
            return expression[1]
        if kind == "variable":
            return environment.get(expression[1])
        if kind == "array":
            return [self.evaluate(item, environment) for item in expression[1]]
        if kind == "map":
            return {key: self.evaluate(value, environment) for key, value in expression[1]}
        if kind == "index":
            value = self.evaluate(expression[1], environment)
            index = int(self.evaluate(expression[2], environment))
            try:
                return value[index]
            except (IndexError, KeyError, TypeError) as error:
                raise NovaError("Index is out of bounds or not indexable") from error
        if kind == "unary":
            value = self.evaluate(expression[2], environment)
            return not truthy(value) if expression[1] == "!" else -value
        if kind == "binary":
            operator = expression[1]
            if operator == "=":
                value = self.evaluate(expression[3], environment)
                target = expression[2]
                if target[0] == "variable":
                    environment.assign(target[1], value)
                else:
                    container = self.evaluate(target[1], environment)
                    index = self.evaluate(target[2], environment)
                    if not isinstance(container, (list, dict)):
                        raise NovaError("Only arrays and maps support indexed assignment")
                    container[index] = value
                return value
            left = self.evaluate(expression[2], environment)
            if operator == "&&" and not truthy(left):
                return False
            if operator == "||" and truthy(left):
                return True
            right = self.evaluate(expression[3], environment)
            return apply_operator(operator, left, right)
        if kind == "call":
            callee = self.evaluate(expression[1], environment)
            arguments = [self.evaluate(argument, environment) for argument in expression[2]]
            if isinstance(callee, Function):
                if len(arguments) != len(callee.parameters):
                    raise NovaError("Function received the wrong number of arguments")
                local = Environment(callee.closure)
                for name, value in zip(callee.parameters, arguments):
                    local.define(name, value)
                try:
                    self.execute_block(callee.body, local)
                except ReturnSignal as returned:
                    return returned.value
                return None
            if callable(callee):
                return callee(*arguments)
            raise NovaError("Only functions can be called")
        raise NovaError(f"Unknown expression {kind}")


def truthy(value: Any) -> bool:
    return bool(value)


def apply_operator(operator: str, left: Any, right: Any) -> Any:
    try:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            return left / right
        if operator == "%":
            return left % right
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
    except (TypeError, ZeroDivisionError) as error:
        raise NovaError(f"Cannot apply '{operator}' to those values") from error
    raise NovaError(f"Unknown operator '{operator}'")


def format_value(value: Any) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, list):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{key}: {format_value(item)}" for key, item in value.items()) + "}"
    return str(value)


def run(source: str) -> list[str]:
    output: list[str] = []
    interpreter = Interpreter(output)
    try:
        interpreter.run(Parser(lex(source)).parse())
    except ReturnSignal as error:
        raise NovaError("'return' can only be used inside a function") from error
    return output
