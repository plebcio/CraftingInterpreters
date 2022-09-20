import Interpreter
import time
from Stmt import Stmt, Function
import Environment

class LoxCallable:
    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        pass
    def arity(self) -> int:
        pass

class clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"

class LoxFunction(LoxCallable):
    def __init__(self, declatration: Function) -> None:
        self.declatration = declatration

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        enviorment = Environment.Environment(interpreter.globals)
        # FIXME should work but not sure
        for param, arg in zip(self.declatration.params, arguments):
            enviorment.define( param.lexeme, arg)

        interpreter.executeBlock(self.declatration.body, enviorment)
        return None

    def arity(self) -> int:
        return len(self.declatration.params)
    
    def __str__(self) -> str:
        return f"fn < {self.declaration.name.lexme}>"