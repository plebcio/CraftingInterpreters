from Token import Token, TokenType
from Expr import Expr, Binary, Grouping, Unary, Literal, Token, Visitor
import pylox

# implementing the recursive decent parser

class ParseError(RuntimeError):
    pass

class Parser:
    def __init__(self, tokens: 'list[Token]') -> None:
        self.tokens = tokens
        self.current: int = 0


    def parse(self):
        try:
            out = self.expression()
            return out
        except ParseError:
            return None

# ------- handling productions top down --------------------

    def expression(self):
        return self.equality()
    
    def equality(self):
        expr: Expr = self.comparison()
        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr

    def comparison(self):
        expr: Expr = self.term()
        while self.match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr: Expr = self.factor()
        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
            
        return expr
 
    def factor(self):
        expr: Expr = self.unary()
        while self.match([TokenType.STAR, TokenType.SLASH]):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
    
        return expr
    
    def unary(self):
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator : Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
    
        return self.primary()

    def primary(self):        
        if self.match([TokenType.FALSE]):
            return Literal(False)
        if self.match([TokenType.TRUE]):
            return Literal(True)
        if self.match([TokenType.NIL]):
            return Literal(None)
        
        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.previous().literal)

        if self.match([TokenType.LEFT_PAREN]):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after expression')
            return Grouping(expr)

        # else - token cant start expression

        raise self.error(self.peek(), "Expected expression")


# --------------- error handling stuff (?) ---------

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)

    def error(self, token: Token, mess):
        pylox.error(token, mess)
        return ParseError() # FIXME dont know if it should be "return ParesError" or "return ParesError()"

    def synchronize(self):
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE,
                TokenType.PRINT, TokenType.RETURN ]:
                return
            
            self.advance()

# -------------- helpers ------------------------

    def match(self, types: 'list[Token]'):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        
        return False

    def check(self, type:TokenType):
        if self.isAtEnd():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.isAtEnd():
            self.current += 1
        return self.previous()
    
    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        return self.tokens[self.current]

    def isAtEnd(self):
        return self.peek().type == TokenType.EOF



        """
        
        production for comma ???

        expr -> equality ("," expr)+
        
        production for turnry operator ???

        ???

        error production for binary operator without left operand

        after unary 

        error_unary -> ("+"| "/"| "*"| "!="| ...) expr

        """