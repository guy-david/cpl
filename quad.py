from ir import *


class Quad:

    class Error(Exception):
        pass

    @classmethod
    def map_instruction(cls, instr):
        opcode, result_type_class, *rest = instr

        if result_type_class is Integer:
            prefix = 'I'
        elif result_type_class is Float:
            prefix = 'R'
        else:
            raise cls.Error(f'{cls.__name__} back-end does not support the basic type {result_type_class}')

        if issubclass(opcode, UnaryOperator):
            result, arg1 = rest

        if issubclass(opcode, BinaryOperator):
            result, arg1, arg2 = rest

        if opcode is Input:
            variable_name = rest[0]
            instrs = [f'{prefix}INP {variable_name}']

        elif opcode is Output:
            value = rest[0]
            instrs = [f'{prefix}PRT {value}']

        elif opcode is StaticCast:
            if result_type_class is Integer:
                instrs = [f'RTOI {result} {arg1}']
            else:
                instrs = [f'ITOR {result} {arg1}']

        elif opcode is UnaryAdd:
            instrs = [f'{prefix}ADD {result} 0 {arg1}']

        elif opcode is Negate:
            instrs = [f'{prefix}SUB {result} 0 {arg1}']

        elif opcode is Not:
            instrs = [f'{prefix}EQL {result} {arg1} 0']

        elif opcode is Assign:
            instrs = [f'{prefix}ASN {result} {arg1}']

        elif opcode is Or:
            instrs = []

            if isinstance(arg1, int) or isinstance(arg1, float):
                normalized_arg1 = int(arg1 == 0)
            else:
                normalized_arg1 = f'_{arg1}'
                instrs.append(f'{prefix}EQL {normalized_arg1} {arg1} 0')

            if isinstance(arg2, int) or isinstance(arg2, float):
                normalized_arg2 = int(arg2 == 0)
            else:
                normalized_arg2 = f'_{arg2}'
                instrs.append(f'{prefix}EQL {normalized_arg2} {arg2} 0')

            instrs.append(f'{prefix}ADD {result} {normalized_arg1} {normalized_arg2}')
            return instrs

        elif opcode is And:
            instrs = []

            if isinstance(arg1, int) or isinstance(arg1, float):
                normalized_arg1 = int(arg1 == 0)
            else:
                normalized_arg1 = f'_{arg1}'
                instrs.append(f'{prefix}EQL {normalized_arg1} {arg1} 0')

            if isinstance(arg2, int) or isinstance(arg2, float):
                normalized_arg2 = int(arg2 == 0)
            else:
                normalized_arg2 = f'_{arg2}'
                instrs.append(f'{prefix}EQL {normalized_arg2} {arg2} 0')

            instrs.append(f'{prefix}MLT {result} {normalized_arg1} {normalized_arg2}')
            return instrs

        elif opcode is Equal:
            instrs = [f'{prefix}EQL {result} {arg1} {arg2}']

        elif opcode is NotEqual:
            instrs = [f'{prefix}NQL {result} {arg1} {arg2}']

        elif opcode is Less:
            instrs = [f'{prefix}LSS {result} {arg1} {arg2}']

        elif opcode is Greater:
            instrs = [f'{prefix}GRT {result} {arg1} {arg2}']

        elif opcode is LessOrEqual:
            return [
                f'{prefix}EQL {result} {arg1} {arg2}',
                f'{prefix}LSS _{result} {arg1} {arg2}',
                f'{prefix}ADD {result} {result} _{result}']

        elif opcode is GreaterOrEqual:
            return [
                f'{prefix}EQL {result} {arg1} {arg2}',
                f'{prefix}GRT _{result} {arg1} {arg2}',
                f'{prefix}ADD {result} {result} _{result}']

        elif opcode is Add:
            instrs = [f'{prefix}ADD {result} {arg1} {arg2}']

        elif opcode is Sub:
            instrs = [f'{prefix}SUB {result} {arg1} {arg2}']

        elif opcode is Mul:
            instrs = [f'{prefix}MLT {result} {arg1} {arg2}']

        elif opcode is Div:
            instrs = [f'{prefix}DIV {result} {arg1} {arg2}']

        elif opcode is Jump:
            label = rest[0]
            instrs = [f'JUMP <{label}>']

        elif opcode is CondBr:
            test_result, true_label, false_label = rest
            instrs = [f'JMPZ <{false_label}> {test_result}',
                      f'JUMP <{true_label}>']

        elif opcode is Halt:
            instrs = ['HALT']

        else:
            raise cls.Error(f'{cls.__name__} back-end does not support {opcode}')

        return instrs
