from Token import Token, TokenType
import pylox

class Environment():
    def __init__(self, enclosing = None) -> None:
        self.values:dict = {}
        self.enclosing = enclosing

    def define(self, name: str, value):
        self.values[name] = value

    def get(self, name:Token):
        if name.lexeme in self.values:
            return self.values.get(name.lexeme)
        
        if self.enclosing != None:
            return self.enclosing.get(name)
        
        raise pylox.LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def getAt(self, distance, name):
        return self.ancestor(distance).values.get(name)

    def ancestor(self, distance):
        enviorment = self
        for _ in range(distance):
            enviorment = enviorment.enclosing
        return enviorment

    def assign(self, name:Token, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing != None:
            self.enclosing.assign(name, value)
            return

        raise pylox.LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assignAt(self, distance, name:Token, value):
        self.ancestor(distance).values[name.lexeme] = value