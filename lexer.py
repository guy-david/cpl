#!/usr/bin/env python3

import argparse

import utils
from tokens import Token


class Lexer:

    class Error(Exception):
        pass

    KEYWORDS = {
        'break': Token.BREAK,
        'case': Token.CASE,
        'default': Token.DEFAULT,
        'else': Token.ELSE,
        'float': Token.FLOAT,
        'if': Token.IF,
        'input': Token.INPUT,
        'int': Token.INT,
        'output': Token.OUTPUT,
        'static_cast': Token.STATIC_CAST,
        'switch': Token.SWITCH,
        'while': Token.WHILE,
    }

    SYMBOLS = {
        '(': Token.LPAREN,
        ')': Token.RPAREN,
        '{': Token.LBRACE,
        '}': Token.RBRACE,
        ',': Token.COMMA,
        ';': Token.SEMICOLON,
        ':': Token.COLON,
        '=': Token.ASSIGN,
        '==': Token.EQUAL,
        '!=': Token.NEQUAL,
        '<': Token.LESS,
        '>': Token.GREATER,
        '<=': Token.EQLESS,
        '>=': Token.EQGREATER,
        '+': Token.PLUS,
        '-': Token.MINUS,
        '*': Token.MULTIPLY,
        '/': Token.DIVIDE,
        '||': Token.OR,
        '&&': Token.AND,
        '!': Token.NOT,
        '/*': Token.COMMENT,
    }

    def build_prefixes_list(strings):
        strings = list(strings)
        return [[key[:l] for key in strings]
                for l in range(max(map(len, strings)) + 1)]

    SYMBOLS_BY_PREFIX = build_prefixes_list(SYMBOLS.keys())

    def __init__(self, stream):
        self.stream = stream
        self.eof = False
        self.line = 1
        self.column = 1
        self._c = ' '

    def tokens(self):
        while not self.eof:
            token = self.next_token()
            if token is None:
                break
            yield token

    def next_token(self):
        kind = None
        data = None

        # Skip spaces
        while self._c.isspace():
            self._c = self._read_char()

        # Handle keywords and identifiers
        if self._c == '_' or self._c.isalpha():
            identifier = self._c
            while True:
                self._c = self._read_char()
                if self._c != '_' and not self._c.isalnum():
                    break
                identifier += self._c

            kind = self.KEYWORDS.get(identifier, Token.IDENTIFIER)
            data = identifier if kind == Token.IDENTIFIER else None

        # Handle numbers
        elif self._c.isdigit():
            is_float = False
            num_str = self._c
            while True:
                self._c = self._read_char()
                if not self._c.isdigit():
                    break
                num_str += self._c
            if self._c == '.':
                is_float = True
                num_str += self._c

                while True:
                    self._c = self._read_char()
                    if not self._c.isdigit():
                        break
                    num_str += self._c

            kind = Token.NUMBER
            data = float(num_str) if is_float else int(num_str)

        # Handle operators and comments
        elif self._c in self.SYMBOLS_BY_PREFIX[1]:
            best_token = None
            op = ''

            for i in range(1, len(self.SYMBOLS_BY_PREFIX)):
                if op + self._c not in self.SYMBOLS_BY_PREFIX[i]:
                    break
                op += self._c
                self._c = self._read_char()

                best_token = self.SYMBOLS.get(op, best_token)

            kind = self.SYMBOLS[op]
            if kind == Token.COMMENT:
                COMMENT_END = '*/'

                comment_text = ''
                candidate = len(COMMENT_END) * ' '
                while True:
                    self._c = self._read_char()
                    if len(self._c) == 0:
                        self._raise_error('Expected comment to end before EOF')

                    comment_text += self._c
                    candidate = candidate[-1:] + self._c
                    if candidate == COMMENT_END:
                        break

                # Must always contain the next character after matching
                self._c = self._read_char()

                comment_text = comment_text[:-len(COMMENT_END)]
                data = comment_text

        if kind is None:
            if self.eof:
                return None
            self._raise_error(f'Did not expect \'{self._c}\'')

        return Token(kind, self.stream.name, self.line, self.column, data)

    def _read_char(self):
        c = self.stream.read(1)
        if len(c) == 0:
            self.eof = True
        elif c.isspace():
            if c == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return c

    def _raise_error(self, msg):
        raise self.Error(f'{msg} in {self.stream.name}:{self.line}:{self.column}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs='+', help='Input files')
    parser.add_argument('-o', '--output-file', default='-', help='Output path')
    args = parser.parse_args()

    with utils.smart_open(args.output_file, 'w') as output_file:
        for input_path in args.input_file:
            with utils.smart_open(input_path, 'r') as input_file:
                lexer = Lexer(input_file)
                for token in lexer.tokens():
                    output_file.write(f'{token}\n')


if __name__ == '__main__':
    main()
