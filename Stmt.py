from abc import ABC
from Token import Token
from Expr import Expr

class Stmt (ABC):
    def __init__(self) -> None:
       super().__init__()
       pass
    def accept(self, visitor: any):
        pass

class Block(Stmt):
    def __init__(self, statements:'list[Stmt]', ):
        super().__init__()
        self.statements = statements
    def accept(self, visitor: any):
        return visitor.visitBlockStmt(self)

class Expression(Stmt):
    def __init__(self, expression:Expr, ):
        super().__init__()
        self.expression = expression
    def accept(self, visitor: any):
        return visitor.visitExpressionStmt(self)

class Print(Stmt):
    def __init__(self, expression:Expr, ):
        super().__init__()
        self.expression = expression
    def accept(self, visitor: any):
        return visitor.visitPrintStmt(self)

class Var(Stmt):
    def __init__(self, name:Token, initializer:Expr, ):
        super().__init__()
        self.name = name
        self.initializer = initializer
    def accept(self, visitor: any):
        return visitor.visitVarStmt(self)

class StmtVisitor:
    def __str__(self):
        return self.__class__.__name__
    def visitBlockStmt(self, stmt:Block):
        pass
    def visitExpressionStmt(self, stmt:Expression):
        pass
    def visitPrintStmt(self, stmt:Print):
        pass
    def visitVarStmt(self, stmt:Var):
        pass
