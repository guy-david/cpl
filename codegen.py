#!/usr/bin/env python3

import re
import argparse

import utils
from parser import Parser
from ir import *
from quad import *


class BasicBlock:
    def __init__(self, id_num):
        self.id_num = id_num
        self.label = None
        self.address = None
        self.instructions = []


class CodeGenerator:

    class Error(Exception):
        pass

    def __init__(self, backend_name):
        self._t = 0
        self._l = 0
        self._break_to_labels = []
        self._backend_name = backend_name.lower()
        self._basic_blocks = []
        self._init_new_bb()
        self._label_to_bb = {}

    def gen(self, stmts):
        # Emit IR instructions and labels into a list of basic-blocks
        self._emit(stmts)
        # Program must end with a HALT instruction
        self._emit(Halt())

        self._remove_empty_basic_blocks()
        self._select_instructions()
        self._translate_labels()
        self._print_instructions()

    def _remove_empty_basic_blocks(self):
        for i in range(len(self._basic_blocks) - 1, -1, -1):
            bb = self._basic_blocks[i]
            if len(bb.instructions) > 0:
                continue
            if bb.label is not None:
                next_bb = self._basic_blocks[i + 1]
                self._label_to_bb[bb.label] = self._label_to_bb[next_bb.label]
            self._basic_blocks.pop(i)

    def _select_instructions(self):
        if self._backend_name == 'quad':
            backend = Quad
        else:
            raise self.Error(f'Unsupported back-end \'{self._backend_name}\'')

        for bb in self._basic_blocks:
            for i in range(len(bb.instructions)):
                bb.instructions[i] = backend.map_instruction(bb.instructions[i])

    def _translate_labels(self):
        # Compute starting address for each basic-block
        current_address = 1
        for bb in self._basic_blocks:
            bb.address = current_address
            bb.label = None
            for instr in bb.instructions:
                current_address += 1

        for bb in self._basic_blocks:
            for i, instr in enumerate(bb.instructions):
                unresolved_labels = re.findall(r'<(\w+)>', instr)
                resolved_labels = []
                for label in unresolved_labels:
                    dest_bb_address = self._label_to_bb[label].address
                    resolved_labels.append(dest_bb_address)
                resolved_instr = re.sub(r'<(\w+)>', '{}', instr).format(*resolved_labels)
                bb.instructions[i] = resolved_instr

    def _print_instructions(self):
        for bb in self._basic_blocks:
            assert bb.label is None
            for instr in bb.instructions:
                print(instr)

    def _init_new_bb(self):
        bb = BasicBlock(len(self._basic_blocks))
        self._basic_blocks.append(bb)

    def _add_instr(self, instr):
        self._basic_blocks[-1].instructions.append(instr)

    def _gen_temp(self):
        self._t += 1
        return f't{self._t}'

    def _gen_label(self):
        self._l += 1
        return f'L{self._l}'

    def _emit_label(self, label):
        self._init_new_bb()
        bb = self._basic_blocks[-1]
        bb.label = label
        self._label_to_bb[label] = bb

    def _emit_jump(self, label):
        self._add_instr([Jump, Integer, label])
        self._init_new_bb()

    def _emit_conditional_branch(self, condition, true_label, false_label):
        self._add_instr([CondBr, Integer, condition, true_label, false_label])
        self._init_new_bb()

    def _emit(self, obj, dest=None):
        result = None
        result_type = None

        if isinstance(obj, list):
            for o in obj:
                self._emit(o)

        elif isinstance(obj, Immediate):
            result = obj.value
            result_type = obj.get_type()
            if dest is not None:
                self._add_instr([Assign, result_type, dest, result])
                result = dest

        elif isinstance(obj, Use):
            result = obj.variable.name
            result_type = obj.variable.type_class
            if dest is not None:
                self._add_instr([Assign, result_type, dest, result])
                result = dest

        elif isinstance(obj, UnaryOperator):
            arg, result_type = self._emit(obj.operands[0])
            result = dest if dest is not None else self._gen_temp()
            self._add_instr([type(obj), result_type, result, arg])

        elif isinstance(obj, BinaryOperator):
            if isinstance(obj, Assign):
                result, result_type = self._emit(obj.operands[0])
                self._emit(obj.operands[1], result)
                if dest is not None:
                    self._add_instr([Assign, result_type, dest, result])
            else:
                arg1, arg1_type = self._emit(obj.operands[0])
                arg2, arg2_type = self._emit(obj.operands[1])
                result = dest if dest is not None else self._gen_temp()
                assert arg1_type is arg2_type
                result_type = arg1_type
                self._add_instr([type(obj), result_type, result, arg1, arg2])

        elif isinstance(obj, Conditional):
            cond_result, _ = self._emit(obj.condition)
            true_label = self._gen_label()
            if obj.false_case is not None:
                false_label = self._gen_label()
                end_label = self._gen_label()
            else:
                end_label = self._gen_label()
                false_label = end_label

            self._emit_conditional_branch(cond_result, true_label, false_label)
            self._emit_label(true_label)
            self._emit(obj.true_case)

            if obj.false_case is not None:
                self._emit_jump(end_label)
                self._emit_label(false_label)
                self._emit(obj.false_case)

            self._emit_label(end_label)

        elif isinstance(obj, While):
            test_label = self._gen_label()
            body_label = self._gen_label()
            end_label = self._gen_label()
            self._break_to_labels.append(end_label)

            self._emit_jump(test_label)
            self._emit_label(body_label)
            self._emit(obj.body)
            self._emit_label(test_label)
            cond_result = self._emit(obj.condition)
            self._emit_conditional_branch(cond_result, body_label, end_label)
            self._emit_label(end_label)

        elif isinstance(obj, Switch):
            value = self._emit(obj.value)

            default_case_index = None
            case_test_labels = []
            for i, case in enumerate(obj.cases):
                if case.value is not None:
                    case_test_labels.append(self._gen_label())
                else:
                    default_case_index = i
            if default_case_index is not None:
                case_test_labels.append(self._gen_label())

            case_body_labels = [self._gen_label() for _ in obj.cases]

            end_label = self._gen_label()
            self._break_to_labels.append(end_label)

            for i, case in enumerate(obj.cases):
                if i > 0:
                    self._emit_label(case_test_labels[i])
                if i == default_case_index:
                    continue
                next_label = case_test_labels[i + 1] if i + 1 < len(case_test_labels) else end_label
                case_value = self._emit(case.value)
                test_result = self._emit(Equal(value, case_value))
                self._emit_conditional_branch(test_result, case_body_labels[i], next_label)

            if default_case_index is not None:
                self._emit_jump(case_body_labels[default_case_index])

            for i, case in enumerate(obj.cases):
                self._emit_label(case_body_labels[i])
                self._emit(case.stmts)

            self._emit_label(end_label)

        elif isinstance(obj, Break):
            assert len(self._break_to_labels) > 0
            self._emit_jump(self._break_to_labels[-1])

        elif isinstance(obj, Input):
            self._add_instr([Input, obj.variable.type_class, obj.variable.name])

        elif isinstance(obj, Output):
            result, result_type = self._emit(obj.expr)
            self._add_instr([Output, result_type, result])

        elif isinstance(obj, Halt):
            self._add_instr([Halt, Integer])

        elif isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, str):
            return obj

        else:
            raise self.Error(f'Missing implemenation for generation of {obj}')

        return result, result_type


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
