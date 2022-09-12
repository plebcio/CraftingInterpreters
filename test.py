from abc import ABC, abstractmethod
from Token import Token

class Expr(ABC):
    def __init__(self) -> None:
        super().__init__()
        pass

class Binary(Expr):
    def __init__(self, left:Expr, operator: Token, right: Expr) -> None:
        super().__init__()    
        self.left = left
        self.operator = operator
        self.right = right