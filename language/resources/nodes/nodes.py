from ..tokens.token_types import Token, TokenType
from typing import Union


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
                                        "VarAssignNode", "VarAccessNode"], operator_token: TokenType, right_node: Union[NumberNode, StringNode, "BinOpNode",
                                          "UnaryOpNode", "VarAssignNode", "VarAccessNode"]):
        self.left_node = left_node
        self.op_tok = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


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

    def __repr__(self):
        return f'{self.value}'


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
