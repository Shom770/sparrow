from ..resources.tokens.token_types import TokenType, Token
from string import ascii_letters

KEYWORDS = ['define', 'cls', 'give']
LETTERS_DIGITS = ascii_letters + '0123456789'


class Lexer:
    def __init__(self, text):
        self.text = text.replace('\n\n', '\n')
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def tokenize(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '\n':
                tokens.append(Token(TokenType.NEWLINE, '\n'))
                self.advance()
            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.make_string(self.current_char))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.SEPARATOR, ','))
                self.advance()
            elif self.current_char in '+-/*^()':
                tokens.append(self.make_operator())
            elif self.current_char == '{':
                tokens.append(Token(TokenType.BLOCK_OPEN, '{'))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TokenType.BLOCK_CLOSE, '}'))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TokenType.EQ, '='))
                self.advance()
            elif self.current_char in '0124356789.':
                tokens.append(self.make_number())
            elif self.current_char in LETTERS_DIGITS + '_':
                tokens.append(self.make_identifier())

        return tokens

    def make_identifier(self):
        id_str = ''
        while self.current_char is not None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TokenType.KEYWORD if id_str in KEYWORDS else TokenType.IDENTIFIER
        return Token(tok_type, id_str)

    def make_number(self):
        id_str = self.current_char
        dec_count = 0
        self.advance()
        while self.current_char is not None and self.current_char in '0123456789.':
            if self.current_char == '.':
                dec_count += 1
            if dec_count > 1:
                break
            id_str += self.current_char
            self.advance()

        if id_str.startswith('.'):
            id_str = '0' + id_str
        elif id_str.endswith('.'):
            id_str += '0'

        if dec_count <= 1:
            return Token(TokenType.INT if dec_count == 0 else TokenType.FLOAT, id_str)

    def make_string(self, character):
        id_str = ''
        self.advance()
        while self.current_char is not None and self.current_char != character:
            id_str += self.current_char
            self.advance()

        return Token(TokenType.STRING, id_str)

    def make_operator(self):
        if self.current_char == '+':
            token = Token(TokenType.PLUS, self.current_char)
        elif self.current_char == '-':
            token = Token(TokenType.MINUS, self.current_char)
        elif self.current_char == '*':
            token = Token(TokenType.MULT, self.current_char)
        elif self.current_char == '/':
            token = Token(TokenType.DIV, self.current_char)
        elif self.current_char == '^':
            token = Token(TokenType.EXP, self.current_char)
        elif self.current_char == '(':
            token = Token(TokenType.LPAREN, self.current_char)
        elif self.current_char == ')':
            token = Token(TokenType.RPAREN, self.current_char)

        self.advance()
        return token



