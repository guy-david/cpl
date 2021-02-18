# CPL
Front-end for a made-up language as part of a compilers course.

## Project Structure
- `cpl.py` - Driver program
- `lexer.py` - Reads the textual source-code and converts it into a stream of tokens described in tokens.py
- `parser.py` - Parses variable declarations and builds and AST out of the statements in the code. Also does semantic analysis.
- `codegen.py` - Divides the AST into basic-blocks, maps IR instructions into the back-end's instructions and finally flattens the instructions into a single sequence.
- `quad.py` - Contains conversions between IR instructions into Quad instructions.

## Examples
<table>
    <tr>
        <th>CPL</th>
        <th>Quad</th>
    </tr>
    <tr>
<td>

```c
/* Finding minimum between two numbers */
a, b: float;
{
    input(a);
    input(b);
    if (a < b)
        output(a);
    else
        output(b);
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
RINP a
RINP b
RLSS t1 a b
JMPZ 7 t1
RPRT a
JUMP 8
RPRT b
HALT
```

</td>
    </tr>
    <tr>
<td>

```c
/* Sum a variadic list of integers */
N, num, sum : int;
{
    sum = 0;
    while (N > 0) {
        input(num);
        sum = sum + num;
        N = N - 1;
    }
    output(sum);
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
IASN sum 0
IGRT t1 N 0
JMPZ 8 t1
IINP num
IADD sum sum num
ISUB N N 1
JUMP 2
IPRT sum
HALT
```

</td>
    </tr>
    <tr>
<td>

```c
/* Tell if an integer is prime */
N, p, limit, result : int;
{
    result = 1;

    if (N < 2)
        result = 0;

    p = 2;
    limit = N / 2;
    while (p < limit) {
        if ((N / p) * p == N) {
            result = 0;
            break;
        }

        p = p + 1;
    }

    output(result);
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
IASN result 1
ILSS t1 N 2
JMPZ 5 t1
IASN result 0
IASN p 2
IDIV limit N 2
ILSS t2 p limit
JMPZ 17 t2
IDIV t3 N p
IMLT t4 t3 p
IEQL t5 t4 N
JMPZ 15 t5
IASN result 0
JUMP 17
IADD p p 1
JUMP 7
IPRT result
HALT
```

</td>
    </tr>
    <tr>
<td>

```c
/*
 * Simple Calculator
 * Accepts two floats and outputs a float if successful.
 * On error, the output is an integer. Error values:
 *     1: Invalid operation
 *     2: Division by zero
 */

/* Input numbers */
A, B : float;

/*
 * Desired operation:
 * - Addition=0
 * - Subtraction=1
 * - Multiplication=2
 * - Divison=3
 */
operation : int;

{
    input(A);
    input(B);
    input(operation);

    switch (operation) {
        default:
            output(1);
            break;
        case 0:
            output(A + B);
            break;
        case 1:
            output(A - B);
            break;
        case 2:
            output(A * B);
            break;
        case 3:
            /* B is a float so the immediate 0 is
             * implicitly casted to a float
             */
            if (B == 0)
                output(2);
            else
                output(A / B);
            break;
    }
}
```

</td>
<td>

```{assembly, attr.source='.numberLines'}
RINP A
RINP B
IINP operation
INQL t1 operation 0
JMPZ 15 t1
INQL t2 operation 1
JMPZ 18 t2
INQL t3 operation 2
JMPZ 21 t3
INQL t4 operation 3
JMPZ 24 t4
JUMP 31
IPRT 1
JUMP 31
RADD t5 A B
RPRT t5
JUMP 31
RSUB t6 A B
RPRT t6
JUMP 31
RMLT t7 A B
RPRT t7
JUMP 31
ITOR t8 0
REQL t9 B t8
JMPZ 29 t9
IPRT 2
JUMP 31
RDIV t10 A B
RPRT t10
HALT
```

</td>
    </tr>
</table>
