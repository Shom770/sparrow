from ..resources.tokens.token_types import TokenType
from ..resources.symbol_table.symbol_table import SymbolTable
from ..resources.nodes.nodes import *
from typing import Union


class Interpreter:
    """
    Class for the interpreter of the language.

    The interpreter will read the abstract syntax tree and nodes and turn it into a specific value.
    """

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()

    def visit(self, node: Union[NumberNode, BinOpNode, StringNode, UnaryOpNode,
                                VarAssignNode, VarAccessNode]) -> Union[Number, String]:
        """Visits node inputted with the functions below."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node: None):
        """Raised when the visit method is not specified for a certain node."""
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    def visit_NumberNode(self, node: NumberNode) -> String:
        """
        Returns a Number class from NumberNode

        NumberNode is a class for an integer or float type in this language.
        """
        return Number(node.tok.value)

    def visit_StringNode(self, node: StringNode) -> String:
        """
        Returns a String class from StringNode

        StringNode is a class for the string type in this language.
        """
        return String(node.tok.value)

    def visit_BinOpNode(self, node: BinOpNode) -> Union[Number, String]:
        """
        Returns a Number or String class depending on the binary operation being done

        Shortens binary operation to a single result
        """
        if type(self.visit(node.left_node)).__name__ == 'Number' and \
                type(self.visit(node.right_node)).__name__ == 'Number':
            if node.op_tok.token_type == TokenType.PLUS:
                return Number(self.visit(node.left_node)) + Number(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.MINUS:
                return Number(self.visit(node.left_node)) - Number(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.MULT:
                return Number(self.visit(node.left_node)) * Number(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.DIV:
                return Number(self.visit(node.left_node)) / Number(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.EXP:
                return Number(self.visit(node.left_node)) ** Number(self.visit(node.right_node))
        elif type(self.visit(node.left_node)).__name__ == 'String' and \
                type(self.visit(node.right_node)).__name__ == 'String':
            if node.op_tok.token_type == TokenType.PLUS:
                return String(self.visit(node.left_node)) + String(self.visit(node.right_node))
            if node.op_tok.token_type == TokenType.MINUS:
                return String(self.visit(node.left_node)) - String(self.visit(node.right_node))

        elif (type(self.visit(node.left_node)).__name__ == 'String' and \
                isinstance(self.visit(node.right_node).value, int)) or \
                type(self.visit(node.right_node)).__name__ == 'String' and \
                isinstance(self.visit(node.left_node).value, int):
            if node.op_tok.token_type == TokenType.MULT:
                return String(self.visit(node.left_node).value * Number(self.visit(node.right_node)).value)

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Number:
        """
        Returns the same number or the negative version of said number.

        UnaryOpNode is a node class used for unary operations denoted by -{number} or +{number}
        """
        number = self.visit(node.node)

        if node.op_tok.token_type == TokenType.MINUS:
            return number * Number(-1)
        elif node.op_tok.token_type == TokenType.PLUS:
            return number

    def visit_VarAssignNode(self, node: VarAssignNode) -> None:
        """
        Assigns a variable in the symbol table

        VarAssignNode is a node class used for the assignment of a variable, denoted by 'identifier = value'.
        """
        # currently not added locality for symbol tables so they are only global for now

        assignment = self.visit(node.value)

        self.symbol_table[node.name] = assignment

    def visit_VarAccessNode(self, node: VarAccessNode) -> Union[Number, String]:
        """
        Returns the value of a variable in the symbol table.

        VarAccessNode is a node class used for getting the value of a certain variable, denoted by 'identifier'.
        """
        return self.symbol_table[node.name]
