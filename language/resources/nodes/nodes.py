from ..tokens.token_types import Token


class NumberNode:
    def __init__(self, tok: Token):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'"{self.tok}"'


class BinOpNode:
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.op_tok = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, operator_token, node):
        self.op_tok = operator_token
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class Number:
    def __init__(self, value):
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
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return String(self.value + other.value)

    def __sub__(self, other):
        return String(self.value - other.value)

    def __repr__(self):
        return f'"{self.value}"'.replace('""', '"')


class VarAssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'{self.name} : ({self.value})'


class VarAccessNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'{self.name}'
#
# class ClassNode:
#     def __init__(self, name, methods, attributes):
#         self.name = name
#         self.methods = methods
#         self.attributes = attributes
#
#     def __repr__(self):
#         return f'({self.name}, {self.methods}, {self.params})'
