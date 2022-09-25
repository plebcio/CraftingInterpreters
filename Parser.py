from Token import Token, TokenType
from Expr import Expr, Binary, Grouping, Unary, Literal, Token, Variable, Assign, Logical, Call, Lambda
from Stmt import Stmt, Expression, Print, Var, Block, If, While, StopIter, Function, Return
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
            if self.match([TokenType.FUN]):
                return self.function("function")
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
        
        if (self.match([TokenType.FOR])):
            return self.forStatement()

        if (self.match([TokenType.IF])):
            return self.ifStatement()

        if self.match([TokenType.WHILE]):
            return self.whileStatement()

        if (self.match([TokenType.PRINT])):
            return self.printStatement()

        if self.match([TokenType.LEFT_BRACE]):
            return Block(self.block())

        # no argument keyword statements go here
        if self.match([TokenType.BREAK]):
            tok = self.previous()
            self.consume(TokenType.SEMICOLON, "Expected ';' after break")
            return StopIter(tok)

        if self.match([TokenType.CONTINUE]):
            tok = self.previous()
            self.consume(TokenType.SEMICOLON, "Expected ';' after continue")
            return StopIter(tok)

        if self.match([TokenType.RETURN]):
                return self.returnStatement()

        return self.expressionStatement()   


    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        
        initializer: Stmt
        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition: Expr = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for condition.")

        increment: Expr = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        body: Stmt = self.statement()

        if increment != None: 
            body = Block([
              body, 
              Expression( increment )  
            ])
        
        if condition == None:
            condition = Literal(True)
        body = While(condition, body)
        
        if initializer != None:
            body = Block([initializer, body])

        return body

    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        thenBranch: Stmt = self.statement()
        elseBranch: Stmt = None
        if self.match([TokenType.ELSE]):
            elseBranch = self.statement()
    
        return If(condition, thenBranch, elseBranch)

    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition.")
        body: Stmt = self.statement()

        return While(condition, body)

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

    def function(self, kind:str):
        if self.peek().type == TokenType.LEFT_PAREN:
            expression =  Expression(self.lambdaExpression())
            self.consume(TokenType.SEMICOLON, "Expected ';' after lambda function")
            return expression
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name")
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            # like a "do while" loop
            parameters.append( self.consume(TokenType.IDENTIFIER, "Expected parameter name"))
            while self.match([TokenType.COMMA]):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters")
                parameters.append( self.consume(TokenType.IDENTIFIER, "Expected parameter name"))
        
        self.consume(TokenType.RIGHT_PAREN, f"Expected ')' after {kind} name.")

        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body")
        body: 'list[Stmt]' = self.block()
        return Function(name, parameters, body)

    def block(self):
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            stmts.append( self.declaration() )
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return stmts
        
    def returnStatement(self):
        keyword: Token = self.previous()
        value: Expr = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return value")
        return Return(keyword, value)


# ------- handling expression productions top down --------------------

    def expression(self):
        return self.assignment()
    
    def assignment(self):
        expr: Expr = self.logic_or()

        if self.match([TokenType.EQUAL]):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logic_or(self):
        expr: Expr = self.logic_and()

        while (self.match([TokenType.OR])):
            operator: Token = self.previous()
            right : expr = self.logic_and()
            expr = Logical(expr, operator, right)

        return expr

    def logic_and(self):
        expr: Expr = self.equality()

        while (self.match([TokenType.AND])):
            operator: Token = self.previous()
            right : expr = self.equality()
            expr = Logical(expr, operator, right)

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
    
        return self.call()

    def call(self):
        expr: Expr = self.primary()
        while True: 
            if self.match([TokenType.LEFT_PAREN]):
                expr = self.finishCall(expr)
            else:
                break

        return expr
    
    def finishCall(self, callee: Expr):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append( self.expression() )
            while(self.match([TokenType.COMMA])):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments")
                arguments.append( self.expression() )
        
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")

        return Call(callee, paren, arguments)


    def primary(self):        
        if self.match([TokenType.FALSE]):
            return Literal(False)
        if self.match([TokenType.TRUE]):
            return Literal(True)
        if self.match([TokenType.NIL]):
            return Literal(None)

        if self.match([TokenType.FUN]):
            # matched a lambda expression
            return self.lambdaExpression()

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

    def lambdaExpression(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after start of lambda function expression")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            # like a "do while" loop
            parameters.append( self.consume(TokenType.IDENTIFIER, "Expected parameter name"))
            while self.match([TokenType.COMMA]):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters")
                parameters.append( self.consume(TokenType.IDENTIFIER, "Expected parameter name"))
        
        self.consume(TokenType.RIGHT_PAREN, f"Expected ')' after lambda fn parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before lambda fuction body")
        body: 'list[Stmt]' = self.block()
        return Lambda(parameters, body)

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