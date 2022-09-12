from Expr import ExprVisitor, Expr, Binary, Grouping, Unary, Literal, Token, Variable, Assign
from Token import TokenType 
from Stmt import StmtVisitor, Stmt, Expression, Print,  Var, Block
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
        self.environment = Environment()

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

    def visitPrintStmt(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        print(stringify(value))


# ----------- visiting expressions ------------

    def visitAssignExpr(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visitVariableExpr(self, expr: Variable):
        return self.environment.get(expr.name)

    def visitLiteralExpr(self, expr: Literal):
        return expr.value

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