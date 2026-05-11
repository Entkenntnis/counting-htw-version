import sys
from parser import parse_message, evaluate_expression


def check(name, got, expected):
    ok = got == expected
    print(f"\033[1m{'\033[32mOK' if ok else '\033[31mFAIL'}\033[0m: {name}: got={got!r} expected={expected!r}")
    return ok


def main():
    failures = 0
    # parse_message literals
    failures += 0 if check("literal dec", parse_message("123"), 123) else 1
    failures += 0 if check("literal hex", parse_message("0xFF"), 255) else 1
    failures += 0 if check("literal bin", parse_message("0b1010"), 10) else 1
    failures += 0 if check("literal oct", parse_message("0o77"), 63) else 1
    failures += 0 if check("literal underscores", parse_message("1_000"), 1000) else 1
    failures += 0 if check("literal negative", parse_message("-42"), -42) else 1
    failures += 0 if check("invalid literal", parse_message("abc"), None) else 1

    # parse_message expressions
    failures += 0 if check("expr simple", parse_message("1+2*3"), 7) else 1
    failures += 0 if check("expr paren", parse_message("(1+2)*3"), 9) else 1
    failures += 0 if check("expr unary", parse_message("-(-1)"), 1) else 1
    failures += 0 if check("expr division round", parse_message("3/2"), 1.5) else 1
    failures += 0 if check("expr with hex/bin", parse_message("0x10 + 0b11"), 19) else 1

    # evaluate_expression directly
    failures += 0 if check("eval sqrt", evaluate_expression("sqrt(9)"), 3) else 1
    failures += 0 if check("eval fac", evaluate_expression("fac(5)"), 120) else 1
    failures += (
        0 if check("eval factorial", evaluate_expression("factorial(4)"), 24) else 1
    )

    # CJK numbers (十=10, 二十五=25, 一百=100, etc.)
    failures += 0 if check("CJK 10", parse_message("\u5341"), 10) else 1
    failures += 0 if check("CJK 25", parse_message("\u4e8c\u5341\u4e94"), 25) else 1
    failures += 0 if check("CJK 100", parse_message("\u4e00\u767e"), 100) else 1
    failures += 0 if check("CJK 1200", parse_message("\u4e00\u5343\u4e8c\u767e"), 1200) else 1
    failures += 0 if check("CJK expr 10+5", parse_message("\u5341+\u4e94"), 15) else 1

    # Klingon numbers
    failures += 0 if check("tlh 1", parse_message("wa'"), 1) else 1
    failures += 0 if check("tlh 10", parse_message("wa'maH"), 10) else 1
    failures += 0 if check("tlh 42", parse_message("loSmaH cha'"), 42) else 1
    failures += 0 if check("tlh 1337", parse_message("wa'SaD wejvatlh wejmaH Soch"), 1337) else 1
    failures += 0 if check("tlh sanid", parse_message("wa'SanID"), 1000) else 1
    failures += 0 if check("tlh wrong order", parse_message("cha' loSmaH"), None) else 1
    failures += 0 if check("tlh same power", parse_message("jav Soch"), None) else 1
    failures += 0 if check("tlh math", parse_message("wa'SaD + wejvatlh wejmaH Soch"), 1337) else 1

    # Roman numerals
    failures += 0 if check("roman 1", parse_message("I"), 1) else 1
    failures += 0 if check("roman 10", parse_message("X"), 10) else 1
    failures += 0 if check("roman 25", parse_message("XXV"), 25) else 1
    failures += 0 if check("roman 40", parse_message("XL"), 40) else 1
    failures += 0 if check("roman 1337", parse_message("MCCCXXXVII"), 1337) else 1
    failures += 0 if check("roman 999", parse_message("IM"), 999) else 1

    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print("\nAll tests passed")


if __name__ == "__main__":
    main()
