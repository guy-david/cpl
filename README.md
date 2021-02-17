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
</table>