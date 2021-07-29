from enum import Enum


class TokenType(Enum):
    """An Enum-derived class that defines token types in the language."""
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
    IS_EQ = 19
    N_EQ = 20
    GT = 21
    LT = 22
    LTE = 23
    GTE = 24
    ACCESS = 25


class Token:
    """The class for tokens, where tokens are created by the lexer and used by the parser to create the nodes."""
    def __init__(self, token_type: TokenType, value: str) -> None:
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.token_type}:{self.value}'
        return f'{self.token_type}'
