from ..tokens.token_types import Token, TokenType
from typing import Union, List
from ..symbol_table.symbol_table import SymbolTable


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
        return f'{self.tok}'


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


class ReturnNode:
    """
    Node when the return keyword is used.

    Returning is syntactically defined as:
    return {expr}
    """

    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f'return {self.expression}'


class FunctionNode:
    """
    Node for the definition of a function.
    Defining a function is syntactically defined as:
    define {function_name}(param, param2) {
        # code goes here
    }
    """
    def __init__(self, func_name: str, params: list, symbol_table: SymbolTable, body: list):
        self.func_name = func_name
        self.params = params
        self.body = body
        self.local_symbol_table = symbol_table

    def __repr__(self):
        return f'(name: {self.func_name}, params: {self.params}, body: {self.body})'


class FunctionCallNode:
    """
    Node for calling a function.
    Calling a function is syntactically defined as:
    {function_name}({params})
    """
    def __init__(self, func_name: str, params: list):
        self.func_name = func_name
        self.params = params

    def __repr__(self):
        return f'{self.func_name}({self.params})'


class ForNode:
    """
    Node of for loops
    for loops are syntactically defined as:
    for (identifier, start value (default 0), end value, step (default 1) {
    body
    }
    """
    def __init__(self, var_name: "VarAssignNode", start_value: Union[NumberNode, "VarAccessNode"],
                 end_value: Union[NumberNode, "VarAccessNode"], step_value: Union[NumberNode, "VarAccessNode"],
                 body: list):
        self.var_name = var_name
        self.start_value = start_value
        self.end_value = end_value
        self.step_value = step_value
        self.body = body

    def __repr__(self):
        return f'({self.var_name}, {self.start_value}, {self.end_value}, {self.step_value})\nbody: {self.body}'


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
        text += f"else case: {self.else_case}\n"
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
        self.vals = {idx: val for idx, val in enumerate(self.value)}

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


class List:
    """Class for the list type in the language"""
    def __init__(self, value: dict):
        self.vals = value
        self.value = [item.value for item in self.vals.values()]

    def __repr__(self):
        return f'{self.value}'

    def __ne__(self, other):
        return Number(self.vals != other.vals)

    def __eq__(self, other):
        return Number(self.vals == other.vals)


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


class AccessNode:
    """
    Node for accessing symbol tables, specifically for class instances.

    Accessing a symbol table is syntactically defined as:
    {variable with symbol table}.{item to access}
    """
    def __init__(self, accessor: VarAccessNode, item_to_access: Union[VarAccessNode, FunctionNode]):
        self.accessor = accessor
        self.item_to_access = item_to_access

    def __repr__(self):
        return f'(from {self.accessor}, get {self.item_to_access})'


class ObjectNode:
    """
    Node for user-defined objects.

    Creating an object syntactically looks like:
    object {name} {
        # constructors
    }
    """
    def __init__(self, name: str, methods: dict, special_methods: dict, attributes: dict, symbol_table: SymbolTable,
                 global_attrs: list, inherit: str = None):
        self.name = name
        self.methods = methods
        self.special_methods = special_methods
        self.attributes = attributes
        self.class_attrs = global_attrs
        self.local_symbol_table = symbol_table
        self.inherit = inherit

    def __repr__(self):
        return f'(name: {self.name}, methods: {self.methods}, special methods: {self.special_methods}, attributes: {self.local_symbol_table.symbols})'


class ListNode:
    """
    Node for lists.
    A list is syntactically defined as:
    [*item, *more items]
    """
    def __init__(self, mapping: dict):
        self.list = mapping

    def __repr__(self):
        return f"({self.list})"

class ExecuteBuiltInsNode:
    """
    Node for executing built in functions

    The following are currently built-in functions:
        print
        input
        input_int
        is_number
        is_string
        is_list
        append
        pop
        extend
    """
    def __init__(self, name: str, params: list):
        self.name = name
        self.method = getattr(self, f"execute_{name}")
        self.params = params

    def fetch_func(self):
        """Used when in interpreter to fetch the built-in function."""
        return self.method(self.params)

    def execute_print(self, params: list) -> list:
        """Helper function to execute a print statement"""
        return params

    def execute_input(self, params: list) -> String:
        """Helper function to fetch input"""
        if params:
            to_display = params[0]
        else:
            to_display = ''
        text = input(to_display.value)
        return String(text)

    def execute_input_int(self, params: list) -> String:
        """Helper function to fetch input in the form of a number"""
        if params:
            to_display = params[0]
        else:
            to_display = ''
        text = input(to_display.value)
        try:
            text = int(text)
        except ValueError:
            return f"{text} is not a number!"

        return Number(str(text))

    def execute_is_number(self, params: list) -> Number:
        """Helper function to see if the argument is a number"""
        if isinstance(params[0], NumberNode) or isinstance(params[0], Number):
            return Number(1)
        else:
            return Number(0)

    def execute_is_string(self, params: list) -> Number:
        """Helper function to see if the argument is a string"""
        if isinstance(params[0], StringNode) or isinstance(params[0], String):
            return Number(1)
        else:
            return Number(0)

    def execute_is_list(self, params: list) -> Number:
        """Helper function to see if the argument is a list"""
        if isinstance(params[0], ListNode) or isinstance(params[0], List):
            return Number(1)
        else:
            return Number(0)

    def execute_append(self, params: list) -> list:
        """Append a value to a list"""
        return params

    def execute_pop(self, params: list) -> list:
        """Remove a certain element of a list with an index."""
        return params

    def execute_extend(self, params: list) -> list:
        """Extend a list with another list"""
        return params


class SliceNode:
    """
    Node used for slice objects.

    Slice objects are denoted by [start:end:step]
    """
    def __init__(self, start: int, end: int, step: int):
        self.start = start
        self.end = end
        self.step = step