class Person:
    def sayname(self):
        print(self.name)
    def shout(self):
        print("hellllooooo")

Jane = Person()
Jane.name = "Janine"
method = Jane.shout
print(method)