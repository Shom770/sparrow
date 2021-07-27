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
        self.symbol_table["true"] = Number(1)
        self.symbol_table["false"] = Number(0)
        self.symbol_table["null"] = Number(0)

    def visit(self, node: Union[NumberNode, BinOpNode, StringNode, UnaryOpNode,
                                VarAssignNode, VarAccessNode]) -> Union[Number, String]:
        """Visits node inputted with the functions below."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node: None):
        """Raised when the visit method is not specified for a certain node."""
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    def visit_ForNode(self, node: ForNode) -> None:
        node_var = self.visit(node.var_name)
        node_var = VarAccessNode(node.var_name.name)
        end_value = node.end_value
        body = node.body
        step_value = node.step_value
        check = node.start_value
        if step_value > 0:
            condition = lambda: check < end_value
        else:
            condition = lambda: check > end_value

        while condition() is True:
            for expr in body:
                if expr is not None:
                    self.visit(expr)
            self.symbol_table[node_var.name] += Number(step_value)
            check += step_value

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
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(self.visit(node.left_node) != self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(self.visit(node.left_node) == self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(self.visit(node.left_node) <= self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(self.visit(node.left_node) >= self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.LT:
                return Number(self.visit(node.left_node) < self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.GT:
                return Number(self.visit(node.left_node) > self.visit(node.right_node))
            elif node.op_tok.value == 'and':
                return Number(self.visit(node.left_node)).anded_by(self.visit(node.right_node))
            elif node.op_tok.value == 'or':
                return Number(self.visit(node.left_node)).ored_by(self.visit(node.right_node))

        elif type(self.visit(node.left_node)).__name__ == 'String' and \
                type(self.visit(node.right_node)).__name__ == 'String':
            if node.op_tok.token_type == TokenType.PLUS:
                return String(self.visit(node.left_node)) + String(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.MINUS:
                return String(self.visit(node.left_node)) - String(self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(self.visit(node.left_node) != self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(self.visit(node.left_node) == self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(self.visit(node.left_node) <= self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(self.visit(node.left_node) >= self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.LT:
                return Number(self.visit(node.left_node) < self.visit(node.right_node))
            elif node.op_tok.token_type == TokenType.GT:
                return Number(self.visit(node.left_node) > self.visit(node.right_node))

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
        elif node.op_tok.value == 'not':
            return number.notted_by()

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

    def visit_list(self, list_to_visit: list) -> Number:
        """
        The visit_list method is for visiting logical expressions,
        containing things like <, >, <=, >=, and, or, not, etc.
        """
        passed_cases = []
        for node in list_to_visit:
            result = self.visit(node)
            passed_cases.append(result)

        if False in [num.value == 1 for num in passed_cases]:
            return self.symbol_table["false"]
        else:
            return self.symbol_table["true"]

    def visit_IfNode(self, node: IfNode) -> List:
        """
        Interprets an if statement.

        IfNode is a node class used for if statements, with the optional elif and else statements following it.
        """
        for case in node.cases:
            condition = case[0]
            passed_cases = []
            for idx, cond in enumerate(condition):
                result = self.visit(cond)
                passed_cases.append(result)
            expr = case[-1]
            if False in [num.value == 1 for num in passed_cases]:
                pass
            else:
                block_results = []
                for line in [elem for elem in expr if elem is not None]:
                    res = self.visit(line)
                    block_results.append(res)
                return block_results

        if node.else_case:
            expr = node.else_case

            block_results = []
            for line in [elem for elem in expr if elem is not None]:
                res = self.visit(line)
                block_results.append(res)

            return block_results
