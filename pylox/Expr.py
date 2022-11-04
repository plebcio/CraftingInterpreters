from abc import ABC
from Token import Token


class Expr (ABC):
    def __init__(self) -> None:
       super().__init__()
       pass
    def accept(self, visitor: any):
        pass
    def __eq__(self, __o: object) -> bool:
        return self is __o
    def __hash__(self):
        return hash(id(self))




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

class Call(Expr):
    def __init__(self, callee:Expr, paren:Token, arguments:'list[Expr]', ):
        super().__init__()
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    def accept(self, visitor: any):
        return visitor.visitCallExpr(self)

class Get(Expr):
    def __init__(self, object:Expr, name:Token, ):
        super().__init__()
        self.object = object
        self.name = name
    def accept(self, visitor: any):
        return visitor.visitGetExpr(self)

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

class Logical(Expr):
    def __init__(self, left:Expr, operator:Token, right:Expr, ):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor: any):
        return visitor.visitLogicalExpr(self)

class Set(Expr):
    def __init__(self, obj:Expr, name:Token, value:Expr, ):
        super().__init__()
        self.obj = obj
        self.name = name
        self.value = value
    def accept(self, visitor: any):
        return visitor.visitSetExpr(self)

class Super(Expr):
    def __init__(self, keyword:Token, method:Token, ):
        super().__init__()
        self.keyword = keyword
        self.method = method
    def accept(self, visitor: any):
        return visitor.visitSuperExpr(self)

class This(Expr):
    def __init__(self, keyword:Token, ):
        super().__init__()
        self.keyword = keyword
    def accept(self, visitor: any):
        return visitor.visitThisExpr(self)

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

class Lambda(Expr):
    def __init__(self, params:'list[Token]', body:any, ):
        super().__init__()
        self.params = params
        self.body = body
    def accept(self, visitor: any):
        return visitor.visitLambdaExpr(self)

class ExprVisitor:
    def __str__(self):
        return self.__class__.__name__
    def visitAssignExpr(self, expr:Assign):
        pass
    def visitBinaryExpr(self, expr:Binary):
        pass
    def visitCallExpr(self, expr:Call):
        pass
    def visitGetExpr(self, expr:Get):
        pass
    def visitGroupingExpr(self, expr:Grouping):
        pass
    def visitLiteralExpr(self, expr:Literal):
        pass
    def visitLogicalExpr(self, expr:Logical):
        pass
    def visitSetExpr(self, expr:Set):
        pass
    def visitSuperExpr(self, expr:Super):
        pass
    def visitThisExpr(self, expr:This):
        pass
    def visitUnaryExpr(self, expr:Unary):
        pass
    def visitVariableExpr(self, expr:Variable):
        pass
    def visitLambdaExpr(self, expr:Lambda):
        pass
