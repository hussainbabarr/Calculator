"""Safe scientific calculation engine used by the desktop UI."""

from __future__ import annotations

import ast
import math
import operator
import random
import statistics
from dataclasses import dataclass, field
from typing import Callable


class CalculatorError(Exception):
    """Raised for invalid expressions or mathematically undefined results."""


def _finite(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise CalculatorError("The result is outside the calculator's range.")
    return value


def _factorial(value: float) -> float:
    if value < 0 or value != int(value):
        raise CalculatorError("Factorial requires a non-negative integer.")
    return float(math.factorial(int(value)))


def _cbrt(value: float) -> float:
    return math.copysign(abs(value) ** (1 / 3), value)


def _round(value: float, digits: float = 0) -> float:
    return float(round(value, int(digits)))


def _build_functions(angle_mode: str) -> dict[str, Callable[..., float]]:
    mode = angle_mode.upper()
    if mode not in {"DEG", "RAD", "GRAD"}:
        raise CalculatorError("Unknown angle mode.")

    def to_radians(value: float) -> float:
        return math.radians(value) if mode == "DEG" else value * math.pi / 200 if mode == "GRAD" else value

    def from_radians(value: float) -> float:
        return math.degrees(value) if mode == "DEG" else value * 200 / math.pi if mode == "GRAD" else value

    return {
        "sin": lambda x: math.sin(to_radians(x)), "cos": lambda x: math.cos(to_radians(x)),
        "tan": lambda x: math.tan(to_radians(x)), "asin": lambda x: from_radians(math.asin(x)),
        "acos": lambda x: from_radians(math.acos(x)), "atan": lambda x: from_radians(math.atan(x)),
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh, "log": math.log10,
        "log10": math.log10, "ln": math.log, "exp": math.exp, "sqrt": math.sqrt,
        "cbrt": _cbrt, "factorial": _factorial, "abs": abs, "floor": math.floor,
        "ceil": math.ceil, "round": _round, "reciprocal": lambda x: 1 / x, "mod": operator.mod,
    }


def evaluate_expression(expression: str, *, angle_mode: str = "DEG", ans: float = 0.0) -> float:
    """Evaluate a calculator expression without invoking Python evaluation."""
    expression = expression.strip().replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**").replace("π", "pi").replace("φ", "phi")
    expression = expression.replace(" mod ", " % ")
    if not expression:
        raise CalculatorError("Enter an expression first.")
    functions = _build_functions(angle_mode)
    names: dict[str, float | Callable[..., float]] = {"pi": math.pi, "e": math.e, "phi": (1 + math.sqrt(5)) / 2, "ANS": ans, "ans": ans, **functions}
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("Check the expression and parentheses.") from exc

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in names and not callable(names[node.id]):
            return float(names[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow}
            operation = operations.get(type(node.op))
            if operation is None:
                raise CalculatorError("That operator is not supported.")
            if isinstance(node.op, (ast.Div, ast.Mod)) and right == 0:
                raise CalculatorError("Division by zero is not defined.")
            try:
                return _finite(operation(left, right))
            except (ValueError, OverflowError, ZeroDivisionError) as exc:
                raise CalculatorError("That operation is not defined for these values.") from exc
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in functions:
            if node.keywords:
                raise CalculatorError("Named arguments are not supported.")
            try:
                return _finite(functions[node.func.id](*(visit(arg) for arg in node.args)))
            except (ValueError, OverflowError, ZeroDivisionError, TypeError) as exc:
                raise CalculatorError("That function is not defined for these values.") from exc
        raise CalculatorError("Only calculator functions and numeric values are allowed.")

    return _finite(visit(tree))


safe_eval = evaluate_expression


def format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.12g}"


def statistics_summary(values: list[float]) -> dict[str, float | str]:
    if not values:
        raise CalculatorError("Enter at least one number.")
    counts = statistics.multimode(values)
    return {"Mean": statistics.fmean(values), "Median": statistics.median(values), "Mode": ", ".join(format_number(item) for item in counts), "Variance": statistics.pvariance(values), "Standard deviation": statistics.pstdev(values)}


@dataclass
class CalculatorState:
    display: str = "0"
    ans: float = 0.0
    angle_mode: str = "DEG"
    memory: float = 0.0
    history: list[tuple[str, str]] = field(default_factory=list)

    def calculate(self) -> str:
        result = evaluate_expression(self.display, angle_mode=self.angle_mode, ans=self.ans)
        self.ans = result
        rendered = format_number(result)
        self.history.insert(0, (self.display, rendered))
        self.display = rendered
        return rendered

    def random_number(self) -> None:
        self.display = format_number(random.random())

    def random_integer(self, low: int = 0, high: int = 100) -> None:
        self.display = str(random.randint(low, high))
