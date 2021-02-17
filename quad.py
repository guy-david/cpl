from ir import *
from codegen import Value


class Quad:

    class Error(Exception):
        pass

    @classmethod
    def map_instruction(cls, instr):
        assert len(instr) >= 1
        opcode, *rest = instr

        if len(rest) >= 3 and isinstance(rest[2], Value):
            arg2 = rest[2]
            a2 = arg2.name
        if len(rest) >= 2 and isinstance(rest[1], Value):
            arg1 = rest[1]
            a1 = arg1.name
        if len(rest) >= 1 and isinstance(rest[0], Value):
            result = rest[0]
            dst = result.name
            instr_type_class = (arg1 if issubclass(opcode, Compare) else result).type_class
            if instr_type_class is Integer:
                prefix = 'I'
            elif instr_type_class is Float:
                prefix = 'R'

        if opcode is Input:
            instrs = [f'{prefix}INP {dst}']

        elif opcode is Output:
            instrs = [f'{prefix}PRT {dst}']

        elif opcode is StaticCast:
            if result.type_class is Integer:
                instrs = [f'RTOI {dst} {a1}']
            else:
                instrs = [f'ITOR {dst} {a1}']

        elif opcode is UnaryAdd:
            instrs = [f'{prefix}ADD {dst} 0 {a1}']

        elif opcode is Negate:
            instrs = [f'{prefix}SUB {dst} 0 {a1}']

        elif opcode is Not:
            instrs = [f'{prefix}EQL {dst} {a1} 0']

        elif opcode is Assign:
            instrs = [f'{prefix}ASN {dst} {a1}']

        elif opcode is Or:
            instrs = []

            if isinstance(arg1, int) or isinstance(arg1, float):
                normalized_arg1 = int(arg1 == 0)
            else:
                normalized_arg1 = f'_{a1}'
                instrs.append(f'{prefix}EQL {normalized_arg1} {a1} 0')

            if isinstance(arg2, int) or isinstance(arg2, float):
                normalized_arg2 = int(arg2 == 0)
            else:
                normalized_arg2 = f'_{a2}'
                instrs.append(f'{prefix}EQL {normalized_arg2} {a2} 0')

            instrs.append(f'{prefix}ADD {dst} {normalized_arg1} {normalized_arg2}')
            return instrs

        elif opcode is And:
            instrs = []

            if isinstance(arg1, int) or isinstance(arg1, float):
                normalized_arg1 = int(arg1 == 0)
            else:
                normalized_arg1 = f'_{a1}'
                instrs.append(f'{prefix}EQL {normalized_arg1} {a1} 0')

            if isinstance(arg2, int) or isinstance(arg2, float):
                normalized_arg2 = int(arg2 == 0)
            else:
                normalized_arg2 = f'_{a2}'
                instrs.append(f'{prefix}EQL {normalized_arg2} {a2} 0')

            instrs.append(f'{prefix}MLT {dst} {normalized_arg1} {normalized_arg2}')
            return instrs

        elif opcode is Equal:
            instrs = [f'{prefix}EQL {dst} {a1} {a2}']

        elif opcode is NotEqual:
            instrs = [f'{prefix}NQL {dst} {a1} {a2}']

        elif opcode is Less:
            instrs = [f'{prefix}LSS {dst} {a1} {a2}']

        elif opcode is Greater:
            instrs = [f'{prefix}GRT {dst} {a1} {a2}']

        elif opcode is LessOrEqual:
            temp_dst = f'_{dst}'
            return [
                f'{prefix}EQL {dst} {a1} {a2}',
                f'{prefix}LSS {temp_dst} {a1} {a2}',
                f'{prefix}ADD {dst} {dst} {temp_dst}']

        elif opcode is GreaterOrEqual:
            temp_dst = f'_{dst}'
            return [
                f'{prefix}EQL {dst} {a1} {a2}',
                f'{prefix}GRT {temp_dst} {a1} {a2}',
                f'{prefix}ADD {dst} {dst} {temp_dst}']

        elif opcode is Add:
            instrs = [f'{prefix}ADD {dst} {a1} {a2}']

        elif opcode is Sub:
            instrs = [f'{prefix}SUB {dst} {a1} {a2}']

        elif opcode is Mul:
            instrs = [f'{prefix}MLT {dst} {a1} {a2}']

        elif opcode is Div:
            instrs = [f'{prefix}DIV {dst} {a1} {a2}']

        elif opcode is Jump:
            _, label = rest
            instrs = [f'JUMP <{label}>']

        elif opcode is CondBr:
            _, test_result, true_label, false_label = rest
            instrs = [f'JMPZ <{false_label}> {test_result.name}',
                      f'JUMP <{true_label}>']

        elif opcode is Halt:
            instrs = ['HALT']

        else:
            raise cls.Error(f'{cls.__name__} back-end does not support {opcode}')

        return instrs
