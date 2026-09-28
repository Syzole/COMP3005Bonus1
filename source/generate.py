"""
Generate relation files R(a, b) and S(b, c) with controllable size and match rate.

Match rate m ≈ how many S tuples each R tuple joins with on b.
Usage:
  python generate.py --n 1000 --match 1 --out data.txt
  python generate.py --r 1000 --s 5000 --match 3 --out data.txt
  python generate.py --experiment   # 8.3: run join at each size, print join counter
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
import time

def write_relation(name: str, attrs: list[str], rows: list[list], f) -> None:
    f.write(f"{name}({', '.join(attrs)}) = {{\n")
    for row in rows:
        f.write("    " + ", ".join(str(v) for v in row) + "\n")
    f.write("}\n")


def generate_relations(
    n_r: int,
    n_s: int,
    match: int,
    seed: int | None = None,
) -> tuple[list[list], list[list]]:
    """
    R(a,b): unique join keys b = 0..n_r-1
    S(b,c): ~match copies of each R key, then non-matching fillers to reach n_s
    """
    if n_r < 0 or n_s < 0:
        raise ValueError("tuple counts must be non-negative")
    if match < 0:
        raise ValueError("match rate must be non-negative")

    needed = n_r * match
    if n_r > 0 and needed > n_s:
        # clamp so we still fit in |S|
        match = n_s // n_r
        needed = n_r * match
        print(
            f"warning: match rate clamped to {match} "
            f"(need {n_r * (match + 1)} S slots for higher rate)",
            file=sys.stderr,
        )

    rng = random.Random(seed)

    r_rows = [[i, i] for i in range(n_r)]

    s_rows: list[list] = []
    c = 0
    for b in range(n_r):
        for _ in range(match):
            s_rows.append([b, c])
            c += 1

    # fillers: keys that never appear in R
    while len(s_rows) < n_s:
        s_rows.append([n_r + (c - needed), c])
        c += 1

    rng.shuffle(r_rows)
    rng.shuffle(s_rows)
    return r_rows, s_rows


def write_file(path: Path, r_rows: list[list], s_rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        write_relation("R", ["a", "b"], r_rows, f)
        f.write("\n")
        write_relation("S", ["b", "c"], s_rows, f)


def run_experiment(match: int, seed: int | None, out_dir: Path) -> None:
    """8.3: R join[R.b=S.b] S at each size; print measured join comparisons."""
    # counters live in eval — must exist before this works
    from tokeniser import tokenise
    from parser import Parser
    from table import load_relation
    from eval import evaluate, reset_counters, join_comparisons

    sizes = [1000, 2000, 4000, 8000, 16000, 32000, 64000]
    query = "R join[R.b=S.b] S"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(
        f"{'n':>8}  {'m':>4}  {'comparisons':>16}  "
        f"{'wall time (s)':>14}  {'output tuples':>14}"
    )
    for n in sizes:
        path = out_dir / f"r{n}.txt"
        r_rows, s_rows = generate_relations(n, n, match, seed=seed)
        write_file(path, r_rows, s_rows)

        reset_counters()
        catalog = load_relation(path.read_text(encoding="utf-8"))
        ast = Parser(tokenise(query)).parse()
        
        t0 = time.perf_counter()
        result = evaluate(ast, catalog)
        elapsed = time.perf_counter() - t0
        print(
            f"{n:>8}  {match:>4}  {join_comparisons:>16}  "
            f"{elapsed:>14.4f}  {len(result.rows):>14}"
        )



def main() -> None:
    p = argparse.ArgumentParser(description="Generate R(a,b) and S(b,c) relation files")
    p.add_argument("--n", type=int, help="tuples in both R and S")
    p.add_argument("--r", type=int, help="tuples in R (overrides --n for R)")
    p.add_argument("--s", type=int, help="tuples in S (overrides --n for S)")
    p.add_argument("--match", type=int, default=1, help="S matches per R tuple (default 1)")
    p.add_argument("--out", type=Path, default=Path("data.txt"), help="output path")
    p.add_argument("--seed", type=int, default=0, help="RNG seed")
    p.add_argument(
        "--experiment",
        action="store_true",
        help="run 8.3 join sizes and print join comparison counts",
    )
    p.add_argument(
        "--exp-dir",
        type=Path,
        default=Path("/tmp/bonus_join_exp"),
        help="directory for experiment data files",
    )
    args = p.parse_args()

    if args.experiment:
        run_experiment(match=args.match, seed=args.seed, out_dir=args.exp_dir)
        return

    n_r = args.r if args.r is not None else args.n
    n_s = args.s if args.s is not None else args.n
    if n_r is None or n_s is None:
        p.error("provide --n, or both --r and --s (or use --experiment)")

    r_rows, s_rows = generate_relations(n_r, n_s, args.match, seed=args.seed)
    write_file(args.out, r_rows, s_rows)
    print(f"wrote |R|={n_r}, |S|={n_s}, match≈{args.match} -> {args.out}")


if __name__ == "__main__":
    main()