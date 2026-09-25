from pathlib import Path
from tokeniser import tokenise, LexError
from parser import Parser, ParseError
from table import load_relation
from eval import evaluate, format_result, EvalError

ROOT = Path(__file__).resolve().parent.parent


def normalize(text: str) -> str:
    """Ignore newlines/spaces so indent differences don't fail tests."""
    return "".join(text.split())


def run_case(n: int) -> str:
    """Return what the program should print for this test (result or error line)."""
    folder = ROOT / "tests" / str(n)
    data = (folder / "data.txt").read_text(encoding="utf-8")
    query = (folder / "query.txt").read_text(encoding="utf-8")

    try:
        catalog = load_relation(data)
        ast = Parser(tokenise(query)).parse()
        return format_result(evaluate(ast, catalog))
    except LexError as e:
        return f"error: lexical, {e}"
    except ParseError as e:
        return f"error: syntax, {e}"
    except EvalError as e:
        return f"error: {e}"


def test_one(n: int, verbose: bool = False) -> bool:
    answer = (ROOT / "tests" / str(n) / "result.txt").read_text(encoding="utf-8")
    got = run_case(n)
    ok = normalize(got) == normalize(answer)

    status = "PASS" if ok else "FAIL"
    print(f"test {n:>2}: {status}")

    if not ok or verbose:
        print("  got:")
        print(got)
        print("  expected:")
        print(answer.rstrip())
        print()
    return ok


if __name__ == "__main__":
    import sys

    # Usage:
    #   python test_eval.py           -> all 1..25
    #   python test_eval.py 14        -> one test
    #   python test_eval.py 10 15     -> range 10..15
    #   python test_eval.py -v 5      -> verbose (always show got/expected)

    args = [a for a in sys.argv[1:] if a != "-v"]
    verbose = "-v" in sys.argv[1:]

    if len(args) == 0:
        start, end = 1, 25
    elif len(args) == 1:
        start = end = int(args[0])
    else:
        start, end = int(args[0]), int(args[1])

    passed = 0
    failed = []
    for n in range(start, end + 1):
        if test_one(n, verbose=verbose):
            passed += 1
        else:
            failed.append(n)

    total = end - start + 1
    print(f"\n{passed}/{total} passed")
    if failed:
        print("failed:", failed)