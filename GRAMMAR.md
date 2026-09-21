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

symbols = "!" | "#" | "$" | "%" | "&";

quoted_content = letter | number | " " | "''" | symbols;

string = "'" , { quoted_content } , "'";

relation_definition = relation_name , "(" , attribute_list , ")" , "=" , "{" { tuple_line } "}";

tuple_line = operand , { "," , operand };

letter = "A"|"B"|..."Z"|"a"|"b"...|"z";

number = ["-"], digit , {digit};

digit = "0"|"1"...|"9";

# 5.2:
- Precendence: By default I want to keep precedence as all equal
Precedence Table:
------------------------------------------------------------------------------
Level            Operator(s)                          Associativity   Notes
------------------------------------------------------------------------------
1                select,project,rename                n/a             associativity does not apply 
------------------------------------------------------------------------------
2                Union,intersect,minus,times,join     Left-to-right   

- Associativity: This I wanted to keep left-to-right as it is more intuitive and consistent with the way we read and write expressions.




# 5.3:


# 5.4:
My parsing strategy is to first tokenize the input, then parse the tokens into the AST nodes.
For more detial about my parsing strategy, I used recursive descent parsing, which is a top-down parsing technique that works by calling a function for each non-terminal in the grammar. I chose this because it is a simple and easy to understand parsing technique that is well suited for the grammar once it is proven to be a LL(1) grammar, which mine is since we dont need to look ahead more than one token to parse the input.

Left recursion is a problem that can occur when using recursive descent parsing. An example of left recursion is the following:
expression = expression , "+" , term;

Where since the expression is defined as itself plus a term, it will call the expression function again, causing an infinite loop.

To solve this I aimed to use repition operators to avoid left recursion. An example of this is the following:
expression = term , { "+" , term };

where if I wanted more than one term, I could just add more terms to the list, thus avoiding left recursion and allowing for more than one term.