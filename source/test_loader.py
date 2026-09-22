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


TEST_NUMBER = 2

case = load_test(TEST_NUMBER)
print(f"test {case.number}")
print(case.data.text, end="" if case.data.text.endswith("\n") else "\n")
print(case.query.text, end="" if case.query.text.endswith("\n") else "\n")
print(format_tree(Parser(tokenise(case.query.text)).parse()))
