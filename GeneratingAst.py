""" helper file for generating classes for ast """


expr_strs = ["Assign : Token name, Expr value","Binary : Expr left, Token operator, Expr right", "Call : Expr callee, Token paren, 'list[Expr]' arguments", 
            "Grouping : Expr expression", "Literal : any value", "Logical : Expr left, Token operator, Expr right",
            "Unary: Token operator, Expr right", "Variable : Token name", "Lambda : 'list[Token]' params, any body"]

stmt_strs = ["Block : 'list[Stmt]' statements","Expression : Expr expression", "Function : Token name, 'list[Token]' params, list[Stmt] body",
            "If : Expr condition, Stmt thenBranch, Stmt elseBranch", "Return : Token keyword, Expr value", "Print : Expr expression", 
            "Var : Token name, Expr initializer", "While : Expr condition, Stmt body", "StopIter: Token name"]

l = [expr_strs, stmt_strs]

base_class_name = input("Base class name: ")

a = input("expr:0, stms:1\n : ")

in_strs = l[int(a)]


with open(base_class_name+".py", "w") as f:
    f.writelines([
        # import 
        "from abc import ABC\n",
        "from Token import Token\n",
        f"{'from Expr import Expr' if base_class_name == 'Stmt' else ''}",
        "\n\n",
        # ABC        
        f"class {base_class_name} (ABC):\n",    
        "    def __init__(self) -> None:\n"
        "       super().__init__()\n",
        "       pass\n"
        "    def accept(self, visitor: any):\n",
        "        pass\n",
        "    def __eq__(self, __o: object) -> bool:\n",
        "        return self is __o\n",
        "    def __hash__(self):\n",
        "        return hash(id(self))\n\n",
        "\n",
    ])

    for production in in_strs:
        l1 = production.split(":")
        class_name = l1[0].strip()
        f.write(f"\n\nclass {class_name}({base_class_name}):")

        children = l1[1].split(",")
        child_tups = [] # list of tuples (type, arg_name)
        for child in children:
            # creates a tuple from list
            child_tups.append( tuple(child.strip().split()) )

        f.write("\n    def __init__(self, ")
        for tok_type, tok in child_tups:
            f.write(f"{tok}:{tok_type}, ")
        f.write("):\n")

        f.write("        super().__init__()\n")
        for tok_type, tok in child_tups:
            f.write(f"        self.{tok} = {tok}\n")

        f.write("    def accept(self, visitor: any):\n")
        f.write(f"        return visitor.visit{class_name.capitalize()}{base_class_name.capitalize()}(self)") 
        
    f.writelines([
            f"\n\nclass {base_class_name.capitalize()}Visitor:\n",
            "    def __str__(self):\n",
            "        return self.__class__.__name__\n"
        ])
    
    for production in in_strs:
        l1 = production.split(":")
        class_name = l1[0].strip()
        f.write(f"    def visit{class_name.capitalize()}{base_class_name.capitalize()}(self, {base_class_name.lower()}:{class_name}):\n")
        f.write("        pass\n")