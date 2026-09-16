# 5.1

(Using Standard EBNF)
EBNF Grammar:
query = expression;

expression = term , {binary_op};

term = unary_op | relation_name | "(" , expression , ")";

unary_op = select_expr | project_expr | rename_expr;

relation_name = letter , {letter | digit};

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" |"Z" 
|"a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" ;

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;


string_char = letter | digit | " " | "_";

string = "'" , {string_char} , "'";


Im so tired im gonna go to sleep, tomorrow i will continue this.