from abc import ABC
from Token import Token

class Expr (ABC):
    def __init__(self) -> None:
       super().__init__()
       pass
    def accept(self, visitor: any):
        pass


class Assign(Expr):
    def __init__(self, name:Token, value:Expr, ):
        super().__init__()
        self.name = name
        self.value = value
    def accept(self, visitor: any):
        return visitor.visitAssignExpr(self)

class Binary(Expr):
    def __init__(self, left:Expr, operator:Token, right:Expr, ):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor: any):
        return visitor.visitBinaryExpr(self)

class Grouping(Expr):
    def __init__(self, expression:Expr, ):
        super().__init__()
        self.expression = expression
    def accept(self, visitor: any):
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __init__(self, value:any, ):
        super().__init__()
        self.value = value
    def accept(self, visitor: any):
        return visitor.visitLiteralExpr(self)

class Unary(Expr):
    def __init__(self, operator:Token, right:Expr, ):
        super().__init__()
        self.operator = operator
        self.right = right
    def accept(self, visitor: any):
        return visitor.visitUnaryExpr(self)

class Variable(Expr):
    def __init__(self, name:Token, ):
        super().__init__()
        self.name = name
    def accept(self, visitor: any):
        return visitor.visitVariableExpr(self)

class ExprVisitor:
    def __str__(self):
        return self.__class__.__name__
    def visitAssignExpr(self, expr:Assign):
        pass
    def visitBinaryExpr(self, expr:Binary):
        pass
    def visitGroupingExpr(self, expr:Grouping):
        pass
    def visitLiteralExpr(self, expr:Literal):
        pass
    def visitUnaryExpr(self, expr:Unary):
        pass
    def visitVariableExpr(self, expr:Variable):
        pass
