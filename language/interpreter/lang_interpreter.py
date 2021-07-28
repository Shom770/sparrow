from ..resources.tokens.token_types import TokenType
from ..resources.symbol_table.symbol_table import SymbolTable
from ..resources.nodes.nodes import *
from typing import Union, Optional

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
                                VarAssignNode, VarAccessNode], symbol_table: Optional[SymbolTable] = None) -> Union[Number, String]:
        """Visits node inputted with the functions below."""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        if symbol_table is None:
            symbol_table = self.symbol_table
        return method(node, symbol_table)

    def no_visit_method(self, node: None, symbol_table: SymbolTable):
        """Raised when the visit method is not specified for a certain node."""
        raise Exception(f'No visit_{type(node).__name__} method defined.')

    def visit_FunctionNode(self, node: FunctionNode, symbol_table: SymbolTable) -> None:
        """
        Defines function in the global symbol table,
        stored for reference till function call.
        """
        self.symbol_table[node.func_name] = node

    def visit_ReturnNode(self, node: ReturnNode, symbol_table: SymbolTable) -> Union[Number, String]:
        result = self.visit(node.expression, symbol_table)
        return result

    def visit_FunctionCallNode(self, node: FunctionCallNode, symbol_table: SymbolTable) -> None:
        """Executes function called with said parameters"""
        func = symbol_table[node.func_name]
        for param, name_of_param in zip(node.params, func.params):
            func.local_symbol_table[name_of_param.value] = self.visit(param, symbol_table)

        for line in func.body:
            if line:
                result = self.visit(line, func.local_symbol_table)
                if isinstance(line, ReturnNode):
                    return result
                elif isinstance(result, ReturnNode):
                    return self.visit(result, func.local_symbol_table)

    def visit_WhileNode(self, node: WhileNode, symbol_table: SymbolTable) -> None:
        """
        Executes code within while loop.

        WhileNode is a class interpreted by this function which will be checking a condition and run
        code within the block while under that certain condition.
        """
        while True:
            if self.visit(node.cond, symbol_table).value == 0:
                break
            else:
                for expr in node.body:
                    if expr is not None:
                        if isinstance(expr, ReturnNode):
                            return expr
                        res = self.visit(expr, symbol_table)
                        if isinstance(res, ReturnNode):
                            return res

    def visit_ForNode(self, node: ForNode, symbol_table: SymbolTable) -> Union[None, ReturnNode]:
        """
        Executes code within the for loop.

        ForNode is a class interpreted by this function which sets forth the guidelines
        for said for loop.
        """
        # initializing node_var
        symbol_table[node.var_name.name] = self.visit(node.var_name.value, symbol_table)
        end_value = self.visit(node.end_value, symbol_table)
        body = node.body
        step_value = self.visit(node.step_value, symbol_table)
        check = self.visit(node.start_value, symbol_table)
        if step_value.value > 0:
            condition = lambda: bool((check < end_value).value)
        else:
            condition = lambda: bool((check > end_value).value)

        while condition() is True:
            for expr in body:
                if expr is not None:
                    if isinstance(expr, ReturnNode):
                        return expr
                    res = self.visit(expr, symbol_table)
                    if isinstance(res, ReturnNode):
                        return res
            symbol_table[node.var_name.name] += Number(step_value)
            check = check + step_value

    def visit_NumberNode(self, node: NumberNode, symbol_table: SymbolTable) -> String:
        """
        Returns a Number class from NumberNode

        NumberNode is a class for an integer or float type in this language.
        """
        return Number(node.tok.value)

    def visit_StringNode(self, node: StringNode, symbol_table: SymbolTable) -> String:
        """
        Returns a String class from StringNode

        StringNode is a class for the string type in this language.
        """
        return String(node.tok.value)

    def visit_BinOpNode(self, node: BinOpNode, symbol_table: SymbolTable) -> Union[Number, String]:
        """
        Returns a Number or String class depending on the binary operation being done

        Shortens binary operation to a single result
        """
        left_node = self.visit(node.left_node, symbol_table)
        right_node = self.visit(node.right_node, symbol_table)
        if type(left_node).__name__ == 'Number' and \
                type(right_node).__name__ == 'Number':
            if node.op_tok.token_type == TokenType.PLUS:
                return Number(left_node) + Number(right_node)
            elif node.op_tok.token_type == TokenType.MINUS:
                return Number(left_node) - Number(right_node)
            elif node.op_tok.token_type == TokenType.MULT:
                return Number(left_node) * Number(right_node)
            elif node.op_tok.token_type == TokenType.DIV:
                return Number(left_node) / Number(right_node)
            elif node.op_tok.token_type == TokenType.EXP:
                return Number(left_node) ** Number(right_node)
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(left_node != right_node)
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(left_node == right_node)
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(left_node <= right_node)
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(left_node >= right_node)
            elif node.op_tok.token_type == TokenType.LT:
                return Number(left_node < right_node)
            elif node.op_tok.token_type == TokenType.GT:
                return Number(left_node > right_node)
            elif node.op_tok.value == 'and':
                return Number(left_node).anded_by(right_node)
            elif node.op_tok.value == 'or':
                return Number(left_node).ored_by(right_node)

        elif type(left_node).__name__ == 'String' and \
                type(right_node).__name__ == 'String':
            if node.op_tok.token_type == TokenType.PLUS:
                return String(left_node.value) + String(right_node.value)
            elif node.op_tok.token_type == TokenType.MINUS:
                return String(left_node) - String(right_node)
            elif node.op_tok.token_type == TokenType.N_EQ:
                return Number(left_node != right_node)
            elif node.op_tok.token_type == TokenType.IS_EQ:
                return Number(left_node == right_node)
            elif node.op_tok.token_type == TokenType.LTE:
                return Number(left_node <= right_node)
            elif node.op_tok.token_type == TokenType.GTE:
                return Number(left_node >= right_node)
            elif node.op_tok.token_type == TokenType.LT:
                return Number(left_node < right_node)
            elif node.op_tok.token_type == TokenType.GT:
                return Number(left_node > right_node)

        elif (type(left_node).__name__ == 'String' and \
              isinstance(right_node.value, int)) or \
                type(right_node).__name__ == 'String' and \
                isinstance(left_node.value, int):
            if node.op_tok.token_type == TokenType.MULT:
                return String(left_node.value * Number(right_node).value)

    def visit_UnaryOpNode(self, node: UnaryOpNode, symbol_table: SymbolTable) -> Number:
        """
        Returns the same number or the negative version of said number.

        UnaryOpNode is a node class used for unary operations denoted by -{number} or +{number}
        """
        number = self.visit(node.node, symbol_table)

        if node.op_tok.token_type == TokenType.MINUS:
            return number * Number(-1)
        elif node.op_tok.token_type == TokenType.PLUS:
            return number
        elif node.op_tok.value == 'not':
            return number.notted_by()

    def visit_VarAssignNode(self, node: VarAssignNode, symbol_table: SymbolTable) -> None:
        """
        Assigns a variable in the symbol table

        VarAssignNode is a node class used for the assignment of a variable, denoted by 'identifier = value'.
        """

        assignment = self.visit(node.value, symbol_table)

        symbol_table[node.name] = assignment

    def visit_VarAccessNode(self, node: VarAccessNode, symbol_table: SymbolTable) -> Union[Number, String]:
        """
        Returns the value of a variable in the symbol table.

        VarAccessNode is a node class used for getting the value of a certain variable, denoted by 'identifier'.
        """
        try:
            res = symbol_table[node.name]
        except KeyError:
            if symbol_table != self.symbol_table:
                res = self.symbol_table[node.name]

        return res

    def visit_list(self, list_to_visit: list, symbol_table: SymbolTable) -> Number:
        """
        The visit_list method is for visiting logical expressions,
        containing things like <, >, <=, >=, and, or, not, etc.
        """
        passed_cases = []
        for node in list_to_visit:
            result = self.visit(node, symbol_table)
            passed_cases.append(result)

        if False in [num.value == 1 for num in passed_cases]:
            return self.symbol_table["false"]
        else:
            return self.symbol_table["true"]

    def visit_IfNode(self, node: IfNode, symbol_table: SymbolTable) -> Union[List, ReturnNode]:
        """
        Interprets an if statement.

        IfNode is a node class used for if statements, with the optional elif and else statements following it.
        """
        for case in node.cases:
            condition = case[0]
            passed_cases = []
            for idx, cond in enumerate(condition):
                result = self.visit(cond, symbol_table)
                passed_cases.append(result)
            expr = case[-1]
            if False in [num.value == 1 for num in passed_cases]:
                pass
            else:
                block_results = []
                for line in [elem for elem in expr if elem is not None]:
                    if isinstance(line, ReturnNode):
                        return line
                    res = self.visit(line, symbol_table)
                    block_results.append(res)
                return block_results

        if node.else_case:
            expr = node.else_case

            block_results = []
            for line in [elem for elem in expr if elem is not None]:
                if isinstance(line, ReturnNode):
                    return line
                res = self.visit(line, symbol_table)
                block_results.append(res)

            return block_results
