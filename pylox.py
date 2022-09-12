from pickle import TRUE
import sys
import Scanner
from Token import Token, TokenType
import Parser
import AstPrinter
import Interpreter

# globals ? idk java thing
hadError: bool
hadRuntimeError : bool
interpreter = Interpreter.Interpreter()

class LoxRuntimeError(RuntimeError):
    def __init__(self, token:Token, mess:str) -> None:
        self.mess = mess # ??? FIXME ???
        self.token = token

def main():
    global hadError, hadRuntimeError
    hadError = False
    hadRuntimeError = False
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)

    elif len(sys.argv) == 2:
        runFile(sys.argv[1])
    else:
        runPrompt()


def runFile(path):
    infile = open(path)
    buffer = infile.read()
    infile.close()
    run(buffer)

    if hadError:
        sys.exit(65)
    if hadRuntimeError:
        sys.exit(70)


def runPrompt():
    global hadError
    while True:
        print("> ", end="")
        try:
            line = input()
            run(line)
            hadError = False
        except EOFError:
            break


def run(source):
    global hadError, hadRuntimeError ,interpreter
    scanner = Scanner.Scanner(source)
    tokens:'list[Token]' = scanner.scanTokens()

    # for token in tokens:
    #     print(token)

    AstRoot = Parser.Parser(tokens).parse()
    if AstRoot is None:
        return

    printer = AstPrinter.AstPrinter()
    printer.print_out(AstRoot)
    out_str = interpreter.interpret(AstRoot)
    if hadRuntimeError or out_str is None:
        return

    print(out_str)

# -- error stuff ---
def error(token: Token, mess: str):
    if token.type == TokenType.EOF:
        report(token.line, " at end", mess)
    else:
        report(token.line, " at '"+ token.lexeme + "'", mess)

def runtimeError(error: LoxRuntimeError):
    global hadError, hadRuntimeError
    print(error.mess)
    print("[line " + str(error.token.line) + "]")
    hadError = True
    hadRuntimeError = True

def report(line, where, mess):
    print(f"[line  {line} ] Error {where} : {mess}")
    global hadError
    hadError = True


if __name__ == "__main__":
    main()

