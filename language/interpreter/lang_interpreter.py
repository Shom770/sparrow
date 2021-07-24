from ..resources.tokens.token_types import TokenType
from ..resources.symbol_table.symbol_table import SymbolTable
from ..resources.nodes.nodes import *


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    def visit_NumberNode(self, node):
        return Number(node.tok.value)

    def visit_StringNode(self, node):
        return String(node.tok.value)

    def visit_BinOpNode(self, node):
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

    def visit_UnaryOpNode(self, node):
        number = self.visit(node.node)

        if node.op_tok.token_type == TokenType.MINUS:
            return number * Number(-1)
        elif node.op_tok.token_type == TokenType.PLUS:
            return number

    def visit_VarAssignNode(self, node):
        assignment = self.visit(node.value)

        self.symbol_table[node.name] = assignment

    def visit_VarAccessNode(self, node):
        return self.symbol_table[node.name]
