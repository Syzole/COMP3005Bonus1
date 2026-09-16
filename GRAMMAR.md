# 5.1
EBNF Grammar:

expression = term , {binary_op, term};

binary_op = "union" | "intersect" | "minus" | "times" | "join", "[" , condition , "]";

term = unary_expr | relation_name | "(" , expression , ")";

relation_name = bare_string;

unary_expr = select_expr | project_expr | rename_expr;

select_expr = "select" , "[" , condition , "]" , "(" , expression , ")";

project_expr = "project" , "[" , attribute_list , "]" , "(" , expression , ")";

attribute_list = bare_string , {"," , bare_string};

rename_expr = "rename" , "[" ,relation_name , "]" , "(" , expression , ")";

condition = or_condition;
or_condition = and_condition , { "or" , and_condition };
and_condition = not_condition , { "and" , not_condition };
not_condition = "not" , not_condition | "(" , condition , ")" | comparison ;

comparison = operand , comparison_op , operand;

comparison_op = "=" | "!=" | "<" | "<=" | ">" | ">=";

operand = string | number | qual_name |bare_string;

bare_string = letter , { letter | number };

qual_name = bare_string ,".", bare_string

symbols = "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | "<" | "=" | ">" | "?" | "@" | "[" | "]" | "^" | "_" | "`" | "{" | "|" | "}" | "~";

quoted_content = letter | number | " " | "''" | symbols;

string = "'" , { quoted_content } , "'";

relation_definition = relation_name , "(" , attribute_list , ")" , "=" , "{" { tuple_line } "}";

tuple_line = operand , { "," , operand };

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" |
  "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z";

number = ["-"], digit , {digit};

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";

# 5.2:
- Precendence: By default I want to keep precedence as all equal
Precedence Table:
------------------------------------------------------------------------------
Level            Operator(s)                          Associativity   Notes
------------------------------------------------------------------------------
1(Highest)       select,project,rename                n/a             associativity does not apply to them since they can only take one input at a time
------------------------------------------------------------------------------
2                Union,intersect,minus,times,join     Left-to-right   

- Associativity: This I wanted to keep left-to-right as it is more intuitive and consistent with the way we read and write expressions.
