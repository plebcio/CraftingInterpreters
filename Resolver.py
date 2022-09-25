from enum import Enum
from Expr import ExprVisitor, Expr, Binary, Grouping, Unary, Literal, Variable, Assign, Logical, Call, Lambda
from Token import Token 
from Stmt import StmtVisitor, Stmt, Expression, Print,  Var, Block, If, While, StopIter, Function, Return
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
    FUNCTION = 1

# acual Resolver class

class Resolver(StmtVisitor, ExprVisitor):
    def __init__(self, interpreter: 'Interpreter.Interpreter') -> None:
        self.interpreter = interpreter
        self.scopes = Stack()
        self.currentFunction: FunctionType = FunctionType.NONE
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
        
        if stmt.value != None:
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

    def visitGroupingExpr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visitLiteralExpr(self, expr: Literal):
        return

    def visitLogicalExpr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visitUnaryExpr(self, expr: Unary):
        self.resolve(expr.right)

    # custom   
    def visitLambdaExpr(self, expr: Lambda):
        for param in expr.params:
            self.resolve(param)
        self.resolve(expr.body)   
        

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