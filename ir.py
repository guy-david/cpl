class Type:
    pass

class Integer(Type):
    def __str__(self):
        return 'int'

class Float(Type):
    def __str__(self):
        return 'float'

class Variable:
    def __init__(self, name, type_class):
        self.name = name
        self.type_class = type_class

    def __str__(self):
        return f'<{self.name}:{self.type_class}>'

class Statement:
    pass

class Break(Statement):
    pass

class While(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Case:
    def __init__(self, const_expr, stmts):
        self.const_expr = const_expr
        self.stmts = stmts

class Switch(Statement):
    def __init__(self, expr, cases, default_case=None):
        self.condition = condition
        self.cases = cases
        self.default_case = default_case

class Cond(Statement):
    def __init__(self, condition, true_case, false_case=None):
        self.condition = condition
        self.true_case = true_case
        self.false_case = false_case

class Input(Statement):
    def __init__(self, ident):
        self.ident = ident

class Output(Statement):
    def __init__(self, expr):
        self.expr = expr

class Value:
    pass

class Use(Value):
    def __init__(self, variable):
        self.variable = variable

    def get_type(self):
        return self.variable.type_class

    def __str__(self):
        return str(self.variable)

class Immediate(Value):
    def __init__(self, value):
        self.value = value

    def get_type(self):
        if type(self.value) is int:
            return Integer
        if type(self.value) is float:
            return Float
        assert False, 'INTERNAL ERROR'

    def __str__(self):
        return str(self.value)

class Operator(Value):
    def __init__(self, *args):
        self.operands = list(args)

    def get_type(self):
        t = self.operands[0].get_type()
        for op in self.operands[1:]:
            assert t == op.get_type()
        return t

class UnaryOperator(Operator):
    pass

class UnaryOperator(Operator):
    def __init__(self, a):
        super().__init__(a)

class StaticCast(UnaryOperator):
    def __init__(self, a, dest_type):
        super().__init__(a)
        self.dest_type = dest_type

    def get_type(self):
        return self.dest_type

class UnaryAdd(UnaryOperator):
    @staticmethod
    def compute(a):
        return a

class Negate(UnaryOperator):
    @staticmethod
    def compute(a):
        return -a

class Not(UnaryOperator):
    @staticmethod
    def compute(a):
        return not a

    def get_type(self):
        return Integer

class BinaryOperator(Operator):
    def __init__(self, a, b):
        super().__init__(a, b)

class Assign(BinaryOperator):
    pass

class Add(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a + b

class Sub(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a - b

class Mul(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a * b

class Div(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a / b

class Or(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a or b

    def get_type(self):
        return Integer

class And(BinaryOperator):
    @staticmethod
    def compute(a, b):
        return a and b

    def get_type(self):
        return Integer

class Compare(BinaryOperator):
    def get_type(self):
        return Integer

class Equal(Compare):
    @staticmethod
    def compute(a, b):
        return a == b

class NotEqual(Compare):
    @staticmethod
    def compute(a, b):
        return a != b

class Less(Compare):
    @staticmethod
    def compute(a, b):
        return a < b

class Greater(Compare):
    @staticmethod
    def compute(a, b):
        return a > b

class LessOrEqual(Compare):
    @staticmethod
    def compute(a, b):
        return a <= b

class GreaterOrEqual(Compare):
    @staticmethod
    def compute(a, b):
        return a >= b
