from Expr import Lambda
import Interpreter
import time
from Stmt import Stmt, Function
import Environment
import pylox

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
    def __init__(self, declatration: Function, closure: 'Environment.Environment') -> None:
        self.declatration = declatration
        self.closure = closure

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        enviorment = Environment.Environment(self.closure)

        for param, arg in zip(self.declatration.params, arguments):
            enviorment.define( param.lexeme, arg)

        try:
            interpreter.executeBlock(self.declatration.body, enviorment)
        except pylox.ReturnExep as ex:
            return ex.value
        
        return None

    def arity(self) -> int:
        return len(self.declatration.params)
    
    def __str__(self) -> str:
        return f"fn < {self.declaration.name.lexme}>"

class LoxLambda(LoxCallable):
    def __init__(self, declatration: Lambda, closure: 'Environment.Environment') -> None:
        self.declatration = declatration
        self.closure = closure

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        enviorment = Environment.Environment(self.closure)

        for param, arg in zip(self.declatration.params, arguments):
            enviorment.define( param.lexeme, arg)

        try:
            interpreter.executeBlock(self.declatration.body, enviorment)
        except pylox.ReturnExep as ex:
            return ex.value
        
        return None

    def arity(self) -> int:
        return len(self.declatration.params)
    
    def __str__(self) -> str:
        return f"anmoymous lambda expression"
