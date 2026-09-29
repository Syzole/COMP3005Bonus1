import time
from pathlib import Path
from tokeniser import tokenise
from parser import Parser
import eval as ev
from table import load_relation
for m in [0,1,2]:
    path = Path(f'../exp_data/match{m}.txt')
    catalog = load_relation(path.read_text(encoding='utf-8'))
    ev.reset_counters()
    ast = Parser(tokenise('R join[R.b=S.b] S')).parse()
    t0 = time.perf_counter()
    result = ev.evaluate(ast, catalog)
    t = time.perf_counter() - t0
    print(f'match={m}  comps={ev.join_comparisons}  time={t:.4f}  out={len(result.rows)}')


