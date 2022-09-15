import sys
import Scanner
from Token import Token, TokenType
import Parser
import AstPrinter
import Interpreter
from Flags import Flags

Flags = Flags()

# globals ? idk java thing
interpreter = Interpreter.Interpreter()

class LoxRuntimeError(RuntimeError):
    def __init__(self, token:Token, mess:str) -> None:
        self.mess = mess # ??? FIXME ???
        self.token = token

class LoxBreakIter(LoxRuntimeError):
    def __init__(self, token: Token, mess: str) -> None:
        super().__init__(token, mess)
class LoxContinueIter(LoxRuntimeError):
    def __init__(self, token: Token, mess: str) -> None:
        super().__init__(token, mess)


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

    if Flags.hadError:
        sys.exit(65)
    if Flags.hadRuntimeError:
        sys.exit(70)


def runPrompt():
    while True:
        print("> ", end="")
        try:
            line = input()
            run(line, REPLmode=True) # REPL mode
            Flags.hadError = False
        except EOFError:
            break


def run(source, REPLmode = False):
    scanner = Scanner.Scanner(source)
    tokens:'list[Token]' = scanner.scanTokens()

    # for token in tokens:
    #     print(token)

    stmt_list = Parser.Parser(tokens, inREPLmode = REPLmode).parse()

    if stmt_list == None:
        return

    out_str = interpreter.interpret(stmt_list)
    if Flags.hadRuntimeError or out_str is None:
        return

    print(out_str)

# -- error stuff ---
def error(token: Token, mess: str):
    if token.type == TokenType.EOF:
        report(token.line, " at end", mess)
    else:
        report(token.line, " at '"+ token.lexeme + "'", mess)

def runtimeError(error: LoxRuntimeError):
    print(error.mess)
    print("[line " + str(error.token.line) + "]")
    Flags.hadRuntimeError = True

def report(line, where, mess):
    print(f"[line  {line} ] Error {where} : {mess}")
    Flags.hadError = True


if __name__ == "__main__":
    main()

