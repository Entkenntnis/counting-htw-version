import sys
from parser import parse_message, evaluate_expression


def check(name, got, expected):
    ok = got == expected
    print(f"{'OK' if ok else 'FAIL'}: {name}: got={got!r} expected={expected!r}")
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
    failures += 0 if check("expr division round", parse_message("3/2"), 2) else 1
    failures += 0 if check("expr with hex/bin", parse_message("0x10 + 0b11"), 19) else 1

    # evaluate_expression directly
    failures += 0 if check("eval sqrt", evaluate_expression("sqrt(9)"), 3) else 1
    failures += 0 if check("eval fac", evaluate_expression("fac(5)"), 120) else 1
    failures += (
        0 if check("eval factorial", evaluate_expression("factorial(4)"), 24) else 1
    )

    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print("\nAll tests passed")


if __name__ == "__main__":
    main()
