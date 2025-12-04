from typing import Optional


def parse_message(content: str) -> Optional[int]:
    """
    Parse a numeric message content using canonical Python literal rules:
    - Supports optional `+`/`-` sign
    - Supports prefixes: `0b`/`0B` (binary), `0o`/`0O` (octal), `0x`/`0X` (hex)
    - Decimal numbers without prefix
    - Allows underscores for readability (e.g. 1_000)

    Returns the integer value, or None if parsing fails.
    """
    if content is None:
        return None
    s = content.strip()
    if not s:
        return None
    try:
        # int(x, 0) uses Python's canonical base detection with prefixes and sign.
        # It also accepts underscores in numeric literals.
        return int(s, 0)
    except Exception:
        return None


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
