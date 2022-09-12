from Expr import Expr, Binary, Grouping, Unary, Literal, Token, Visitor
from Token import TokenType 

class AstPrinter(Visitor):
    def print_out(self, expr: Expr):
        return expr.accept(self)

    def visitBinaryExpr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return self.parenthesize("group", [expr.expression])

    def visitLiteralExpr(self, expr: Literal) -> str:
        if (expr.value == None):
            return "nil"
        return str(expr.value) # FIXME ???

    def visitUnaryExpr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right]) 


    def parenthesize(self, name, arg_list: 'list[Expr]'):
        
        out_list = ["(", name]
        for expr in arg_list:
            out_list.append(" ")
            out_list.append(expr.accept(self))
        
        out_list.append(")")
        return "".join(out_list)


def main():
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal(45.67)
        )
    )
    
    prit = AstPrinter()
    print(prit.print_out(expression))

#main()