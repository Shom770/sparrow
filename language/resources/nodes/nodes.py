from ..tokens.token_types import Token, TokenType
from typing import Union, List


class NumberNode:
    """Node for a number created by the parser for the abstract syntax tree"""

    def __init__(self, tok: Token) -> None:
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    """Node for a string created by the parser for the abstract syntax tree"""

    def __init__(self, tok: Token):
        self.tok = tok

    def __repr__(self):
        return f'"{self.tok}"'


class BinOpNode:
    """
    Node for usage of binary operators

    The following binary operators defined in the language right now are:
    +, -, /, *, ^
    """
    def __init__(self, left_node: Union[NumberNode, StringNode, "BinOpNode", "UnaryOpNode",
                                        "VarAssignNode", "VarAccessNode"], operator_token: TokenType,
                 right_node: Union[NumberNode, StringNode, "BinOpNode",
                                   "UnaryOpNode", "VarAssignNode", "VarAccessNode"]):
        self.left_node = left_node
        self.op_tok = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class ForNode:
    """
    Node of for loops
    for loops are syntactically defined as:
    for (identifier, start value (default 0), end value, step (default 1) {
    body
    }
    """
    def __init__(self, var_name: "VarAssignNode", start_value: int = 0, *, end_value: int, step_value: int = 1,  body: list):
        self.var_name = var_name
        self.start_value = start_value
        self.end_value = end_value
        self.step_value = step_value
        self.body = body

    def __repr__(self):
        return f'({self.var_name}, {self.start_value}, {self.end_value}, {self.step_value})'


class WhileNode:
    """
    Node for while loops
    while loops are syntactically defined as:
    while condition {
    body
    }
    """
    def __init__(self, cond: list, body: list):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return f'({self.cond}, {self.body})'


class UnaryOpNode:
    """
    Node for unary operators

    Unary operators are - and + before a number, like -1
    """
    def __init__(self, operator_token: TokenType,
                 node: Union[NumberNode, StringNode, BinOpNode,
                             "UnaryOpNode", "VarAssignNode", "VarAccessNode"]):
        self.op_tok = operator_token
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    """Node for an if statement"""
    def __init__(self, cases: List, else_case: Union[UnaryOpNode, BinOpNode]):
        self.cases = cases
        self.else_case = else_case

    def __repr__(self):
        text = '\n'
        for condition in self.cases:
            text += f"condition: {condition}\n"
        return text


class Number:
    """Class for the integer and float types in the language, under the Number class"""
    def __init__(self, value: Union["Number", int, float]):
        if isinstance(value, Number):
            self.value = value.value
        else:
            self.value = int(value) if '.' not in str(value) else float(value)

    def __add__(self, other):
        return Number(self.value + other.value)

    def __sub__(self, other):
        return Number(self.value - other.value)

    def __mul__(self, other):
        return Number(self.value * other.value)

    def __pow__(self, other):
        return Number(self.value ** other.value)

    def __truediv__(self, other):
        return Number(self.value / other.value)

    def __lt__(self, other):
        return Number(self.value < other.value)

    def __le__(self, other):
        return Number(self.value <= other.value)

    def __gt__(self, other):
        return Number(self.value > other.value)

    def __ge__(self, other):
        return Number(self.value >= other.value)

    def __ne__(self, other):
        return Number(self.value != other.value)

    def __eq__(self, other):
        return Number(self.value == other.value)

    def __repr__(self):
        return f'{self.value}'

    def anded_by(self, other):
        return Number(int(self.value and other.value))

    def ored_by(self, other):
        return Number(int(self.value or other.value))

    def notted_by(self):
        return Number(1 if self.value == 0 else 0)


class String:
    """Class for the string type in the language"""
    def __init__(self, value: str):
        self.value = value

    def __add__(self, other):
        return String(self.value + other.value)

    def __sub__(self, other):
        return String(self.value - other.value)

    def __repr__(self):
        return f'"{self.value}"'.replace('""', '"')

    def __lt__(self, other):
        return Number(self.value < other.value)

    def __le__(self, other):
        return Number(self.value <= other.value)

    def __gt__(self, other):
        return Number(self.value > other.value)

    def __ge__(self, other):
        return Number(self.value >= other.value)

    def __ne__(self, other):
        return Number(self.value != other.value)

    def __eq__(self, other):
        return Number(self.value == other.value)




class VarAssignNode:
    """
    Node for the assignment of a variable

    Assignment of a variable syntactically looks like:
    {name} = {value}
    """
    def __init__(self, name: str, value: Union[Number, String]) -> None:
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name} : ({self.value})'


class VarAccessNode:
    """
    Node for the accessing a variable

    Accessing of a variable syntactically looks like:
    {name}
    """
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self):
        return f'{self.name}'
