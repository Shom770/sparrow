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
            if self.current_tok.token_type == TokenType.NEWLINE:
                parsing_result.append(result)
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

        if token.token_type == TokenType.LPAREN:
            self.advance()
            result = self.expr()

            self.advance()
            return result

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

        elif token.token_type in (TokenType.PLUS, TokenType.MINUS):
            self.advance()
            return UnaryOpNode(token, self.factor())
