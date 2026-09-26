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
    LBRACE = auto() # {
    RBRACE = auto() # }

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
    
    #next is a function that returns the next character and updates the line and column
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

    #here is where we will start the breakign down of the query
    # and we will start to break them down into tokens

    while i < len(source):
        start_line = line
        start_column = column
        char = next()

        #now we start handling the different token types
        
        
        #first handle whitespace by doing nothing
        if char.isspace():
            continue

        if char in "\t\n\r":
            next()
            continue

        #now if we deal with strings
        # i had the idea of using booleans to check if the string is escaped or not
        # but i decided to use a while loop instead, cause it seemed easier
        if char == "'":
            text = char
            while True:
                p = peek()
                if p is None:
                    raise LexError("string never closed")


                #handle the escape here 
                if p == "'":
                    text += next()
                    if peek() == "'":
                        text += next()
                        continue
                    break
                text += next()
            tokens.append(Token(TokenType.STRING, text, start_line, start_column))
            continue


        #this would be an identifier, a letter then either more letters, digits, or underscores
        if char.isalpha():
            text = char
            while (p := peek()) is not None and p.isalnum():
                text += next()
            tokens.append(Token(TokenType.IDENTIFIER, text, start_line, start_column))
            continue


        #handle the negative sign
        if char == "-" and (p := peek()) is not None and p.isdigit():
            text = char + next() #consume the '-' and attach the next digit to it
            while (p := peek()) is not None and p.isdigit():
                text += next()
            tokens.append(Token(TokenType.NUMBER, text, start_line, start_column))
            continue

        #next hanlde if it is a number
        if char.isdigit():
            text = char
            while (p := peek()) is not None and p.isdigit():
                text += next()
            tokens.append(Token(TokenType.NUMBER, text, start_line, start_column))
            continue

        #im very confident that the 2 if statments will not work for all cases, so i will adjust as needed

        #first draft of handling the funny parts like [](), im confident that this will work for all cases
        match (char, peek()):
            # 2-character operators (checks peek() without advancing i unless matched)
            case ("!", "="):
                next() # consume the '='
                tokens.append(Token(TokenType.NOT_EQUALS, None, start_line, start_column))
            case ("<", "="):
                next()
                tokens.append(Token(TokenType.LESS_THAN_OR_EQUALS, None, start_line, start_column))
            case (">", "="):
                next()
                tokens.append(Token(TokenType.GREATER_THAN_OR_EQUALS, None, start_line, start_column))

            # 1-character operators / structural symbols
            case ("[", _):
                tokens.append(Token(TokenType.LBRACKET, None, start_line, start_column))
            case ("]", _):
                tokens.append(Token(TokenType.RBRACKET, None, start_line, start_column))
            case ("(", _):
                tokens.append(Token(TokenType.LPARENTHESIS, None, start_line, start_column))
            case (")", _):
                tokens.append(Token(TokenType.RPARENTHESIS, None, start_line, start_column))
            case ("=", _):
                tokens.append(Token(TokenType.EQUALS, None, start_line, start_column))
            case ("<", _):
                tokens.append(Token(TokenType.LESS_THAN, None, start_line, start_column))
            case (">", _):
                tokens.append(Token(TokenType.GREATER_THAN, None, start_line, start_column))
            case (",", _):
                tokens.append(Token(TokenType.COMMA, None, start_line, start_column))
            case (".", _):
                tokens.append(Token(TokenType.DOT, None, start_line, start_column))
            case ("{", _):
                tokens.append(Token(TokenType.LBRACE, None, start_line, start_column))
            case ("}", _):
                tokens.append(Token(TokenType.RBRACE, None, start_line, start_column))



    
    tokens.append(Token(TokenType.EOF, None, line, column))
    return tokens


def dump_tokens(tokens: list[Token]) -> None:
    for t in tokens:
        pos = f"{t.line}:{t.column}"
        kind = t.type.name
        value = "" if t.value is None else repr(t.value)
        print(f"  {pos:<7} {kind:<24} {value}")




#this is me running some small tests on the tokeniser, making sure it splits as expected
if __name__ == "__main__":
    from pathlib import Path

    tests = Path(__file__).resolve().parent.parent / "tests"
    first, last = 19,19  # change this range as you go

    for n in range(first, last + 1):
        query = (tests / str(n) / "query.txt").read_text(encoding="utf-8")
        print(f"=== test {n} ===")
        print(f"query: {query.rstrip()}")
        try:
            dump_tokens(tokenise(query))
        except LexError as e:
            print(f"  ERROR: {e}")
        print()