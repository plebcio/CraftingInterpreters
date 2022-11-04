from abc import ABC
from Token import Token
from Expr import Expr

class Stmt (ABC):
    def __init__(self) -> None:
       super().__init__()
       pass
    def accept(self, visitor: any):
        pass
    def __eq__(self, __o: object) -> bool:
        return self is __o
    def __hash__(self):
        return hash(id(self))




class Block(Stmt):
    def __init__(self, statements:'list[Stmt]', ):
        super().__init__()
        self.statements = statements
    def accept(self, visitor: any):
        return visitor.visitBlockStmt(self)

class Class(Stmt):
    def __init__(self, name:Token, superclass:'Expr.Variable', methods:'list[Function]', ):
        super().__init__()
        self.name = name
        self.superclass = superclass
        self.methods = methods
    def accept(self, visitor: any):
        return visitor.visitClassStmt(self)

class Expression(Stmt):
    def __init__(self, expression:Expr, ):
        super().__init__()
        self.expression = expression
    def accept(self, visitor: any):
        return visitor.visitExpressionStmt(self)

class Function(Stmt):
    def __init__(self, name:Token, params:'list[Token]', body:list[Stmt], ):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
    def accept(self, visitor: any):
        return visitor.visitFunctionStmt(self)

class If(Stmt):
    def __init__(self, condition:Expr, thenBranch:Stmt, elseBranch:Stmt, ):
        super().__init__()
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch
    def accept(self, visitor: any):
        return visitor.visitIfStmt(self)

class Return(Stmt):
    def __init__(self, keyword:Token, value:Expr, ):
        super().__init__()
        self.keyword = keyword
        self.value = value
    def accept(self, visitor: any):
        return visitor.visitReturnStmt(self)

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

class While(Stmt):
    def __init__(self, condition:Expr, body:Stmt, ):
        super().__init__()
        self.condition = condition
        self.body = body
    def accept(self, visitor: any):
        return visitor.visitWhileStmt(self)

class StopIter(Stmt):
    def __init__(self, name:Token, ):
        super().__init__()
        self.name = name
    def accept(self, visitor: any):
        return visitor.visitStopiterStmt(self)

class StmtVisitor:
    def __str__(self):
        return self.__class__.__name__
    def visitBlockStmt(self, stmt:Block):
        pass
    def visitClassStmt(self, stmt:Class):
        pass
    def visitExpressionStmt(self, stmt:Expression):
        pass
    def visitFunctionStmt(self, stmt:Function):
        pass
    def visitIfStmt(self, stmt:If):
        pass
    def visitReturnStmt(self, stmt:Return):
        pass
    def visitPrintStmt(self, stmt:Print):
        pass
    def visitVarStmt(self, stmt:Var):
        pass
    def visitWhileStmt(self, stmt:While):
        pass
    def visitStopiterStmt(self, stmt:StopIter):
        pass
