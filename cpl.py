#!/usr/bin/env python3

import argparse

import utils
from parser import Parser
from codegen import CodeGenerator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', nargs='+', help='Input files')
    parser.add_argument('-o', '--output-file', default='-', help='Output path')
    args = parser.parse_args()

    with utils.smart_open(args.output_file, 'w') as output_file:
        for input_path in args.input_file:
            with utils.smart_open(input_path, 'r') as input_file:
                parser = Parser(input_file)
                stmts = parser.parse()

                code_gen = CodeGenerator('quad')
                code_gen.gen(stmts)


if __name__ == '__main__':
    main()
