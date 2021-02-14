#!/usr/bin/env python3

import argparse

import utils
from parser import Parser
from ir import *


class CodeGenerator:
    def __init__(self):
        self._t = 0

    def gen_temp(self):
        self._t += 1
        return f't{self._t}'

    def gen(self, variables, stmts):
        t = 0
        for stmt in stmts:
            self.emit(stmt)

    def emit(self, stmt, dest=None):
        result = None

        if isinstance(stmt, Immediate):
            result = stmt.value
            if dest is not None:
                print(f'{dest} = {result}')
                result = dest

        elif isinstance(stmt, Use):
            result = stmt.variable.name
            if dest is not None:
                print(f'{dest} = {result}')
                result = dest

        elif isinstance(stmt, UnaryOperator):
            arg = self.emit(stmt.operands[0])
            result = dest if dest is not None else self.gen_temp()
            print(f'{result} = {stmt.__class__.__name__} {arg}')

        elif isinstance(stmt, BinaryOperator):
            if isinstance(stmt, Assign):
                result = self.emit(stmt.operands[0])
                src = self.emit(stmt.operands[1], result)
                if dest is not None:
                    print(f'{dest} = {result}')
            else:
                arg1 = self.emit(stmt.operands[0])
                arg2 = self.emit(stmt.operands[1])
                result = dest if dest is not None else self.gen_temp()
                print(f'{result} = {arg1} {stmt.__class__.__name__} {arg2}')
        return result


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

                code_gen = CodeGenerator()
                code_gen.gen(parser.variables, parser.stmts)


if __name__ == '__main__':
    main()
