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
    # remove surrounding single backticks, e.g., `1+2`
    if len(s) >= 2 and s[0] == "`" and s[-1] == "`":
        s = s[1:-1].strip()
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


def evaluate_expression(text: str):
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
        if c in "+-*/()^":
            tokens.append(c)
            i += 1
            continue
        # identifiers for functions or constants (e.g., sqrt, fac, pi, e)
        if c.isalpha():
            j = i
            while j < len(s) and (s[j].isalpha()):
                j += 1
            ident = s[i:j]
            # constants mapping
            if ident in ("pi", "e"):
                import math

                const_val = math.pi if ident == "pi" else math.e
                tokens.append(const_val)
            else:
                tokens.append(ident)
            i = j
            continue
        j = i
        while j < len(s) and (not s[j].isspace()) and s[j] not in "+-*/()^":
            j += 1
        lit = s[i:j]
        try:
            tokens.append(int(lit, 0))
        except Exception:
            raise ValueError(f"Invalid literal: {lit}")
        i = j

    prec = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
    output = []
    ops = []
    prev = None
    for t in tokens:
        if isinstance(t, (int, float)):
            output.append(float(t))
            prev = "num"
        elif t in "+-":
            if prev in (None, "op", "("):
                output.append(0.0)
            while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                output.append(ops.pop())
            ops.append(t)
            prev = "op"
        elif t in "*/^":
            # '^' is right-associative: only pop ops with strictly higher precedence
            while (
                ops
                and ops[-1] in prec
                and (
                    (t != "^" and prec[ops[-1]] >= prec[t])
                    or (t == "^" and prec[ops[-1]] > prec[t])
                )
            ):
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

    def _sqrt(x: float):
        if x < 0:
            raise ValueError("sqrt() not defined for negative values")
        return math.sqrt(x)

    def _fac(x: float):
        xi = int(x)
        if xi < 0:
            raise ValueError("factorial() not defined for negative values")
        return math.factorial(xi)

    def _abs(x: float):
        return abs(x)

    def _floor(x: float):
        return math.floor(x)

    def _ceil(x: float):
        return math.ceil(x)

    def _exp(x: float):
        return math.exp(x)

    def _sin(x: float):
        return math.sin(x)

    def _cos(x: float):
        return math.cos(x)

    def _tan(x: float):
        return math.tan(x)

    def _asin(x: float):
        if x < -1 or x > 1:
            raise ValueError("asin() domain is [-1, 1]")
        return math.asin(x)

    def _acos(x: float):
        if x < -1 or x > 1:
            raise ValueError("acos() domain is [-1, 1]")
        return math.acos(x)

    def _atan(x: float):
        return math.atan(x)

    def _log10(x: float):
        if x <= 0:
            raise ValueError("log() not defined for non-positive values")
        return math.log10(x)

    def _ln(x: float):
        if x <= 0:
            raise ValueError("ln() not defined for non-positive values")
        return math.log(x)

    funcs = {
        "sqrt": _sqrt,
        "fac": _fac,
        "factorial": _fac,
        "abs": _abs,
        "floor": _floor,
        "ceil": _ceil,
        "exp": _exp,
        "sin": _sin,
        "cos": _cos,
        "tan": _tan,
        "asin": _asin,
        "acos": _acos,
        "atan": _atan,
        "log": _log10,
        "ln": _ln,
    }
    for t in output:
        if isinstance(t, float):
            st.append(t)
        else:
            # operator or function
            if t in ("+", "-", "*", "/", "^"):
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
                elif t == "^":
                    st.append(a**b)
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
    return st[0]


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
