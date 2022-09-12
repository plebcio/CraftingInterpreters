from abc import ABC
from Token import Token
from Expr import Expr

class Stmt (ABC):
    def __init__(self) -> None:
       super().__init__()
       pass
    def accept(self, visitor: any):
        pass


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

class StmtVisitor:
    def __str__(self):
        return self.__class__.__name__
    def visitExpressionStmt(self, expr:Expression):
        pass
    def visitPrintStmt(self, expr:Print):
        pass
