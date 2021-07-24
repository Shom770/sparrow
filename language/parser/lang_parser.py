from ..resources.tokens.token_types import TokenType
from ..resources.nodes.nodes import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        parsing_result = []
        if self.current_tok is None:
            return None

        while self.current_tok is not None:
            result = self.expr()
            if self.current_tok.token_type == TokenType.NEWLINE:
                parsing_result.append(result)
                self.advance()

        return parsing_result

    def expr(self):
        result = self.term()

        while self.current_tok is not None and self.current_tok.token_type in (TokenType.PLUS, TokenType.MINUS):
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.term())

        return result

    def term(self):
        result = self.pow()
        while self.current_tok is not None and self.current_tok.token_type in (TokenType.MULT, TokenType.DIV):
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.pow())

        return result

    def pow(self):
        result = self.factor()
        while self.current_tok is not None and self.current_tok.token_type == TokenType.EXP:
            symbol = self.current_tok
            self.advance()
            result = BinOpNode(result, symbol, self.factor())

        return result

    def factor(self):
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
