from pathlib import Path
from tokeniser import tokenise
from parser import Parser
from table import load_relation
from eval import evaluate

ROOT = Path(__file__).resolve().parent.parent
data = (ROOT / "tests" / "1" / "data.txt").read_text(encoding="utf-8")
query = (ROOT / "tests" / "1" / "query.txt").read_text(encoding="utf-8")
catalog = load_relation(data)
ast = Parser(tokenise(query)).parse()
result = evaluate(ast, catalog)
print(result)