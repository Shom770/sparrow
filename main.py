from language.lexer.lexer import Lexer
from language.parser.lang_parser import Parser
from language.interpreter.lang_interpreter import Interpreter

def run():
    text = ''
    with open('run/interpret.txt', 'r') as file:
        for line in file:
            text += f"{line}\n"

    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreted_results = [interpreter.visit(to_parse) for to_parse in ast]
    return interpreted_results


print(run())