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

    def __str__(self):
        return str(self.variable)

class Immediate(Value):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Operator(Value):
    def __init__(self, *args):
        self.operands = list(args)

class UnaryOperator(Operator):
    pass

class UnaryOperator(Operator):
    def __init__(self, a):
        super().__init__(a)

class StaticCast(UnaryOperator):
    def __init__(self, a, dest_type):
        super().__init__(a)
        self.dest_type = dest_type

class UnaryAdd(UnaryOperator):
    pass

class Negate(UnaryOperator):
    pass

class Not(UnaryOperator):
    pass

class BinaryOperator(Operator):
    def __init__(self, a, b):
        super().__init__(a, b)

class Assign(BinaryOperator):
    pass

class Add(BinaryOperator):
    pass

class Sub(BinaryOperator):
    pass

class Mul(BinaryOperator):
    pass

class Div(BinaryOperator):
    pass

class Or(BinaryOperator):
    pass

class And(BinaryOperator):
    pass

class Compare(BinaryOperator):
    pass

class Equal(Compare):
    pass

class NotEqual(Compare):
    pass

class Less(Compare):
    pass

class Greater(Compare):
    pass

class LessOrEqual(Compare):
    pass

class GreaterOrEqual(Compare):
    pass
