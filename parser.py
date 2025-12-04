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
        elif t == "(":
            ops.append(t)
            prev = "("
        elif t == ")":
            while ops and ops[-1] != "(":
                output.append(ops.pop())
            if not ops:
                raise ValueError("Mismatched parentheses")
            ops.pop()
            prev = "num"
    while ops:
        op = ops.pop()
        if op in ("(", ")"):
            raise ValueError("Mismatched parentheses")
        output.append(op)

    st = []
    for t in output:
        if isinstance(t, float):
            st.append(t)
        else:
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
