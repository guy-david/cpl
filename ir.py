class Type:
    pass

class Integer(Type):
    pass

class Float(Type):
    pass

class Statement:
    pass

class While(Statement):
    pass

class Switch(Statement):
    pass

class Cond(Statement):
    pass

class Input(Statement):
    pass

class Output(Statement):
    pass

class Value:
    pass

class Parameter(Value):
    def __init__(self, name):
        self.name = name

class Immediate(Value):
    def __init__(self, value):
        self.value = value

class Operator(Value):
    def __init__(self, *args):
        operands = list(args)

class UnaryOperator(Operator):
    pass

class UnaryOperator(Operator):
    def __init__(self, a):
        super().__init__(a)

class StaticCast(UnaryOperator):
    def __init__(self, a, dest_type):
        super().__init__(a)
        self.dest_type = dest_type

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

class Equal(BinaryOperator):
    pass

class NotEqual(BinaryOperator):
    pass

class Less(BinaryOperator):
    pass

class Greater(BinaryOperator):
    pass

class LessOrEqual(BinaryOperator):
    pass

class GreaterOrEqual(BinaryOperator):
    pass
