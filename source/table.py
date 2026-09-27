from dataclasses import dataclass
from tokeniser import tokenise, TokenType, Token
from tree import *

"""
In-memory relation storage and data.txt loader.
load_relation parses text like:
  Employees(Name, Age) = { 'Alice', 30 ... }
into dict[name] -> Table(attributes, rows).
"""

@dataclass
class Table:
    attributes: list[str]
    rows: list[list]


def load_relation(text: str) -> dict[str, Table]: #it acts lile Name(attributes) = { row1, row2, ... }
    tokens = tokenise(text)
    i = 0
    tables = {}

    def peek():
        return tokens[i]

    def next():
        nonlocal i
        t = tokens[i]
        i += 1
        return t

    def check(token_type, value=None):
        t = peek()
        if t.type != token_type:
            return False
        if value is not None and t.value != value:
            return False
        return True

    def expect(token_type, value=None):
        if not check(token_type, value):
            raise ValueError(f"Expected {token_type} but got {peek().type}")
        return next()

    def read_value():
        if check(TokenType.NUMBER):
            return int(next().value)  

        if check(TokenType.STRING):
            return next().value

        if check(TokenType.IDENTIFIER):
            return next().value
        raise ValueError(f"Expected a value but got {peek().type}")

    while not check(TokenType.EOF):
        name = expect(TokenType.IDENTIFIER).value
        expect(TokenType.LPARENTHESIS)
        attributes = [expect(TokenType.IDENTIFIER).value]
        while check(TokenType.COMMA):
            next()
            attributes.append(expect(TokenType.IDENTIFIER).value)
        expect(TokenType.RPARENTHESIS)
        expect(TokenType.EQUALS)
        expect(TokenType.LBRACE)

        rows = []
        while not check(TokenType.RBRACE):
            # we read one tuple line at a time
            row = [read_value()]
            while check(TokenType.COMMA):
                next()
                row.append(read_value())
            rows.append(row)
        
        expect(TokenType.RBRACE)
        tables[name] = Table(attributes, rows)
    return tables

