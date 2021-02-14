#!/usr/bin/env python3

import argparse

import utils
from parser import Parser
from ir import *


class CodeGenerator:

    class Error(Exception):
        pass

    def __init__(self):
        self._t = 0
        self._l = 0
        self._break_to_labels = []

    def gen(self, stmts):
        self.emit(stmts)

    def gen_temp(self):
        self._t += 1
        return f't{self._t}'

    def gen_label(self):
        self._l += 1
        return f'L{self._l}'

    def emit_label(self, label):
        print(f'{label}:')

    def emit_jump(self, label):
        print(f'jump {label}')

    def emit_conditional_branch(self, condition, true_label, false_label):
        print(f'branch {condition}, {true_label}, {false_label}')

    def emit(self, obj, dest=None):
        result = None

        if isinstance(obj, list):
            for o in obj:
                self.emit(o)

        elif isinstance(obj, Immediate):
            result = obj.value
            if dest is not None:
                print(f'{dest} = {result}')
                result = dest

        elif isinstance(obj, Use):
            result = obj.variable.name
            if dest is not None:
                print(f'{dest} = {result}')
                result = dest

        elif isinstance(obj, UnaryOperator):
            arg = self.emit(obj.operands[0])
            result = dest if dest is not None else self.gen_temp()
            print(f'{result} = {obj.__class__.__name__} {arg}')

        elif isinstance(obj, BinaryOperator):
            if isinstance(obj, Assign):
                result = self.emit(obj.operands[0])
                src = self.emit(obj.operands[1], result)
                if dest is not None:
                    print(f'{dest} = {result}')
            else:
                arg1 = self.emit(obj.operands[0])
                arg2 = self.emit(obj.operands[1])
                result = dest if dest is not None else self.gen_temp()
                print(f'{result} = {arg1} {obj.__class__.__name__} {arg2}')

        elif isinstance(obj, Conditional):
            cond_result = self.emit(obj.condition)
            true_label = self.gen_label()
            if obj.false_case is not None:
                false_label = self.gen_label()
                end_label = self.gen_label()
            else:
                end_label = self.gen_label()
                false_label = end_label

            self.emit_conditional_branch(cond_result, true_label, false_label)
            self.emit_label(true_label)
            self.emit(obj.true_case)

            if obj.false_case is not None:
                self.emit_jump(end_label)
                self.emit_label(false_label)
                self.emit(obj.false_case)

            self.emit_label(end_label)

        elif isinstance(obj, While):
            test_label = self.gen_label()
            body_label = self.gen_label()
            end_label = self.gen_label()
            self._break_to_labels.append(end_label)

            self.emit_jump(test_label)
            self.emit_label(body_label)
            self.emit(obj.body)
            self.emit_label(test_label)
            cond_result = self.emit(obj.condition)
            self.emit_conditional_branch(cond_result, body_label, end_label)
            self.emit_label(end_label)

        elif isinstance(obj, Switch):
            value = self.emit(obj.value)

            default_case_index = None
            case_test_labels = []
            for i, case in enumerate(obj.cases):
                if case.value is not None:
                    case_test_labels.append(self.gen_label())
                else:
                    default_case_index = i
            if default_case_index is not None:
                case_test_labels.append(self.gen_label())

            case_body_labels = [self.gen_label() for _ in obj.cases]

            end_label = self.gen_label()
            self._break_to_labels.append(end_label)

            for i, case in enumerate(obj.cases):
                if i > 0:
                    self.emit_label(case_test_labels[i])
                if i == default_case_index:
                    continue
                next_label = case_test_labels[i + 1] if i + 1 < len(case_test_labels) else end_label
                case_value = self.emit(case.value)
                test_result = self.emit(Equal(value, case_value))
                self.emit_conditional_branch(test_result, case_body_labels[i], next_label)

            if default_case_index is not None:
                self.emit_jump(case_body_labels[default_case_index])

            for i, case in enumerate(obj.cases):
                self.emit_label(case_body_labels[i])
                self.emit(case.stmts)

            self.emit_label(end_label)

        elif isinstance(obj, Break):
            assert len(self._break_to_labels) > 0
            self.emit_jump(self._break_to_labels[-1])

        elif isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, str):
            return obj

        else:
            raise self.Error(f'Missing implemenation for generation of {obj}')

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
                stmts = parser.parse()

                code_gen = CodeGenerator()
                code_gen.gen(stmts)


if __name__ == '__main__':
    main()
