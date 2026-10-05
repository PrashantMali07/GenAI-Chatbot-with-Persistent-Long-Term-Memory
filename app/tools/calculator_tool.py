import operator
from typing import Literal

from langchain_core.tools import tool


@tool
def calculator(num1: float, num2: float, operation: Literal['add', 'subtract', 'multiply', 'divide']) -> float:
    """Calculate different operations on two numbers."""
    if operation == 'add':
        return operator.add(num1, num2)
    elif operation == 'subtract':
        return operator.sub(num1, num2)
    elif operation == 'multiply':
        return operator.mul(num1, num2)
    elif operation == 'divide':
        if num2 == 0:
            raise ValueError("Cannot divide by zero")
        return operator.truediv(num1, num2)