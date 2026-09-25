import argparse
from tokeniser import tokenise, LexError
from parser import Parser, ParseError
from tree import format_tree
from eval import format_result, evaluate
from table import load_relation
from pathlib import Path


def main():
    arg_parse = argparse.ArgumentParser(description="Query language for relational databases")
    arg_parse.add_argument(
        "--tree",
        action="store_true",
        help="print the AST of the query instead of executing it"
    )
    arg_parse.add_argument(
        "query",
        help='query string, e.g. \'project[Name](select[Age>30](Employees))\'',
    )
    arg_parse.add_argument(
        "--data",
        help="path to a data.txt / relation file",
        default="tests/data/Employees.txt",
    )
    args = arg_parse.parse_args()

    try:
        tokens = tokenise(args.query)
        ast = Parser(tokens).parse()
    except LexError as e:
        print(f"Lexical error: {e}")
        return
    except ParseError as e:
        print(f"Parse error: {e}")
        return
    
    if args.tree:
        print(format_tree(ast))
        return
    
    
    data_path = Path(args.data)
    if not data_path.is_file():
        ROOT = Path(__file__).resolve().parent.parent
        data_path = ROOT / "tests" / "data" / "Employees.txt"

    catalog = load_relation(data_path.read_text(encoding="utf-8"))

    #if we get this far, we can evaluate the query
    # print("args.query", args.query)
    result = evaluate(ast, catalog)
    print(format_result(result))


if __name__ == "__main__":
    main()