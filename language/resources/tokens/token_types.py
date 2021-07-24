from enum import Enum


class TokenType(Enum):
    IDENTIFIER = 1
    KEYWORD = 2
    BLOCK_OPEN = 3
    BLOCK_CLOSE = 4
    METHOD = 5
    EQ = 6
    INT = 7
    FLOAT = 8
    PLUS = 9
    MINUS = 10
    MULT = 11
    DIV = 12
    EXP = 13
    NEWLINE = 14
    LPAREN = 15
    RPAREN = 16
    SEPARATOR = 17
    STRING = 18


class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value:
            return f'{self.token_type}:{self.value}'
        return f'{self.token_type}'
