from ..resources.tokens.token_types import Token, TokenType
from ..resources.nodes.nodes import *
from time import sleep
from typing import List


class Parser:
    """
    The class for the parser of the language.

    The parser creates the abstract syntax tree, which essentially has the nodes that the interpreter will use.
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = -1
        self.current_tok = None
        self.called = False
        self.advance()

    def advance(self) -> None:
        """
        Goes to the next token in the list of tokens, and sets a current token
        relative to the position in the list.
        """
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self) -> Union[None, List]:
        """
        The function used by main.py to parse through the tokens and create the abstract syntax tree.
        """
        parsing_result = []
        if self.current_tok is None:
            return None

        while self.current_tok is not None:
            result = self.expr()
            if self.current_tok is None:
                parsing_result.append(result)
                break
            if result is not None:
                parsing_result.append(result)
            if self.current_tok.token_type == TokenType.NEWLINE:
                self.advance()

        return parsing_result

    def expr(self) -> Union[BinOpNode, StringNode, NumberNode,
                            UnaryOpNode, VarAccessNode, VarAssignNode]:
        """
        Part of the syntax tree, expression would be the entire part of a certain segment.
        Mathematically, expression could either be the entire segment or a segment within parentheses,
        it could also be a certain token.
        """
        result = self.term()

        while self.current_tok is not None and self.current_tok.token_type in (TokenType.PLUS, TokenType.MINUS):
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.term())

        return result

    def term(self) -> Union[BinOpNode, StringNode, NumberNode,
                            UnaryOpNode, VarAccessNode, VarAssignNode]:
        """
        Part of the syntax tree, the term would be a certain operation between two numbers,
        or can be a certain token.
        """
        result = self.pow()
        while self.current_tok is not None and self.current_tok.token_type in (TokenType.MULT, TokenType.DIV):
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.pow())

        return result

    def pow(self) -> Union[BinOpNode, StringNode, NumberNode,
                           UnaryOpNode, VarAccessNode, VarAssignNode]:
        """
        This is either used to filter out exponential equations as the top of the order of operations,
        behind parentheses. However, usually it is a singular token.
        """
        result = self.factor()
        while self.current_tok is not None and self.current_tok.token_type == TokenType.EXP:
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.factor())

        return result

    def factor(self) -> Union[StringNode, NumberNode,
                              UnaryOpNode, VarAccessNode, VarAssignNode]:
        """
        Part of a syntax tree, this is a certain token or an item (when it comes to unary operations),
        assignment of nodes will go on in this function.
        """
        token = self.current_tok
        if token is not None:
            if token.token_type == TokenType.KEYWORD and token.value == 'return':
                self.advance()
                return_expr = self.expr()
                return ReturnNode(return_expr)

            elif token.token_type == TokenType.KEYWORD and token.value == "object":
                self.advance()
                result = self.obj_expr()
                return result

            elif token.token_type == TokenType.KEYWORD and token.value == 'for':
                self.advance()
                result = self.for_expr()
                return result

            elif token.token_type == TokenType.KEYWORD and token.value == "define":
                self.advance()
                result = self.create_function_expr()
                return result

            elif token.token_type == TokenType.KEYWORD and token.value == 'while':
                self.advance()
                result = self.while_expr()
                return result

            elif token.token_type == TokenType.KEYWORD and token.value == 'if':
                self.advance()
                result = self.if_expr(main_func=True)
                return result

            elif token.token_type == TokenType.LPAREN:
                self.advance()
                result = self.expr()

                self.advance()
                return result

            elif token.token_type == TokenType.BLOCK_CLOSE:
                self.advance()

            elif token.token_type == TokenType.LIST:
                res = {}
                for idx, ele in enumerate(token.value.values()):
                    if '"' in ele:
                        res[idx] = StringNode(Token(TokenType.STRING, ele.replace("'", '').replace('"', '')))
                    else:
                        res[idx] = NumberNode(Token(TokenType.INT if '.' not in ele else TokenType.FLOAT, ele))
                self.advance()
                return ListNode(res)

            elif token.token_type == TokenType.STRING:
                self.advance()
                return StringNode(token)

            elif token.token_type in (TokenType.INT, TokenType.FLOAT):
                self.advance()
                return NumberNode(token)

            elif token.token_type in (TokenType.PLUS, TokenType.MINUS) or token.value == 'not':
                self.advance()
                return UnaryOpNode(token, self.factor())

            elif token.token_type == TokenType.SLICE:
                self.advance()
                token.value = list(map(int, token.value))
                return SliceNode(token.value[0], token.value[1], token.value[2])

            elif self.pos + 1 < len(self.tokens):
                if (self.tokens[self.pos + 1].token_type in
                    (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT,
                     TokenType.LT, TokenType.GTE, TokenType.LTE) or
                    self.tokens[self.pos + 1].value in ('and', 'or')) and \
                        not self.called:
                    self.called = True
                    result = self.logical_expr(block=False)
                    self.called = False
                    return result

            if token.token_type == TokenType.IDENTIFIER:
                if self.tokens[self.pos + 1].token_type == TokenType.EQ:
                    self.advance()
                    self.advance()
                    result = self.expr()
                    return VarAssignNode(token.value, result)
                elif self.tokens[self.pos + 1].token_type == TokenType.LPAREN:
                    result = self.function_call_expr()
                    return result
                elif self.tokens[self.pos + 1].token_type == TokenType.ACCESS:
                    self.advance()
                    self.advance()
                    access_node = AccessNode(VarAccessNode(token.value), self.factor())
                    if self.current_tok.token_type == TokenType.EQ:
                        self.advance()
                        result = self.expr()
                        return VarAssignNode(access_node, result)
                    else:
                        return access_node
                else:
                    self.advance()
                    return VarAccessNode(token.value)

        self.called = False

    def function_call_expr(self) -> FunctionCallNode:
        """Used when function is called"""
        func_name = self.current_tok.value
        if func_name in ('print', 'input', 'input_int', 'is_number', 'is_string',
                         'is_list', 'pop', 'extend', 'append'):
            built_in = True
        else:
            built_in = False
        self.advance()
        self.advance()
        params = []
        while self.current_tok.token_type != TokenType.RPAREN:
            if self.current_tok.token_type == TokenType.SEPARATOR:
                self.advance()
            params.append(self.expr())
        self.advance()
        if built_in:
            return ExecuteBuiltInsNode(func_name, params)
        else:
            return FunctionCallNode(func_name, params)

    def create_function_expr(self) -> FunctionNode:
        """Creating the FunctionNode when defining a function."""
        name = self.current_tok.value
        symbol_table = SymbolTable()
        self.advance()
        self.advance()
        params = []
        while self.current_tok.token_type != TokenType.RPAREN:
            if self.current_tok.token_type == TokenType.SEPARATOR:
                self.advance()
            symbol_table[self.current_tok.value] = Number(0)
            params.append(self.current_tok)
            self.advance()
        self.advance()
        self.advance()
        body = []
        self.advance()
        while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
            result = self.expr()
            if self.current_tok.token_type == TokenType.NEWLINE:
                self.advance()
            body.append(result)
        self.advance()

        return FunctionNode(func_name=name, params=params, symbol_table=symbol_table, body=body)

    def parentheses_logical_expr(self) -> Union[List, bool]:
        """Helper function for dealing with parenthesized logical expressions"""
        paren_ran = True
        other_paren_ran = False
        premature_token = False
        keyword_in_paren = (False, None)
        append_to_paren = []
        paren_cases = []
        self.advance()
        while self.current_tok.token_type != TokenType.RPAREN:
            if self.current_tok.token_type == TokenType.LPAREN:
                result, paren_ran, other_paren_ran = self.parentheses_logical_expr()
                other_paren_ran = True

            if self.current_tok.value in ('and', 'or', 'not'):
                keyword_in_paren = (True, self.current_tok)
                self.advance()
            else:
                if self.current_tok.token_type in (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                                                   TokenType.LTE, TokenType.GTE, TokenType.PLUS, TokenType.MINUS,
                                                   TokenType.DIV, TokenType.MULT, TokenType.EXP):
                    if not (self.tokens[self.pos + 1].token_type in (
                            TokenType.INT, TokenType.IDENTIFIER, TokenType.STRING,
                            TokenType.FLOAT) and
                            self.tokens[self.pos - 1].token_type not in (
                                    TokenType.INT, TokenType.IDENTIFIER, TokenType.STRING,
                                    TokenType.FLOAT)):
                        premature_token = True
                        result = append_to_paren[-1]
                        paren_cases.remove(result)

                if not other_paren_ran and not premature_token:
                    result = self.factor()
                if self.current_tok.token_type in (
                        TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                        TokenType.LTE, TokenType.GTE, TokenType.PLUS, TokenType.MINUS,
                        TokenType.MULT, TokenType.DIV, TokenType.EXP):
                    op_tok = self.current_tok
                    self.advance()
                    tok = self.factor()
                    append_to_paren.append(BinOpNode(result, op_tok, tok))
                else:
                    append_to_paren.append(result)
                if keyword_in_paren[0] is True:
                    if keyword_in_paren[1].value in ('and', 'or'):
                        paren_cases.append(BinOpNode(append_to_paren[-2], keyword_in_paren[1],
                                                     append_to_paren[-1]))
                    else:
                        paren_cases.append(UnaryOpNode(keyword_in_paren[1], append_to_paren[-1]))
                elif keyword_in_paren[0] is False and self.current_tok.value not in ('and', 'or'):
                    paren_cases.append(append_to_paren[-1])
                keyword_in_paren = (False, None)
        return paren_cases, paren_ran, other_paren_ran

    def logical_expr(self, block: bool) -> List[tuple]:
        """Helper function for dealing with logical operators"""
        cases = []
        keyword = (False, None)
        append_to_cases = []
        premature_token = False
        conditions = []
        paren_ran = False
        while self.current_tok.token_type != TokenType.BLOCK_OPEN and self.current_tok.token_type != TokenType.NEWLINE:
            if self.current_tok.value in ('and', 'or', 'not'):
                keyword = (True, self.current_tok)
                self.advance()
            else:
                if self.current_tok.token_type in (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                                                   TokenType.LTE, TokenType.GTE, TokenType.PLUS, TokenType.MINUS,
                                                   TokenType.DIV, TokenType.MULT, TokenType.EXP):
                    if not (self.tokens[self.pos + 1].token_type in (
                            TokenType.INT, TokenType.IDENTIFIER, TokenType.STRING,
                            TokenType.FLOAT) and
                            self.tokens[self.pos - 1].token_type not in (
                                    TokenType.INT, TokenType.IDENTIFIER, TokenType.STRING,
                                    TokenType.FLOAT)):
                        result = conditions[-1]
                        append_to_cases.remove(result)
                        premature_token = True

                if self.current_tok.token_type == TokenType.LPAREN:
                    paren_cases, paren_ran, _ = self.parentheses_logical_expr()
                    for res in paren_cases:
                        conditions.append(res)

                if self.current_tok.token_type != TokenType.BLOCK_OPEN:
                    if self.current_tok.token_type == TokenType.RPAREN:
                        self.advance()
                    if self.current_tok.token_type in (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                                                       TokenType.LTE, TokenType.GTE) and self.tokens[self.pos - 1] in \
                            (TokenType.IDENTIFIER, TokenType.INT, TokenType.FLOAT, TokenType.STRING):
                        self.pos -= 1
                        self.current_tok = self.tokens[self.pos]
                    if not paren_ran and not premature_token:
                        result = self.factor()
                    if self.current_tok.token_type in (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                                                       TokenType.LTE, TokenType.GTE, TokenType.PLUS, TokenType.MINUS,
                                                       TokenType.MULT, TokenType.DIV, TokenType.EXP):
                        op_tok = self.current_tok
                        self.advance()
                        tok = self.factor()
                        conditions.append(BinOpNode(result if not paren_ran else conditions[-1], op_tok, tok))
                    else:
                        if not paren_ran:
                            conditions.append(result)
                    paren_ran = False
                if keyword[0] is True:
                    if keyword[1].value in ('and', 'or'):
                        append_to_cases.append(BinOpNode(conditions[-2], keyword[1],
                                                         conditions[-1]))
                    else:
                        append_to_cases.append(UnaryOpNode(keyword[1], conditions[-1]))
                elif keyword[0] is False and self.current_tok.value not in ('and', 'or'):
                    append_to_cases.append(conditions[-1])
                keyword = (False, None)
                premature_token = False

        if block:
            expr_results = []
            self.advance()
            while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
                result = self.expr()
                if self.current_tok.token_type == TokenType.NEWLINE:
                    self.advance()
                expr_results.append(result)
            cases.append((append_to_cases, expr_results))
        else:
            cases.append(*append_to_cases)

        return cases

        self.advance()

    def obj_expr(self) -> ObjectNode:
        """Expression used to parse through an object in the language"""
        name = self.current_tok.value
        if self.tokens[self.pos + 1].token_type == TokenType.LPAREN:
            self.advance()
            self.advance()
            inherit = self.current_tok.value
            self.advance()
        else:
            inherit = None
        symbol_table = SymbolTable()
        methods = {}
        special_methods = {'init': None}
        attrs = {}
        global_attrs = []
        self.advance()
        self.advance()
        while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
            if self.current_tok.value == 'cls' and self.current_tok.token_type == TokenType.KEYWORD:
                self.advance()
                global_attrs.append(self.factor())
            else:
                result = self.factor()
                if isinstance(result, FunctionNode):
                    methods[result.func_name] = result
                    if result.func_name in special_methods.keys():
                        del methods[result.func_name]
                        special_methods[result.func_name] = result

                    for line in result.body:
                        if isinstance(line, VarAssignNode):
                            attrs[line] = line
                elif isinstance(result, VarAssignNode):
                    attrs[result] = result
            self.advance()

        return ObjectNode(name, methods, special_methods, attrs, symbol_table, global_attrs, inherit)


    def if_expr(self, main_func: bool) -> IfNode:
        """Expression used for if statements in the language"""
        else_result = None
        self.called = True
        cases = self.logical_expr(block=True)
        self.called = False

        self.advance()
        if self.current_tok.token_type == TokenType.NEWLINE:
            self.advance()

        if self.current_tok is not None and self.current_tok.value == 'elif':
            self.advance()
            result = self.if_expr(main_func=False)
            cases.append(*result)

        if main_func is True and self.current_tok is not None and self.current_tok.value == 'else':
            self.advance()
            self.advance()
            self.advance()
            else_results = []
            while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
                result = self.expr()
                if self.current_tok.token_type == TokenType.NEWLINE:
                    self.advance()
                else_results.append(result)
            self.advance()
            else_result = else_results

        if main_func:
            return IfNode(cases, else_case=else_result)
        else:
            return cases

    def for_expr(self) -> ForNode:
        """Function for defining the node of for loops"""
        # advance past the parentheses
        self.advance()
        if self.current_tok.token_type == TokenType.IDENTIFIER:
            name = self.current_tok.value
            self.advance()
            self.advance()
            start_value = self.factor()
            var_name = VarAssignNode(name, start_value)
        self.advance()
        end_value = self.factor()
        self.advance()
        if self.current_tok.token_type == TokenType.INT or self.current_tok.token_type == TokenType.MINUS:
            step_value = self.factor()
            self.advance()
        else:
            step_value = NumberNode(Token(TokenType.INT, '1'))
        self.advance()
        body = []
        while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
            result = self.expr()
            if self.current_tok.token_type == TokenType.NEWLINE:
                self.advance()
            body.append(result)
        self.advance()

        return ForNode(var_name, start_value, end_value, step_value, body)

    def while_expr(self) -> WhileNode:
        """Function for while loops"""
        cond = self.logical_expr(block=False)
        self.advance()
        body = []
        self.advance()
        while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
            result = self.expr()
            if self.current_tok.token_type == TokenType.NEWLINE:
                self.advance()
            body.append(result)
        self.advance()
        return WhileNode(cond, body)
