from __future__ import annotations

from typing import Optional

try:
    from pyBCV import Currency
except ImportError:
    Currency = None


def parse_amount(value: str) -> float:
    if value is None or not value.strip():
        raise ValueError("El monto no puede estar vacío.")

    normalized = value.strip().replace(",", ".")
    try:
        return float(normalized)
    except ValueError as error:
        raise ValueError("Ingresa un número válido.") from error


def convert_amount(cantidad: float, tasa: float, modo: str) -> float:
    if tasa <= 0:
        raise ValueError("La tasa debe ser mayor que cero.")
    if cantidad < 0:
        raise ValueError("El monto no puede ser negativo.")

    if modo == "USD a Bs":
        return cantidad * tasa
    if modo == "Bs a USD":
        return cantidad / tasa

    raise ValueError("Modo de conversión no válido.")


def format_result(value: float, modo: str) -> str:
    if modo == "USD a Bs":
        return f"{value:,.2f} Bs"
    return f"{value:,.2f} USD"


def clean_rate(raw_rate) -> float:
    value = str(raw_rate).replace("Bs.", "").replace("Bs", "").strip().replace(" ", "")
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    else:
        value = value.replace(",", ".")
    return float(value)


def get_rate_from_pybcv() -> Optional[float]:
    if Currency is None:
        return None

    rate = Currency().get_rate("USD")
    return clean_rate(rate)


def evaluate_expression(expression: str) -> float:
    """Evalúa una expresión aritmética simple de forma segura.

    Soporta +, -, *, /, **, paréntesis y números (coma o punto como decimal).
    Lanza ValueError si la expresión contiene elementos no permitidos.
    """
    import ast
    import operator as _op

    if expression is None or not str(expression).strip():
        raise ValueError("Expresión vacía.")

    expr = str(expression).strip().replace(",", ".")

    # Operadores permitidos
    operators = {
        ast.Add: _op.add,
        ast.Sub: _op.sub,
        ast.Mult: _op.mul,
        ast.Div: _op.truediv,
        ast.Pow: _op.pow,
        ast.USub: _op.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            if type(node.op) not in operators:
                raise ValueError("Operador no permitido.")
            left = _eval(node.left)
            right = _eval(node.right)
            return operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in operators:
                raise ValueError("Operador unario no permitido.")
            return operators[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Num):
            return node.n
        if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
        raise ValueError("Expresión no válida.")

    try:
        node = ast.parse(expr, mode="eval")
        return float(_eval(node))
    except Exception as e:
        raise ValueError(f"Error evaluando la expresión: {e}") from e
