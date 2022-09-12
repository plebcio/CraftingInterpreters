from Token import Token, TokenType
import pylox


keywords = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}


class Scanner:
    def __init__(self, source) -> None:
        self.source = source
        self.source_len = len(source)
        self.tokens:'list[Token]' = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scanTokens(self):
        while (not self.isAtEnd()):
            self.start = self.current
            self.scanToken()

        # add an EOF token
        self.tokens.append(Token(TokenType.EOF,"", None, self.line))
        return self.tokens

    def isAtEnd(self):
        return self.current >= self.source_len

    def scanToken(self):
        c = self.advance()
        if c == '(':
            self.addToken(TokenType.LEFT_PAREN)
        elif c == ')':
            self.addToken(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.addToken(TokenType.LEFT_BRACE)
        elif c == '}':
            self.addToken(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.addToken(TokenType.COMMA)
        elif c == '.':
            self.addToken(TokenType.DOT)
        elif c == '-':
            self.addToken(TokenType.MINUS)
        elif c == '+':
            self.addToken(TokenType.PLUS)
        elif c == ';':
            self.addToken(TokenType.SEMICOLON)
        elif c == '*':
            self.addToken(TokenType.STAR)

        elif c == '!':
            self.addToken(TokenType.BANG_EQUAL if self.match("=")
                else TokenType.BANG)
        elif c == '=':
            self.addToken(TokenType.EQUAL_EQUAL if self.match("=")
                else TokenType.EQUAL)
        elif c == '<':
            self.addToken(TokenType.LESS_EQUAL if self.match("=")
                else TokenType.LESS)
        elif c == '>':
            self.addToken(TokenType.GREATER_EQUAL if self.match("=")
                else TokenType.GREATER)
        
        elif c == "/":
            if self.match("/"):
                while (self.peek() != '\n'):
                    self.advance()
            # handle /* ... */ comments
            elif self.match("*"):
                while self.peek() != '*' or self.peekNext() != '/':
                    if self.peek() == '\n':
                        self.line += 1
                    self.advance()
                # eat the  */
                self.advance()
                self.advance() 

            else:
                self.addToken(TokenType.SLASH)

        elif c in " \r\t":
            # ignore whitespace
            pass
        elif c == '\n':
            self.line += 1
        
        # handle strings
        elif c == '"':
            self.string()

        else:
            if self.isDigit(c):
                self.number()
            elif self.isAlpha(c):
                self.identifier()
            else:       
                pylox.error(self.line, "Unexpected character.")            

    def identifier(self):
        while(self.isAlphaNumeric(self.peek())):
            self.advance()
        
        text = self.source[self.start: self.current:]
        # default value is user defined identifier
        type: TokenType = keywords.get(text, TokenType.IDENTIFIER) 
        self.addToken(type)
        


    def number(self):
        while(self.isDigit(self.peek())):
            self.advance()
        # look at fraction
        if self.peek() == "." and self.isDigit(self.peekNext()):
            # eat the "."
            self.advance()
            # eat following digits
            while(self.isDigit(self.peek())):
                self.advance()
        
        self.addToken(TokenType.NUMBER, float(self.source[ self.start:self.current: ]))

    def isAlpha(self, c):
        return (ord(c) >= ord("a") and ord(c) <= ord("z")) or\
            (ord(c) >= ord("A") and ord(c) <= ord("Z")) or\
            c == "_"

    def isAlphaNumeric(self, c):
        return self.isAlpha(c) or self.isDigit(c)

    def isDigit(self, c):
        return ord(c) >= ord("0") and ord(c) <= ord("9")

    def peekNext(self):
        if self.current + 1 >=self.source_len:
            return "\0"
        return self.source[self.current+1]

    def string(self):
        while (self.peek() != '"' and not self.isAtEnd()):
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if (self.isAtEnd()):
            pylox.error(self.line, "Unterminated string")
            return

        # eat the closing " 
        self.advance()
        # trim the "   "  off
        str_val = self.source[self.start + 1:self.current -1:]
        self.addToken(TokenType.STRING, str_val)


    def advance(self) -> chr:
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected):
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> chr:
        if self.isAtEnd():
            return '\0'
        return self.source[self.current]


    def addToken(self, type: TokenType, literal = None):
        text = self.source[self.start:self.current:]
        self.tokens.append(Token(type, text, literal, self.line))

        




