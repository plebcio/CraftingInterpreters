from Token import Token, TokenType
from Expr import Expr, Binary, Grouping, Unary, Literal, Token, Variable, Assign
from Stmt import Stmt, Expression, Print, Var, Block
import pylox
from Flags import Flags

myFlgas = Flags()

# implementing the recursive decent parser

class ParseError(RuntimeError):
    pass

class Parser:
    def __init__(self, tokens: 'list[Token]', inREPLmode = False) -> None:
        self.tokens = tokens
        self.current: int = 0
        self.inREPLmode = inREPLmode


    def parse(self):
        self.statements = []
        while not self.isAtEnd():
            try:
                self.statements.append( self.declaration() )
            except ParseError:
                return None

        if myFlgas.hadError:
            return None
        return self.statements

# ------- handling statement productions ----------

    def declaration(self):
        try:
            if self.match([TokenType.VAR]):
                return self.varDeclaration()
            return self.statement()
        except ParseError as err:
            self.synchronize()
            return None

    def varDeclaration(self):
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected variable name.")

        initializer: Expr = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)

    def statement(self):
        if (self.match([TokenType.PRINT])):
            return self.printStatement()

        if self.match([TokenType.LEFT_BRACE]):
            return Block(self.block())

        return self.expressionStatement()   
    
    def printStatement(self):
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expected ";" after value')
        return Print(value)

    def expressionStatement(self):
        expr: Expr = self.expression()
        # fixing repl mode to work with single expression input
        if self.inREPLmode:
            if self.peek().type == TokenType.EOF:
                self.advance()
                return Print(expr)
                
        # if REPL specific behaior does not occur, behave nomally         
        self.consume(TokenType.SEMICOLON, 'Expected ";" after expression')

        return Expression(expr)

    def block(self):
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            stmts.append( self.declaration() )
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return stmts
        
# ------- handling expression productions top down --------------------

    def expression(self):
        return self.assignment()
    
    def assignment(self):
        expr: Expr = self.equality()

        if self.match([TokenType.EQUAL]):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

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

        if self.match([TokenType.IDENTIFIER]):
            return Variable(self.previous())

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
        myFlgas.hadError = True # not the greatest solution but was done with python scoping 
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