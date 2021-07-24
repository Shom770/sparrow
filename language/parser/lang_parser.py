from ..resources.tokens.token_types import Token, TokenType
from ..resources.nodes.nodes import *
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

        if token.token_type == TokenType.KEYWORD and token.value == 'if':
            self.advance()
            result = self.if_expr(main_func=True)
            return result
        if token.token_type == TokenType.LPAREN:
            self.advance()
            result = self.expr()

            self.advance()
            return result

        if token.token_type == TokenType.BLOCK_CLOSE:
            self.advance()

        if token.token_type == TokenType.STRING:
            self.advance()
            return StringNode(token)

        if token.token_type == TokenType.IDENTIFIER:
            if self.tokens[self.pos + 1].token_type == TokenType.EQ:
                self.advance()
                self.advance()
                result = self.expr()
                return VarAssignNode(token.value, result)
            elif self.tokens[self.pos + 1].token_type != TokenType.EQ:
                self.advance()
                return VarAccessNode(token.value)

        elif token.token_type in (TokenType.INT, TokenType.FLOAT):
            self.advance()
            return NumberNode(token)

        elif token.token_type in (TokenType.PLUS, TokenType.MINUS) or token.value == 'not':
            self.advance()
            return UnaryOpNode(token, self.factor())

    def if_expr(self, main_func: bool) -> IfNode:
        """Expression used for if statements in the language"""
        cases = []
        append_to_cases = []
        conditions = []
        else_result = None
        keyword = (False, None)
        while self.current_tok.token_type != TokenType.BLOCK_OPEN:
            if self.current_tok.value in ('and', 'or'):
                keyword = (True, self.current_tok)
                self.advance()
            else:
                if self.current_tok.token_type in (TokenType.N_EQ, TokenType.IS_EQ, TokenType.GT, TokenType.LT,
                                                   TokenType.LTE, TokenType.GTE):
                    self.pos -= 1
                    self.current_tok = self.tokens[self.pos]
                result = self.factor()
                op_tok = self.current_tok
                self.advance()
                tok = self.factor()
                conditions.append(BinOpNode(result, op_tok, tok))
                if keyword[0] is True:
                    append_to_cases.append(BinOpNode(conditions[-2], keyword[1],
                                                     conditions[-1]))
                elif keyword[0] is False and self.current_tok.value not in ('and', 'or'):
                    append_to_cases.append(conditions[-1])
                keyword = (False, None)

        self.advance()

        expr_results = []
        while self.current_tok.token_type != TokenType.BLOCK_CLOSE:
            result = self.expr()
            if self.current_tok.token_type == TokenType.NEWLINE:
                self.advance()
            expr_results.append(result)

        cases.append((append_to_cases, expr_results))
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
