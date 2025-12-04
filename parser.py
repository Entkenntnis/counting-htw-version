from typing import Optional


def parse_message(content: str) -> Optional[int]:
    """
    Parse a message as either an integer literal (canonical `int(..., 0)`)
    or as an expression using +,-,*,/ and parentheses with int-literals.
    Returns an int result or None if parsing fails.
    """
    if content is None:
        return None
    s = content.strip()
    if not s:
        return None
    # First try as a plain integer literal
    try:
        return int(s, 0)
    except Exception:
        pass
    # Fallback to expression evaluation
    try:
        return evaluate_expression(s)
    except Exception:
        return None


def evaluate_expression(text: str) -> int:
    """Evaluate expressions with +,-,*,/ and parentheses using int literals only.
    Literals follow Python's int canonical parsing (int(lit, 0)). Result is rounded to int.
    """
    s = text.strip()
    if not s:
        raise ValueError("Empty expression")
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/()":
            tokens.append(c)
            i += 1
            continue
        # identifiers for functions (e.g., sqrt, fac, factorial)
        if c.isalpha():
            j = i
            while j < len(s) and (s[j].isalpha()):
                j += 1
            ident = s[i:j]
            tokens.append(ident)
            i = j
            continue
        j = i
        while j < len(s) and (not s[j].isspace()) and s[j] not in "+-*/()":
            j += 1
        lit = s[i:j]
        try:
            tokens.append(int(lit, 0))
        except Exception:
            raise ValueError(f"Invalid literal: {lit}")
        i = j

    prec = {"+": 1, "-": 1, "*": 2, "/": 2}
    output = []
    ops = []
    prev = None
    for t in tokens:
        if isinstance(t, int):
            output.append(float(t))
            prev = "num"
        elif t in "+-":
            if prev in (None, "op", "("):
                output.append(0.0)
            while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                output.append(ops.pop())
            ops.append(t)
            prev = "op"
        elif t in "*/":
            while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                output.append(ops.pop())
            ops.append(t)
            prev = "op"
        elif isinstance(t, str) and t not in (
            "(",
            ")",
            "+",
            "-",
            "*",
            "/",
        ):  # function name
            ops.append(t)
            prev = "func"
        elif t == "(":
            ops.append(t)
            prev = "("
        elif t == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops:
                raise ValueError("Mismatched parentheses")
            ops.pop()
            # if a function is on top, pop it to output
            if (
                ops
                and isinstance(ops[-1], str)
                and ops[-1] not in ("+", "-", "*", "/", "(", ")")
            ):
                output.append(ops.pop())
            prev = "num"
    while ops:
        op = ops.pop()
        if op in ("(", ")"):
            raise ValueError("Mismatched parentheses")
        output.append(op)

    st = []
    # supported unary functions (self-contained checks inside functions)
    import math

    def _sqrt(x: float) -> float:
        if x < 0:
            raise ValueError("sqrt() not defined for negative values")
        return math.sqrt(x)

    def _fac(x: float) -> float:
        xi = int(x)
        if xi < 0:
            raise ValueError("factorial() not defined for negative values")
        return float(math.factorial(xi))

    funcs = {
        "sqrt": _sqrt,
        "fac": _fac,
        "factorial": _fac,
    }
    for t in output:
        if isinstance(t, float):
            st.append(t)
        else:
            # operator or function
            if t in ("+", "-", "*", "/"):
                if len(st) < 2:
                    raise ValueError("Invalid expression")
                b = st.pop()
                a = st.pop()
                if t == "+":
                    st.append(a + b)
                elif t == "-":
                    st.append(a - b)
                elif t == "*":
                    st.append(a * b)
                elif t == "/":
                    if b == 0:
                        raise ZeroDivisionError("division by zero")
                    st.append(a / b)
            else:
                # unary function: pop one arg
                if len(st) < 1:
                    raise ValueError("Invalid expression")
                x = st.pop()
                if t not in funcs:
                    raise ValueError(f"Unknown function: {t}")
                st.append(float(funcs[t](x)))
    if len(st) != 1:
        raise ValueError("Invalid expression")
    return round(st[0])


if __name__ == "__main__":
    print("Parser interactive mode. Type a value (Ctrl+C to exit).")
    try:
        while True:
            inp = input("> ").strip()
            result = parse_message(inp)
            if result is None:
                print("-> None (invalid)")
            else:
                print(f"-> {result}")
    except KeyboardInterrupt:
        print("\nBye!")
