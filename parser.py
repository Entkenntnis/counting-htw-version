from math import log
from typing import Optional

# CJK number characters: digits and place-value multipliers
CJK_DIGITS = {
    "〇": 0, "零": 0,
    "一": 1, "二": 2, "两": 2, "兩": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
}
CJK_MULTIPLIERS = (
    ("兆", 1_000_000_000_000),
    ("億", 100_000_000), ("亿", 100_000_000),
    ("万", 10_000), ("萬", 10_000),
    ("千", 1_000),
    ("百", 100),
    ("十", 10),
)
KLINGON_DIGITS = {
    "wa'": 1,
    "cha'": 2,
    "wej": 3,
    "loS": 4,
    "vagh": 5,
    "jav": 6,
    "Soch": 7,
    "chorgh": 8,
    "Hut": 9
}
KLINGON_MULTIPLIERS = {
    "SaDSaghan": 1_000_000_000_000, "SanIDSaghan": 1_000_000_000_000,
    "vatlhSaghan": 100_000_000_000, "bIp'uy'": 100_000_000_000,
    "maHSaghan": 10_000_000_000, "netlh'uy'": 10_000_000_000,
    "vatlh'uy'": 100_000_000, "SaDbIp": 100_000_000, "SanIDbIp": 100_000_000,
    "maH'uy'": 10_000_000, "vatlhbIp": 10_000_000,
    "Saghan": 1_000_000_000,
    "'uy'": 1_000_000,
    "bIp": 100_000,
    "netlh": 10_000,
    "SaD": 1_000, "SanID": 1_000,
    "vatlh": 100,
    "maH": 10,
}

def parse_cjk_number(s: str) -> Optional[int]:
    """
    Parse CJK number symbols (e.g. 十=10, 二十五=25, 一百=100).
    Returns the integer value or None if the string is not a valid CJK number.
    """
    s = s.strip()
    if not s:
        return None
    # Quick check: at least one char must be a known CJK digit or multiplier
    valid_chars = set(CJK_DIGITS) | {m for m, _ in CJK_MULTIPLIERS}
    if not any(c in valid_chars for c in s):
        return None
    try:
        return _parse_cjk_inner(s)
    except (ValueError, KeyError):
        return None


def _parse_cjk_inner(s: str) -> int:
    """
    Simplified CJK parser. Numbers like:
    - 十 = 10 (standalone)
    - 十五 = 15 (10 + 5)
    - 二十 = 20 (2 * 10)
    - 二十五 = 25 (2*10 + 5)
    - 百 = 100
    - 一百二十五 = 125
    - 一千二百 = 1200
    - 一万 = 10000
    """
    result = 0
    current = 0
    i = 0
    n = len(s)

    while i < n:
        c = s[i]
        if c in CJK_DIGITS:
            d = CJK_DIGITS[c]
            i += 1
            if i < n:
                next_c = s[i]
                found = False
                for mul_char, mul_val in CJK_MULTIPLIERS:
                    if next_c == mul_char:
                        if mul_val >= 10_000:
                            result += (current + d) * mul_val
                            current = 0
                        else:
                            current += d * mul_val
                        i += 1
                        found = True
                        break
                if not found:
                    current += d
            else:
                current += d
        else:
            found = False
            for mul_char, mul_val in CJK_MULTIPLIERS:
                if c == mul_char:
                    if mul_val >= 10_000:
                        result += (current if current else 1) * mul_val
                        current = 0
                    else:
                        # 十, 百, 千 as standalone or after digits
                        # 十 alone = 10, 二十 = 2*10
                        if current == 0:
                            current = mul_val
                        else:
                            # 二十: current=2, 十 -> 2*10=20
                            current = current * mul_val
                    i += 1
                    found = True
                    break
            if not found:
                raise ValueError(f"Invalid CJK character: {c}")

    return result + current

def parse_klingon_number(s: str) -> Optional[int]:
    s = s.replace("‘", "'").replace("’", "'").replace("`", "'")
    def parse_word(word: str) -> int:
        for digit in KLINGON_DIGITS:
            if word.startswith(digit):
                value = KLINGON_DIGITS[digit]
                suffix = word[len(digit):]
                if not suffix.strip():
                    return value
                multiplier = KLINGON_MULTIPLIERS.get(suffix)
                if multiplier is None:
                    raise ValueError(f"Invalid Klingon number suffix: {suffix}")
                return value * multiplier
        raise ValueError(f"Invalid Klingon number: {word}")

    try:        
        words = s.split(" ")
        value = 0
        powers = []
        last_value = 0
        for word in words:
            word_value = parse_word(word)
            if last_value and word_value > last_value or int(log(word_value, 10)) in powers:
                raise ValueError(f"Invalid combination of Klingon numbers: {word}")
            value += word_value
            last_value = word_value
        return value
    except ValueError:
        return None
        
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
    # Try CJK number (e.g. 十, 二十五, 一百)
    cjk_val = parse_cjk_number(s)
    if cjk_val is not None:
        return cjk_val
    # Try Klingon number (e.g. wa'SaD wejvatlh wejmaH Soch)
    klingon_val = parse_klingon_number(s)
    if klingon_val is not None:
        return klingon_val
    # Fallback to expression evaluation
    try:
        return evaluate_expression(s)
    except Exception:
        return None


def parse_roman(roman: str) -> int:
    digits = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    value = 0
    current = 0

    for c in roman:
        v = digits.get(c.upper())
        if v is None:
            raise ValueError("Invalid roman numeral")
        
        if current == 0:
            current = v
        elif v > current:
            value += v - current
            current = 0
        else:
            value += current
            current = v
    return value + current

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
        # check for Klingon number (multi-word token) before
        if c in "abcDegHIjlmnopqQrStuvwy'":
            j = i
            klingon_words = []
            while j < len(s):
                while j < len(s) and s[j].isspace():
                    j += 1
                if j >= len(s) or s[j] not in "abcDegHIjlmnopqQrStuvwy'":
                    break
                word_start = j
                while j < len(s) and s[j] not in " +-*/()^" and not s[j].isspace():
                    j += 1
                klingon_words.append(s[word_start:j])
            
            klingon_val = parse_klingon_number(" ".join(klingon_words))
            if klingon_val is not None:
                tokens.append(klingon_val)
                i = j
                continue
        # Functions, constants, roman numerals, CJK
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
            elif set(ident) <= set("IVXLCDMivxlcdm"):
                tokens.append(parse_roman(ident))
            elif (cjk_val := parse_cjk_number(ident)) is not None:
                tokens.append(cjk_val)   
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
            output.append(t)
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
        if xi > 1000:
            raise ValueError("factorial() argument too large")
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
        if isinstance(t, float) or isinstance(t, int):
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
                    if b > 1000:
                        raise ValueError("Exponent too large")
                    st.append(a**b)
            else:
                # unary function: pop one arg
                if len(st) < 1:
                    raise ValueError("Invalid expression")
                x = st.pop()
                if t not in funcs:
                    raise ValueError(f"Unknown function: {t}")
                st.append(funcs[t](x))
    if len(st) != 1:
        raise ValueError("Invalid expression")
    str(st[0])
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
