""" helper file for generating classes for ast """


expr_strs = ["Binary : Expr left, Token operator, Expr right", "Grouping : Expr expression", "Literal : any value",
            "Unary: Token operator, Expr right"]

stmt_strs = ["Expression : Expr expression", "Print : Expr expression"]

l = [expr_strs, stmt_strs]

base_class_name = input("Base class name: ")

a = input("expr:0, stms:1\n : ")

in_strs = l[int(a)]


with open(base_class_name+".py", "w") as f:
    f.writelines([
        # import 
        "from abc import ABC\n",
        "from Token import Token\n",
        "\n"
        # ABC        
        f"class {base_class_name} (ABC):\n",    
        "    def __init__(self) -> None:\n"
        "       super().__init__()\n",
        "       pass\n"
        "    def accept(self, visitor: any):\n",
        "        pass"
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
        f.write(f"    def visit{class_name.capitalize()}{base_class_name.capitalize()}(self, expr:{class_name}):\n")
        f.write("        pass\n")