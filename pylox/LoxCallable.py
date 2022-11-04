import time

from Expr import Literal, Lambda
import Interpreter
from Token import Token
from Stmt import Function
import Environment
import pylox

class LoxCallable:
    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        pass
    def arity(self) -> int:
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declatration: Function, closure: 'Environment.Environment', isInitializer: bool = False) -> None:
        self.declatration = declatration
        self.closure = closure
        self.isInitializer = isInitializer

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        enviorment = Environment.Environment(self.closure)

        for param, arg in zip(self.declatration.params, arguments):
            enviorment.define( param.lexeme, arg)

        try:
            interpreter.executeBlock(self.declatration.body, enviorment)
        except pylox.ReturnExep as ex:
            if self.isInitializer:
                return self.closure.getAt(0, "this")
            return ex.value
        
        if self.isInitializer:
            return self.closure.getAt(0, "this")
        return None

    def arity(self) -> int:
        return len(self.declatration.params)
    
    def bind(self, instance: 'LoxInstance'):
        enviorment: Environment.Environment = Environment.Environment(self.closure)
        enviorment.define("this", instance)
        return LoxFunction(self.declatration, enviorment, self.isInitializer)

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


class LoxClass(LoxCallable):
    def __init__(self, name, superclass: 'LoxClass',  methods: 'dict[Function]') -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        instance = LoxInstance(self)
        initializer: LoxFunction = self.findMethod("init")
        if initializer != None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def findMethod(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.superclass != None:
            return self.superclass.findMethod(name)
        
        return None

    def arity(self) -> int:
        initializer: LoxFunction = self.findMethod("init")
        if initializer != None:
            return initializer.arity()
        return 0

    def __str__(self) -> str:
        return self.name


# ---- loxIntance class (didnt bother with new file) ---
class LoxInstance():
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method: LoxFunction = self.klass.findMethod(name.lexeme)
        if method != None:
            return method.bind(self)
        
        raise pylox.LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")


    def set(self, name: Token, value):
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return self.klass.name + " instance"


# ---- native functions -----

class clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"

class loxInput(LoxCallable):
    def arity(self) -> int:
        return 0
    
    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        return input()

    def __str__(self) -> str:
        return "<native fn>"


# ------ lists ---------   
class LoxList(LoxCallable):
    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        return LoxListInstance()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<class 'list'>"

class LoxListInstance(LoxInstance):
    def __init__(self) -> None:
        self.list = []

    def get(self, name: Token):
        if name.lexeme == "insert":
            return ListInsert(self, name)
        elif name.lexeme == "get":
            return listGet(self, name)
        elif name.lexeme == "append":
            return listAppend(self, name)
        elif name.lexeme == "len":
            return listLen(self, name)

        raise pylox.LoxRuntimeError(name, f"Undefined ''''''''list'''''''' property '{name.lexeme}'.")

    def set(self, name: Token, value):
        raise pylox.LoxRuntimeError(name, "Can't set properties to built-in 'list' class")

    def __str__(self) -> str:
        return self.list.__str__()

# suport list classes
class ListInsert(LoxFunction):
    def __init__(self, mother_list, name:Token) -> None:
        self.this = mother_list
        self.name = name

    def arity(self) -> int:
        return 2

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        position = arguments[0]
        value = arguments[1]
        if not isinstance(position, float) or not position.is_integer():
            raise pylox.LoxRuntimeError(self.name, "List index must be an intiger")
        
        return self.this.list.insert(int(position), value)

    def __str__(self) -> str:
        return "<native fn>"

class listGet(LoxFunction):
    def __init__(self, mother_list, name:Token) -> None:
        self.this = mother_list
        self.name = name

    def arity(self) -> int:
        return 1

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        position = arguments[0]
        if not isinstance(position, float) or not position.is_integer():
            raise pylox.LoxRuntimeError(self.name, "List index must be an intiger")
        
        return self.this.list[int(position)]

    def __str__(self) -> str:
        return "<native fn>"

class listAppend(LoxFunction):
    def __init__(self, mother_list, name:Token) -> None:
        self.this = mother_list
        self.name = name

    def arity(self) -> int:
        return 1

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        value = arguments[0]
        return self.this.list.append(value)

    def __str__(self) -> str:
        return "<native fn>"

class listLen(LoxFunction):
    def __init__(self, mother_list: LoxListInstance, name:Token) -> None:
        self.this = mother_list
        self.name = name

    def arity(self) -> int:
        return 0

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        return len(self.this.list)

    def __str__(self) -> str:
        return "<native fn>"

# ------ end of list stuff -------

class loxToNum(LoxCallable):
    def arity(self) -> int:
        return 1

    def call(self, interpreter: 'Interpreter.Interpreter', arguments):
        try:
            return float(arguments[0])
        except ValueError:
            raise pylox.NativeFuncError("'num' argument must be a number")
            
    def __str__(self) -> str:
        return "<native fn>"
