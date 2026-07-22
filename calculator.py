"""
Scientific calculator engine: safe expression evaluation, memory, bases, statistics.

Designed by Hussain Babar
"""

from __future__ import annotations

import ast
import math
import operator
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class CalculatorError(Exception):
    """User-facing calculation error."""


class AngleMode(str, Enum):
    DEG = "DEG"
    RAD = "RAD"
    GRAD = "GRAD"


class NumberBase(str, Enum):
    BIN = "Binary"
    OCT = "Octal"
    DEC = "Decimal"
    HEX = "Hexadecimal"


PHI = (1 + math.sqrt(5)) / 2


def finite(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise CalculatorError("Result is outside the calculator range.")
    return value


def format_number(value: float, max_decimals: int = 12) -> str:
    """Format for display; strip trailing noise from float math."""
    if abs(value) >= 1e15 or (abs(value) > 0 and abs(value) < 1e-9):
        return f"{value:.12g}"
    if float(value).is_integer() and abs(value) < 1e12:
        return str(int(value))
    text = f"{value:.{max_decimals}f}".rstrip("0").rstrip(".")
    return text if text else "0"


def factorial_value(value: float) -> float:
    if value < 0 or value != int(value):
        raise CalculatorError("Factorial requires a non-negative integer.")
    n = int(value)
    if n > 170:
        raise CalculatorError("Factorial is too large for this calculator.")
    return float(math.factorial(n))


def cbrt_value(value: float) -> float:
    return math.copysign(abs(value) ** (1 / 3), value)


def build_trig_functions(mode: AngleMode) -> dict[str, Callable[..., float]]:
    """Trigonometric helpers respecting angle mode."""

    def to_rad(x: float) -> float:
        if mode == AngleMode.DEG:
            return math.radians(x)
        if mode == AngleMode.GRAD:
            return x * math.pi / 200
        return x

    def from_rad(x: float) -> float:
        if mode == AngleMode.DEG:
            return math.degrees(x)
        if mode == AngleMode.GRAD:
            return x * 200 / math.pi
        return x

    return {
        "sin": lambda x: math.sin(to_rad(x)),
        "cos": lambda x: math.cos(to_rad(x)),
        "tan": lambda x: math.tan(to_rad(x)),
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
    }


def build_functions(mode: AngleMode) -> dict[str, Callable[..., float]]:
    """All callable names allowed in expressions."""
    trig = build_trig_functions(mode)
    return {
        **trig,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "log": math.log10,
        "log10": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "sqrt": math.sqrt,
        "cbrt": cbrt_value,
        "factorial": factorial_value,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "round": lambda x, n=0: float(round(x, int(n))),
        "reciprocal": lambda x: 1 / x,
        "mod": operator.mod,
        "pow10": lambda x: 10 ** x,
        "square": lambda x: x ** 2,
        "cube": lambda x: x ** 3,
    }


def normalize_expression(raw: str) -> str:
    """Map UI symbols to Python/math tokens."""
    text = raw.strip()
    replacements = (
        ("×", "*"),
        ("÷", "/"),
        ("−", "-"),
        ("^", "**"),
        ("π", "pi"),
        ("φ", "phi"),
        (" mod ", " % "),
        ("√", "sqrt"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def validate_brackets(expression: str) -> None:
    depth = 0
    for ch in expression:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            raise CalculatorError("Mismatched parentheses.")
    if depth != 0:
        raise CalculatorError("Mismatched parentheses.")


def auto_complete_brackets(expression: str) -> str:
    """Append missing closing parentheses."""
    open_count = expression.count("(")
    close_count = expression.count(")")
    if open_count > close_count:
        expression += ")" * (open_count - close_count)
    return expression


def evaluate_expression(
    expression: str,
    angle_mode: AngleMode = AngleMode.DEG,
    ans: float = 0.0,
) -> float:
    """
    Safely evaluate a numeric expression using AST (no arbitrary code execution).
    """
    expression = normalize_expression(expression)
    if not expression:
        raise CalculatorError("Enter an expression first.")
    validate_brackets(expression)
    expression = auto_complete_brackets(expression)

    functions = build_functions(angle_mode)
    constants: dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "phi": PHI,
        "ANS": ans,
        "ans": ans,
    }

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("Invalid expression syntax.") from exc

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in constants:
                return float(constants[node.id])
            raise CalculatorError(f"Unknown symbol: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
            }
            op = ops.get(type(node.op))
            if op is None:
                raise CalculatorError("Unsupported operator.")
            if isinstance(node.op, (ast.Div, ast.Mod)) and right == 0:
                raise CalculatorError("Division by zero is not defined.")
            try:
                return finite(op(left, right))
            except (ValueError, OverflowError, ZeroDivisionError) as exc:
                raise CalculatorError("Operation undefined for these values.") from exc
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in functions:
                raise CalculatorError(f"Unknown function: {name}")
            if node.keywords:
                raise CalculatorError("Named arguments are not supported.")
            try:
                args = [visit(arg) for arg in node.args]
                return finite(functions[name](*args))
            except CalculatorError:
                raise
            except (ValueError, OverflowError, ZeroDivisionError, TypeError) as exc:
                raise CalculatorError("Function undefined for these values.") from exc
        raise CalculatorError("Only numbers and calculator functions are allowed.")

    return finite(visit(tree))


def apply_percent(expression: str) -> str:
    """Append /100 for percentage key (applies to last numeric term)."""
    if not expression.strip():
        return "0/100"
    return f"({expression})/100"


def convert_base(value: float, target: NumberBase) -> str:
    """Convert integer decimal value to binary/octal/hex string."""
    n = int(value)
    if target == NumberBase.DEC:
        return str(n)
    if target == NumberBase.BIN:
        return bin(n)[2:]
    if target == NumberBase.OCT:
        return oct(n)[2:]
    if target == NumberBase.HEX:
        return hex(n)[2:].upper()
    return str(n)


def parse_base(text: str, source: NumberBase) -> float:
    text = text.strip()
    if not text:
        raise CalculatorError("Enter a number to convert.")
    try:
        if source == NumberBase.BIN:
            return float(int(text, 2))
        if source == NumberBase.OCT:
            return float(int(text, 8))
        if source == NumberBase.HEX:
            return float(int(text, 16))
        return float(text)
    except ValueError as exc:
        raise CalculatorError(f"Invalid {source.value} number.") from exc


def statistics_summary(values: list[float]) -> dict[str, str]:
    if not values:
        raise CalculatorError("Enter at least one number.")
    return {
        "Mean": format_number(statistics.fmean(values)),
        "Median": format_number(statistics.median(values)),
        "Mode": ", ".join(format_number(v) for v in statistics.multimode(values)),
        "Variance": format_number(statistics.pvariance(values)),
        "Standard Deviation": format_number(statistics.pstdev(values)),
    }


def random_float(low: float = 0.0, high: float = 1.0) -> float:
    import random

    return random.uniform(low, high)


def random_int(low: int, high: int) -> int:
    import random

    if low > high:
        low, high = high, low
    return random.randint(low, high)


def symbolic_simplify(expression: str) -> str:
    """
    Optional SymPy simplification for educational / exact forms.
    Falls back to normalized expression if SymPy is unavailable.
    """
    try:
        import sympy as sp

        x = sp.symbols("x")
        local = {
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "ln": sp.log,
            "log": sp.log,
            "sqrt": sp.sqrt,
            "pi": sp.pi,
            "e": sp.E,
            "phi": sp.GoldenRatio,
        }
        text = normalize_expression(expression)
        parsed = sp.sympify(text, locals=local)
        return str(sp.simplify(parsed))
    except Exception:
        return normalize_expression(expression)


@dataclass
class CalculatorMemory:
    """Memory register (MC, MR, M+, M-, MS)."""

    value: float = 0.0

    def clear(self) -> None:
        self.value = 0.0

    def recall(self) -> float:
        return self.value

    def add(self, amount: float) -> None:
        self.value += amount

    def subtract(self, amount: float) -> None:
        self.value -= amount

    def store(self, amount: float) -> None:
        self.value = amount


@dataclass
class UndoRedoStack:
    """Expression undo/redo for the display."""

    _undo: list[str] = field(default_factory=list)
    _redo: list[str] = field(default_factory=list)
    limit: int = 100

    def push(self, state: str) -> None:
        if self._undo and self._undo[-1] == state:
            return
        self._undo.append(state)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def undo(self, current: str) -> str | None:
        if len(self._undo) < 2:
            return None
        self._redo.append(current)
        self._undo.pop()
        return self._undo[-1]

    def redo(self, current: str) -> str | None:
        if not self._redo:
            return None
        state = self._redo.pop()
        self._undo.append(state)
        return state
