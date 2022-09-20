from Expr import ExprVisitor, Expr, Binary, Grouping, Unary, Literal, Variable, Assign, Logical, Call
from Token import TokenType 
from Stmt import StmtVisitor, Stmt, Expression, Print,  Var, Block, If, While, StopIter, Function
import LoxCallable
from Environment import Environment
import pylox



# helper 
# everything apart from nil (None under the hood) and false is evaluated to true
def isTruthy(obj):
    if obj == None:
        return False
    if isinstance(obj, bool):
        return bool(obj)
    return True

def checkNumberOperand(operator, operand):
    if isinstance(operand, float):
        return True
    raise pylox.LoxRuntimeError(operator, "Operand must be a number")

def checkNumberOperands(operator, left, right):
    if isinstance(left, float) and isinstance(right, float):
        return True
    raise pylox.LoxRuntimeError(operator, "Operands must be numbers")

def stringify(s) -> str:
    if s is None:
        return "nil"
    elif isinstance(s, float):
        txt = str(s)
        if txt.endswith(".0"):
            return txt[0:-2:]
        return txt

    return str(s)

class Interpreter(ExprVisitor, StmtVisitor):    

    def __init__(self) -> None:
        self.globals = Environment()
        self.environment = self.globals
        # or 
        # self.environment = Environment(self.globals)

        self.globals.define("clock", LoxCallable.clock())

    def interpret(self, statements: 'list[Stmt]'):
        try:
            for statement in statements:
                self.execute(statement)
        except pylox.LoxRuntimeError as error:
            pylox.runtimeError(error)
            return None

# ----------- visiting statemenst -------------
    # statments dont have a return value since they dont evaluate to a value

    def visitBlockStmt(self, stmt: Block):
        self.executeBlock(stmt.statements, Environment(self.environment))

    def visitVarStmt(self, stmt: Var):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visitExpressionStmt(self, stmt: Expression):
        self.evaluate(stmt.expression)

    def visitIfStmt(self, stmt: If):
        if isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)

    def visitWhileStmt(self, stmt: While):
        while isTruthy(self.evaluate( stmt.condition )):
            try:
                self.execute(stmt.body)
            except pylox.LoxBreakIter:
                break
            except pylox.LoxContinueIter:
                continue

    def visitStopiterStmt(self, stmt: StopIter):
        if stmt.name.type == TokenType.BREAK:
            raise pylox.LoxBreakIter(stmt.name, "Invalid: 'break' statement outside of loop")
        # else
        raise pylox.LoxContinueIter(stmt.name, "Invalid: 'continue' statement outside of loop")

    def visitPrintStmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    def visitFunctionStmt(self, stmt: Function):
        function: LoxCallable.LoxFunction = LoxCallable.LoxFunction(stmt)
        self.environment.define(stmt.name.lexeme, function)
        return None

# ----------- visiting expressions ------------

    def visitAssignExpr(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visitVariableExpr(self, expr: Variable):
        return self.environment.get(expr.name)

    def visitLiteralExpr(self, expr: Literal):
        return expr.value

    def visitLogicalExpr(self, expr: Logical):
        left = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if isTruthy(left):
                return left 
        elif not isTruthy(left):
            return left 

        return self.evaluate(expr.right)

    def visitGroupingExpr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr: Unary):
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            checkNumberOperand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not isTruthy(right)
        #else
        return None

    def visitBinaryExpr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            checkNumberOperands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.STAR:
            checkNumberOperands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == TokenType.SLASH:
            checkNumberOperands(expr.operator, left, right)
            return float(left) / float(right)
        
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(right, float) and isinstance(left, float):
                return float(left) + float(right)
            # no implicit conversions here
            elif isinstance(right, str) and isinstance(left, str):
                # same syntax in python xd
                return str(left) + str(right)
            
            raise pylox.LoxRuntimeError(expr.operator, "Operands must be two number or two strings")
        
        elif expr.operator.type == TokenType.GREATER:
            checkNumberOperands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            checkNumberOperands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            checkNumberOperands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            checkNumberOperands(expr.operator, left, right)
            return float(left) <= float(right)
        
        # python's "==" behaves exacly like == in lox :)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not (right == left)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return right == left
        #else - unreachable
        return None

    def visitCallExpr(self, expr: Call):
        callee = self.evaluate( expr.callee )

        arguments: 'list[Expr]' = []
        for arg in expr.arguments:
            arguments.append( self.evaluate(arg))
        
        if not isinstance(callee, LoxCallable.LoxCallable):
            raise pylox.LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        function: LoxCallable.LoxCallable = callee
        if len(arguments) != function.arity():
            raise pylox.runtimeError(expr.paren, f"Exprcted {function.arity()} arguments but got {arguments.size()}.")

        return function.call(self, arguments)

# -------------- helpers, executors and evaluators ----

    def executeBlock(self, statements: 'list[Stmt]', environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        
        finally:
            self.environment = previous
    
    # evaluate for Stmts
    def execute(self, stms: Stmt):
        return stms.accept(self)

    def evaluate(self, expr: Expr):
        return expr.accept(self)