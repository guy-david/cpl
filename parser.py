#!/usr/bin/env python3

import argparse

import utils
from lexer import Lexer
from tokens import Token
from ir import *


class Parser:

    class SyntaxError(Exception):
        pass

    class SemanticError(Exception):
        pass

    TYPES = {
        Token.INT: Integer,
        Token.FLOAT: Float,
    }

    def __init__(self, stream):
        self._lexer = Lexer(stream)
        self._last_accepted_token = None
        self._current_token = None
        self._breakable_scopes_depth = 0

    def parse(self):
        self._advance()
        return self._parse_program()

    def _parse_program(self):
        self.variables = self._parse_declarations()
        return self._parse_stmt_block()

    def _parse_declarations(self):
        variables = {}
        while True:
            idents = self._parse_id_list()
            if len(idents) == 0:
                return variables
            self._expect(Token.COLON)
            type_class = self._parse_type()
            self._expect(Token.SEMICOLON)
            for v in idents:
                if v in variables:
                    self.raise_error(self.SyntaxError, f'{v} is already declared')
                variables[v] = Variable(v, type_class)
        return variables

    def _parse_type(self):
        for token, type_class in self.TYPES.items():
            if self._accept(token):
                return type_class
        self._expected('Expected a type')

    def _parse_id_list(self):
        idents = []
        while True:
            variable = self._accept(Token.IDENTIFIER)
            if variable is None:
                return idents

            idents.append(variable.data)
            while self._accept(Token.COMMA):
                variable = self._expect(Token.IDENTIFIER)
                idents.append(variable.data)
        return idents

    def _parse_stmt_block(self):
        self._expect(Token.LBRACE)
        stmts = self._parse_stmt_list()
        self._expect(Token.RBRACE)
        return stmts

    def _parse_stmt_list(self):
        stmts = []
        while True:
            stmt = self._parse_stmt()
            if stmt is None:
                break
            stmts.append(stmt)
        return stmts

    def _parse_stmt(self):
        if self._accept(Token.IF):
            self._expect(Token.LPAREN)
            condition = self._parse_expr()
            self._expect(Token.RPAREN)
            true_case = self._parse_stmt()

            false_case = None
            if self._accept(Token.ELSE):
                false_case = self._parse_stmt()

            return Conditional(condition, true_case, false_case)

        elif self._accept(Token.INPUT):
            self._expect(Token.LPAREN)
            ident = self._expect(Token.IDENTIFIER)
            self._expect(Token.RPAREN)
            self._expect(Token.SEMICOLON)

            return Input(ident)

        elif self._accept(Token.OUTPUT):
            self._expect(Token.LPAREN)
            expr = self._parse_expr()
            self._expect(Token.RPAREN)
            self._expect(Token.SEMICOLON)

            return Output(expr)

        elif self._accept(Token.WHILE):
            self._expect(Token.LPAREN)
            condition = self._parse_expr()
            self._expect(Token.RPAREN)

            self._breakable_scopes_depth += 1
            body = self._parse_stmt()
            self._breakable_scopes_depth -= 1

            return While(condition, body)

        elif self._accept(Token.SWITCH):
            self._expect(Token.LPAREN)
            expr = self._parse_expr()
            self._expect(Token.RPAREN)

            self._expect(Token.LBRACE)

            cases = []
            has_default_case = False

            while self._accept(Token.CASE) or self._accept(Token.DEFAULT):
                parsing_case = self._last_accepted_token.kind == Token.CASE
                if parsing_case:
                    case_expr = self._parse_expr()
                    case_expr = Immediate(self.eval_const_expr(case_expr))
                elif not has_default_case:
                    case_expr = None
                    has_default_case = True
                else:
                    self.raise_error(self.SyntaxError, 'Only one default case is permitted')

                self._expect(Token.COLON)

                self._breakable_scopes_depth += 1
                case_body = self._parse_stmt_list()
                self._breakable_scopes_depth -= 1

                cases.append(Case(case_body, case_expr))

            self._expect(Token.RBRACE)

            return Switch(expr, cases)

        elif self._accept(Token.BREAK):
            if self._breakable_scopes_depth == 0:
                self.raise_error(self.SemanticError, 'break statement outside of while-loop or switch-case')
            self._expect(Token.SEMICOLON)

            return Break()

        elif self._accept(Token.LBRACE):
            stmts = self._parse_stmt_list()
            self._expect(Token.RBRACE)

            return stmts

        else:
            expr = self._try_parse_expr()
            if expr is None:
                return None
            self._expect(Token.SEMICOLON)

            return expr

    def _parse_expr(self, precedence=0):
        expr = self._try_parse_expr(precedence)
        if expr is None:
            self.raise_error(self.SyntaxError, 'Expected an expression')
        return expr

    def _try_parse_expr(self, precedence=0):
        right_associative_ops = [Assign]
        ops = [
            [(Token.ASSIGN, Assign)],
            [(Token.OR, Or), ],
            [(Token.AND, And), ],
            [(Token.EQUAL, Equal), (Token.NEQUAL, NotEqual), ],
            [(Token.LESS, Less), (Token.GREATER, Greater),
             (Token.EQLESS, LessOrEqual), (Token.EQGREATER, GreaterOrEqual), ],
            [(Token.PLUS, Add), (Token.MINUS, Sub), ],
            [(Token.MULTIPLY, Mul), (Token.DIVIDE, Div), ],

            [(Token.PLUS, UnaryAdd),
             (Token.MINUS, Negate),
             (Token.NOT, Not), ]
        ]

        if precedence >= len(ops):
            return self._try_parse_factor()

        for token, op in ops[precedence]:
            if not issubclass(op, UnaryOperator):
                continue
            if self._accept(token):
                term = self._try_parse_expr(precedence)
                return op(term)

        term = self._try_parse_expr(precedence + 1)
        if term is None:
            return None

        while True:
            found = False
            for token, op in ops[precedence]:
                if not issubclass(op, BinaryOperator):
                    continue

                if self._accept(token):
                    lhs = term
                    if op in right_associative_ops:
                        rhs = self._parse_expr(precedence)
                    else:
                        rhs = self._parse_expr(precedence + 1)

                    lhs, rhs = self._create_implicit_casts(lhs, rhs)
                    term = op(lhs, rhs)
                    found = True
            if not found:
                break

        return term

    def _try_parse_factor(self):
        if self._accept(Token.LPAREN):
            factor = self._parse_expr()
            self._expect(Token.RPAREN)

        elif self._accept(Token.STATIC_CAST):
            self._expect(Token.LESS)
            dest_type = self._parse_type()
            self._expect(Token.GREATER)

            self._expect(Token.LPAREN)
            expr = self._parse_expr()
            self._expect(Token.RPAREN)

            factor = StaticCast(expr, dest_type)

        elif self._accept(Token.IDENTIFIER):
            var_name = self._last_accepted_token.data
            if var_name not in self.variables:
                self.raise_error(self.SemanticError, f'{var_name} is undeclared')
            factor = Use(self.variables[var_name])

        elif self._accept(Token.NUMBER):
            factor = Immediate(self._last_accepted_token.data)

        else:
            return None

        return factor

    def _create_implicit_casts(self, lhs, rhs):
        if lhs.get_type() == rhs.get_type():
            return lhs, rhs

        if lhs.get_type() == Integer:
            if op is Assign:
                self.raise_error(self.SemanticError, 'Cannot assign float value to a variable of type integer')
            lhs = StaticCast(lhs, Float)
        else:
            rhs = StaticCast(rhs, Float)

        return lhs, rhs

    def eval_const_expr(self, expr):
        if isinstance(expr, Immediate):
            return expr.value
        if not isinstance(expr, Operator):
            self.raise_error(self.SemanticError, f'Could not evaluate {expr} as part of a constant-expression')
        operands = [self.eval_const_expr(op) for op in expr.operands]
        return expr.compute(*operands)

    def _advance(self):
        self._current_token = self._lexer.next_token()
        while self._current_token is not None and self._current_token.kind == Token.COMMENT:
            self._current_token = self._lexer.next_token()

    def _accept(self, token_kind):
        token = None
        if self._current_token is not None and self._current_token.kind == token_kind:
            self._last_accepted_token = self._current_token
            token = self._current_token
            self._advance()
        return token

    def _expect(self, token_kind):
        token = self._accept(token_kind)
        if token is None:
            self.raise_error(self.SyntaxError, f'Expected a {Token.kind_to_str(token_kind)}')
        return token

    def raise_error(self, error_class, msg):
        raise error_class(f'{msg} in {self._current_token.location}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs='+', help='Input files')
    parser.add_argument('-o', '--output-file', default='-', help='Output path')
    args = parser.parse_args()

    with utils.smart_open(args.output_file, 'w') as output_file:
        for input_path in args.input_file:
            with utils.smart_open(input_path, 'r') as input_file:
                parser = Parser(input_file)
                parser.parse()


if __name__ == '__main__':
    main()
