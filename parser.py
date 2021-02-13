#!/usr/bin/env python3

import argparse

import utils
from lexer import Lexer
from tokens import Token
from ir import *


class Parser:

    class SyntaxError(Exception):
        pass

    TYPES = {
        Token.INT: Integer,
        Token.FLOAT: Float,
    }

    def __init__(self, stream):
        self._lexer = Lexer(stream)
        self._last_accepted_token = None
        self._current_token = None

    def parse(self):
        self._advance()
        self._parse_program()

    def _parse_program(self):
        decls = self._parse_declarations()
        block = self._parse_stmt_block()

    def _parse_declarations(self):
        decls = []
        while True:
            variables = self._parse_id_list()
            if len(variables) == 0:
                return decls
            self._expect(Token.COLON)
            type_class = self._parse_type()
            self._expect(Token.SEMICOLON)
        return decls

    def _parse_type(self):
        for token, type_class in self.TYPES.items():
            if self._accept(token):
                return type_class
        self._expected('Expected a type')

    def _parse_id_list(self):
        variables = []
        while True:
            variable = self._accept(Token.IDENTIFIER)
            if variable is None:
                return variables

            variables.append(variable)
            while self._accept(Token.COMMA):
                variable = self._expect(Token.IDENTIFIER)
                variables.append(variable)
        return variables

    def _parse_stmt_block(self):
        self._expect(Token.LBRACE)
        stmts = self._parse_stmt_list()
        self._expect(Token.RBRACE)
        return stmts

    def _parse_stmt_list(self):
        while True:
            stmt = self._parse_stmt()
            if stmt is None:
                break

    def _parse_stmt(self):
        if self._accept(Token.IF):
            self._expect(Token.LPAREN)
            self._parse_boolexpr()
            self._expect(Token.RPAREN)
            self._parse_stmt()

            if self._accept(Token.ELSE):
                self._parse_stmt()

        elif self._accept(Token.INPUT):
            self._expect(Token.LPAREN)
            self._expect(Token.IDENTIFIER)
            self._expect(Token.RPAREN)
            self._expect(Token.SEMICOLON)

        elif self._accept(Token.OUTPUT):
            self._expect(Token.LPAREN)
            self._parse_expr()
            self._expect(Token.RPAREN)
            self._expect(Token.SEMICOLON)

        elif self._accept(Token.WHILE):
            self._expect(Token.LPAREN)
            self._parse_boolexpr()
            self._expect(Token.RPAREN)
            self._parse_stmt()

        elif self._accept(Token.SWITCH):
            self._expect(Token.LPAREN)
            self._parse_expr()
            self._expect(Token.RPAREN)

            self._expect(Token.LBRACE)

            while self._accept(Token.CASE):
                self._parse_expr()
                self._expect(Token.COLON)
                self._parse_stmt_list()
            if self._accept(Token.DEFAULT):
                self._expect(Token.COLON)
                self._parse_stmt_list()
            while self._accept(Token.CASE):
                self._parse_expr()
                self._expect(Token.COLON)
                self._parse_stmt_list()

            self._expect(Token.RBRACE)

        elif self._accept(Token.BREAK):
            self._expect(Token.SEMICOLON)

        elif self._accept(Token.LBRACE):
            self._parse_stmt_list()
            self._expect(Token.RBRACE)

        elif self._try_parse_expr():
            self._expect(Token.SEMICOLON)

        else:
            expr = self._try_parse_expr()
            if expr is None:
                return None
            self._expect(Token.SEMICOLON)

            return expr

    def _parse_expr(self, precedence=0):
        expr = self._try_parse_expr(precedence)
        if expr is None:
            self.raise_syntax_error('Expected an expression')
        return expr

    def _try_parse_expr(self, precedence=0):
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

        lhs = self._try_parse_expr(precedence + 1)
        if lhs is None:
            return None

        while True:
            found = False
            for token, op in ops[precedence]:
                if not issubclass(op, BinaryOperator):
                    continue
                if self._accept(token):
                    rhs = self._parse_expr(precedence + 1)
                    lhs = op(lhs, rhs)
                    found = True
            if not found:
                break

        return lhs

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
            factor = Parameter(self._last_accepted_token.data)

        elif self._accept(Token.NUMBER):
            factor = Immediate(self._last_accepted_token.data)

        else:
            return None

        return factor

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
            self.raise_syntax_error(f'Expected a {Token.kind_to_str(token_kind)}')
        return token

    def raise_syntax_error(self, msg):
        raise self.SyntaxError(f'{msg} in {self._current_token.location}')


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
