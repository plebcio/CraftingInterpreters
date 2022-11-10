from enum import Enum
from Expr import ExprVisitor, Expr, Binary, Grouping, Set, Super, This, Unary, Literal, Variable, Assign, Logical, Call, Lambda, Get
from Token import Token 
from Stmt import StmtVisitor, Stmt, Expression, Print,  Var, Block, If, While, StopIter, Function, Return, Class
import LoxCallable
from Environment import Environment
import pylox
import Interpreter

# helper stack
class Stack():
    def __init__(self) -> None:
        self.stack = []

    def push(self, obj):
        self.stack.append(obj)
    
    def pop(self):
        return self.stack.pop(-1)
    
    def isEmpty(self):
        return len(self.stack) == 0
        
    def peek(self):
        return self.stack[-1]

    def size(self):
        return len(self.stack)

class FunctionType(Enum):
    NONE = 0,
    FUNCTION = 1,
    METHOD = 2,
    INITIALIZER = 3

class ClassType(Enum):
    NONE = 0,
    CLASS = 1, 
    SUBCLASS = 2
# acual Resolver class

class Resolver(StmtVisitor, ExprVisitor):
    def __init__(self, interpreter: 'Interpreter.Interpreter') -> None:
        self.interpreter = interpreter
        self.scopes = Stack()
        self.currentFunction: FunctionType = FunctionType.NONE
        self.currentClass = ClassType.NONE

        self.localHadError = False
# ---------- Statements -----------------
    def firstResolve(self, stmtL):
        for stmt in stmtL:
            self.resolve(stmt)
        
        return self.localHadError

    def visitBlockStmt(self, stmt: Block):
        self.beginScope()
        for statement in stmt.statements:
            self.resolve(statement)
        self.endScope()
        return None
    
    def visitClassStmt(self, stmt: Class):
        enclosingClass: ClassType = self.currentClass
        self.currentClass = ClassType.CLASS
        
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass != None:
            self.currentClass = ClassType.SUBCLASS
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                pylox.error(stmt.superclass.name, "A class can't inherit from itself.")
                self.localHadError = True
            self.resolve(stmt.superclass)
            if stmt.superclass != None:
                self.beginScope()
                self.scopes.peek()["super"] = True

        self.beginScope()
        self.scopes.peek()["this"] = True
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER    
            self.resolveFunction(method, declaration)
        
        self.endScope()
        if stmt.superclass != None:
            self.endScope()
        self.currentClass = enclosingClass

    def visitVarStmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer != None:
            self.resolve(stmt.initializer)

        self.define(stmt.name)
        return None

    def visitFunctionStmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolveFunction(stmt, FunctionType.FUNCTION)

    # ---- boring resolutions ----
    def visitExpressionStmt(self, stmt: Expression):
        self.resolve(stmt.expression)
    
    def visitIfStmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch != None:
            self.resolve(stmt.elseBranch)
        
    def visitPrintStmt(self, stmt: Print):
        self.resolve(stmt.expression)

    def visitReturnStmt(self, stmt: Return):
        if self.currentFunction == FunctionType.NONE:
            pylox.error(stmt.keyword, "Can't return from top-level code")
            self.localHadError = True
            return
        if stmt.value != None:
            if self.currentFunction == FunctionType.INITIALIZER:
                pylox.error(stmt.keyword, "Can't return a value from an initializer")
                self.localHadError = True
                return
            self.resolve(stmt.value)
        
    def visitWhileStmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    # costume
    def visitStopiterStmt(self, stmt: StopIter):
        return

# --------- Expressions ----------------

    def visitVariableExpr(self, expr: Variable):
        if not self.scopes.isEmpty() and \
        self.scopes.peek().get(expr.name.lexeme) == False:
            pylox.error(expr.name, "Can't read local variable in its own initializer")
            self.localHadError = True
            return
        self.resolveLocal(expr, expr.name)
        return None

    def visitAssignExpr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)
        return None

    # --- boring resolutions ----
    def visitBinaryExpr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitCallExpr(self, expr: Call):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)

    def visitGetExpr(self, expr: Get):
        self.resolve(expr.object)

    def visitGroupingExpr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visitLiteralExpr(self, expr: Literal):
        return

    def visitLogicalExpr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitSetExpr(self, expr: Set):
        self.resolve(expr.value)
        self.resolve(expr.obj)

    def visitSuperExpr(self, expr: Super):
        if self.currentClass == ClassType.NONE:
            pylox.error(expr.keyword, "Can't use 'super' ouside of a class")
            self.localHadError = True
        elif self.currentClass == ClassType.CLASS:
            pylox.error(expr.keyword, "Cant use 'super' in a class with no superclass")
            self.localHadError = True
            
        self.resolveLocal(expr, expr.keyword)

    def visitThisExpr(self, expr: This):
        if self.currentClass == ClassType.NONE:
            pylox.error(expr.keyword, "Can't use 'this' outside of a class")
            self.localHadError = True
            return
        self.resolveLocal(expr, expr.keyword)

    def visitUnaryExpr(self, expr: Unary):
        self.resolve(expr.right)

    # custom   
    def visitLambdaExpr(self, expr: Lambda):
        self.beginScope()
        for param in expr.params:
            self.declare(param)
            self.define(param)
        for stmt in expr.body:
            self.resolve(stmt)   
        self.endScope()

# ----------- helpers ----------------

    def resolve(self, stmt: Stmt):
        stmt.accept(self)

    def resolveFunction(self, function: Function, ftype: FunctionType.FUNCTION):
        enclosingFunction = self.currentFunction
        self.currentFunction = ftype
        
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        for stmt in function.body:
            self.resolve(stmt)
        self.endScope()

        self.currentFunction = enclosingFunction


    def beginScope(self):
        self.scopes.push(dict()) # ??? FIXME

    def endScope(self):
        self.scopes.pop()
    
    def declare(self, name: Token):
        if self.scopes.isEmpty():
            return
        scope = self.scopes.peek()
        if name.lexeme in scope:
            pylox.error(name, "Already variable with this name in this scope.")
            self.localHadError = True
            return 
        scope[name.lexeme] = False

    def define(self, name: Token):
        if self.scopes.isEmpty():
            return 
        self.scopes.peek()[name.lexeme] =  True

    def resolveLocal(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self.scopes.stack)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return 