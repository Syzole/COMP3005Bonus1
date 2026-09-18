from dataclasses import dataclass
from enum import Enum,auto

class TokenType(Enum):
    IDENTIFIER = auto() # A sequence of letters, digits, and underscores that does not start with a digit.
    NUMBER = auto() # number literal
    STRING = auto() # string literal
    LBRACKET = auto() # [
    RBRACKET = auto() # ]
    LPARENTHESIS = auto() # (
    RPARENTHESIS = auto() # )
    COMMA = auto() # ,
    DOT = auto() # .
    EQUALS = auto() # =
    NOT_EQUALS = auto() # !=
    LESS_THAN = auto() # <
    LESS_THAN_OR_EQUALS = auto() # <=
    GREATER_THAN = auto() # >
    GREATER_THAN_OR_EQUALS = auto() # >=
    EOF = auto() # End of file

@dataclass
class Token:
    type: TokenType
    value: str | int | None
    line: int
    column: int

class LexError(Exception):
    pass

def tokenise(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1

    def peek() -> str | None: # peek at the next char, if we're at the end of the source, return None
        if i >= len(source):
            return None
        return source[i]
    
    def next() -> str:
        nonlocal i, line, column
        char = source[i]
        i += 1
        if char == '\n':
            line += 1
            column = 1
        else:
            column += 1
        return char

    while i < len(source):
        start_line, start_column = line, column
        char = next()
        #now we start handling the different token types

