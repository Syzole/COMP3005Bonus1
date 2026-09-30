Link to video: https://youtu.be/4d4Wnx43oi8?si=TdE6OYp_06ME8-Om

# How to run
Python 3.13. The program uses only the standard library.


# How to use

first cd into source folder and run the following command:

```
python source/ra.py "project[Name](select[Age>30](Employees))"
```

That command uses tests/data/Employees.txt when you do not pass a data file. Point --data at another relation file when you need one:
```
python source/ra.py "project[Name](Emp)" --data tests/1/data.txt
```

Print the query tree instead of running it:

```
python source/ra.py --tree "A union B minus C"
```
Run the test suite from the project root:

```
python source/test_eval.py
python source/test_eval.py 14
python source/test_eval.py 10 15
```
A data file is one or more relations in this form:

Employees (EID, Name, Age, DID) = {
    E1, 'John.', 32, D1
    E2, Alice, 28, D2
    E3, Bob, 29, D1
}

Numbers are integers. Text values are either a bare name (E1, Alice) or a single-quoted string ('John.'). A quote inside a string is written as ''.

# What is supported
Unary operators:

select[condition](expression) keeps the rows that satisfy the condition.
project[Attr, Attr](expression) keeps the named columns and drops duplicate rows.
rename[NewName](expression) prefixes every column with NewName..
Binary operators, all at the same precedence and associating left to right:

union, intersect, and minus require both sides to have the same attribute list.
times is the Cartesian product.
join[condition] is a nested-loop theta join. Each side that is a relation name or a rename has its columns prefixed with that name, so a condition can use Emp.EID.
Conditions support =, !=, <, <=, >, >=, plus and, or, and not. Precedence inside a condition is not, then and, then or. Parentheses group both queries and conditions.

Names are a letter followed by letters and digits. A qualified name is Relation.Attribute.

# Why a self-join needs rename
rename[E2](Emp) join[Emp.MgrID=E2.EID] Emp

The reason this needs a rename is without rename, the attempt at a self-join will fail because the join condition will not be able to distinguish between the two copies of the Emp relation.

Resulting in a schema like:
result (Emp.EID, Emp.Name, Emp.MgrID, Emp.EID, Emp.Name, Emp.MgrID) = {
    E1, Pat, E1, E1, Pat, E1
    E1, Pat, E1, E2, John, E1
    E1, Pat, E1, E3, Alice, E2
}

This would produce an error because the attribute EID is duplicated. Thus the rename is necessary to distinguish between the two copies of the Emp relation, and allow for a proper join, or in this case, a self-join.


# Known limitations
Numbers are integers only. The scanner reads an optional minus and then digits, and the loader stores that text with int. A decimal point is a separate dot token, so a float such as 3.14 is not a number.
Names cannot contain underscores or other symbols.
Keywords (select, project, rename, union, intersect, minus, times, join, and, or, not) are lowercase.
union, intersect, and minus compare attribute lists for equality, including order. The result rows come from a Python set, so their order is not fixed.
Join qualifies columns only when that side is a plain relation or a rename. A nested expression on a join side keeps whatever column names it already has.
There is no division operator, aggregation, sorting, or outer join.
Join compares every row of the left input with every row of the right input, so its cost grows with the product of the two sizes.
