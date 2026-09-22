import argparse
from tokeniser import tokenise, LexError
from parser import Parser, ParseError
from tree import format_tree



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

    print("Please wait for exections to be a thing")


if __name__ == "__main__":
    main()