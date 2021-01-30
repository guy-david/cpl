class Token:
    # Keywords
    BREAK = 1
    CASE = 2
    DEFAULT = 3
    ELSE = 4
    FLOAT = 5
    IF = 6
    INPUT = 7
    INT = 8
    OUTPUT = 9
    STATIC_CAST = 10
    SWITCH = 11
    WHILE = 12

    # Symbols
    LPAREN = 13
    RPAREN = 14
    LBRACE = 15
    RBRACE = 16
    COMMA = 17
    SEMICOLON = 18
    COLON = 19

    # Operators
    ASSIGN = 20
    EQUAL = 21
    NEQUAL = 22
    LESS = 23
    GREATER = 24
    EQLESS = 25
    EQGREATER = 26
    PLUS = 27
    MINUS = 28
    MULTIPLY = 29
    DIVIDE = 30
    OR = 31
    AND = 32
    NOT = 33
    COMMENT = 34

    # Factors
    IDENTIFIER = 35
    NUMBER = 36

    KIND_TO_STR = {}

    def __init__(self, kind, file_path, line, column, data=None):
        self.kind = kind
        self.file_path = file_path
        self.line = line
        self.column = column
        self.data = data

    def __str__(self):
        strs = [self.kind_to_str(self.kind)]
        if self.data is not None:
            strs.append(str(self.data))
        return '\t'.join(strs)

    @staticmethod
    def kind_to_str(kind):
        return Token.KIND_TO_STR[kind]


ALL_ATTRS = {attr: getattr(Token, attr) for attr in dir(Token)}
Token.KIND_TO_STR = {value: attr for attr, value in ALL_ATTRS.items()
                     if isinstance(value, int) and not attr.startswith('__')}
