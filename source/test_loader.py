#this file was used to test the loader and the tree formatter

from dataclasses import dataclass
from pathlib import Path
from tokeniser import tokenise
from parser import Parser, ParseError
from tree import format_tree

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"

@dataclass
class Source:
    path: str
    text: str

@dataclass
class TestCase:
    number: int
    data: Source
    query: Source

def load_test(number: int) -> TestCase:
    folder = TESTS / str(number)
    return TestCase(
        number=number,
        data=_read(folder / "data.txt"),
        query=_read(folder / "query.txt"),
    )

def _read(path: Path) -> Source:
    text = path.read_text(encoding="utf-8")
    return Source(path=str(path), text=text)


TEST_NUMBER = 10,11

for test_number in range(TEST_NUMBER[0], TEST_NUMBER[1] + 1):
    try:
        case = load_test(test_number)
        print(f"test {case.number}")
    except Exception as e:
        print(f"test {test_number} failed: {e}")
        continue
    try:
        # print(case.data.text, end="" if case.data.text.endswith("\n") else "\n")
        print(case.query.text, end="" if case.query.text.endswith("\n") else "\n")
        print(format_tree(Parser(tokenise(case.query.text)).parse()))
    except Exception as e:
        print(f"test {test_number} failed: {e}")
