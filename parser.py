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
        self._token = None

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

        elif self._parse_expr():
            self._expect(Token.SEMICOLON)

        else:
            return None

        return 1

    def _parse_boolexpr(self):
        self._parse_boolterm()
        while True:
            if self._accept(Token.OR):
                pass
            else:
                break
            self._parse_boolterm()

    def _parse_boolterm(self):
        self._parse_boolfactor()
        while True:
            if self._accept(Token.AND):
                pass
            else:
                break
            self._parse_boolfactor()

    def _parse_boolfactor(self):
        if self._accept(Token.NOT):
            self._expect(Token.LPAREN)
            self._parse_boolexpr()
            self._expect(Token.RPAREN)
        else:
            self._parse_expr()
            if self._accept(Token.EQUAL):
                pass
            elif self._accept(Token.NEQUAL):
                pass
            elif self._accept(Token.LESS):
                pass
            elif self._accept(Token.GREATER):
                pass
            elif self._accept(Token.EQLESS):
                pass
            elif self._accept(Token.EQGREATER):
                pass
            else:
                self.raise_syntax_error('Expected a comparison operator')
            self._parse_expr()

    def _parse_expr(self):
        term = self._parse_term1()
        while True:
            if self._accept(Token.ASSIGN):
                pass
            else:
                break
            term = Assign(term, self._parse_term1())
        return term

    def _parse_term1(self):
        term = self._parse_term2()
        while True:
            if self._accept(Token.PLUS):
                op = Add
            elif self._accept(Token.MINUS):
                op = Sub
            else:
                break
            term = op(term, self._parse_term2())
        return term

    def _parse_term2(self):
        term = self._parse_factor()
        while True:
            if self._accept(Token.MULTIPLY):
                op = Mul
            elif self._accept(Token.DIVIDE):
                op = Div
            else:
                break
            term = op(term, self._parse_factor())
        return term

    def _parse_factor(self):
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
            factor = Parameter(self._token.data)

        elif self._accept(Token.NUMBER):
            factor = Immediate(self._token.data)

        else:
            return None

        return factor

    def _advance(self):
        self._token = self._lexer.next_token()
        while self._token is not None and self._token.kind == Token.COMMENT:
            self._token = self._lexer.next_token()

    def _accept(self, token_kind):
        result = None
        if self._token is not None and self._token.kind == token_kind:
            result = self._token
            self._advance()
        return result

    def _expect(self, token_kind):
        result = self._accept(token_kind)
        if result is None:
            self.raise_syntax_error(f'Expected a {Token.kind_to_str(token_kind)}')
        return result

    def raise_syntax_error(self, msg):
        file_path, line, column = self._token.file_path, self._token.line, self._token.column
        raise self.SyntaxError(f'{msg} in {file_path}:{line}:{column}')


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
