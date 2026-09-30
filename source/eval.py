from table import Table
from tree import *

"""
Evaluate an RA AST against a catalog of Tables. (RA is Relational Algebra)
Pipeline: AST node -> recursively evaluate children -> return a Table.
Handles select/project/rename, set ops, product, and join (with column qualification).
"""

# thse counters are used to count the number of comparisons made during join and select operations
join_comparisons = 0
select_comparisons = 0

def reset_counters():
    global join_comparisons, select_comparisons
    join_comparisons = 0
    select_comparisons = 0

class EvalError(Exception):
    pass

def as_set(table: Table) -> set[tuple]:
    """Convert a Table to a set of tuples for set operations (union, intersect, minus, etc.)."""
    result = set()
    for row in table.rows:
        result.add(tuple(row))
    return result

def from_set(attrs: list[str], rows: set[tuple]) -> Table:
    """Convert a set of tuples to a Table."""
    result = []
    for row in rows:
        result.append(list(row))
    return Table(attributes=attrs, rows=result)

def same_schema(a: Table, b: Table) -> bool:
    """Check if two Tables have the same schema."""
    return a.attributes == b.attributes

def relation_label(node) -> str | None:
    """Name used to qualify columns for a join side."""
    # the reason only relation and rename are qualified is because they are the only nodes that can have a relation name
    if isinstance(node, Relation):
        return node.name
    if isinstance(node, Rename):
        return node.name
    return None  # already qualified / nested

def qualify(table: Table, name: str | None) -> Table:
    """Qualify the columns of a Table with a relation name."""
    if name is None:
        return table
    attrs = [f"{name}.{a.split('.')[-1]}" for a in table.attributes] # strips old rel.attr before re-prefixing
    return Table(attributes=attrs, rows=[list(r) for r in table.rows])

def normalize(v):
    """Normalize a value (remove quotes from strings)."""
    if isinstance(v, str) and len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v

def check_duplicate_attributes(attrs: list[str]):
    seen = set()
    for attr in attrs:
        if attr in seen:
            raise EvalError(f"schema, duplicate attribute {attr}")
        seen.add(attr)

def evaluate(node, catalog: dict[str, Table]) -> Table:
    global select_comparisons
    """Recursively evaluate AST; catalog maps relation name -> Table."""
    if isinstance(node, Relation):
        if node.name not in catalog:
            raise EvalError(f"name, unknown relation {node.name}")
        return catalog[node.name]

    if isinstance(node, Select):
        child = evaluate(node.input, catalog)
        kept = []
        for row in child.rows:
            select_comparisons += 1
            if matches(node.cond, child.attributes, row):
                kept.append(row)
        return Table(attributes=child.attributes, rows=kept)

    if isinstance(node, Project):
        seen = set() # check for duplicate attributes in the project list
        for attr in node.attrs:
            if attr in seen:
                raise EvalError(f"schema, duplicate attribute {attr}")
            seen.add(attr)

        child = evaluate(node.input, catalog)
        for attr in node.attrs:
            if attr not in child.attributes:
                raise EvalError(f"name, unknown attribute {attr}")
            if child.attributes.count(attr) > 1:
                raise EvalError(f"schema, duplicate attribute {attr}")

        indexes = [child.attributes.index(a) for a in node.attrs]
        rows = []
        seen = set() # check for duplicate rows in the projected table
        for row in child.rows:
            projected = [row[i] for i in indexes]
            key = tuple(projected)
            if key in seen:
                continue
            seen.add(key)
            rows.append(projected)
        return Table(attributes=list(node.attrs), rows=rows)

    if isinstance(node, Binary):
        left = evaluate(node.left, catalog)
        right = evaluate(node.right, catalog)
        if node.op == "join":
            left = qualify(left, relation_label(node.left))
            right = qualify(right, relation_label(node.right))
        return eval_binary(node.op, left, right, node.cond)

    if isinstance(node, Rename):
        child = evaluate(node.input, catalog)
        attrs = [f"{node.name}.{a.split('.')[-1]}" for a in child.attributes]
        check_duplicate_attributes(attrs)
        return Table(attributes=attrs, rows=list(child.rows))

    raise ValueError(f"not implemented: {type(node)}")

def eval_binary(op, left, right, cond):
    global join_comparisons
    """Run union/intersect/minus (same schema), times, or join with cond"""
    if op in ("union", "intersect", "minus"):
        if left.attributes != right.attributes:
            raise EvalError("schema, not union compatible")
        L, R = as_set(left), as_set(right)
        if op == "union":
            out = L | R
        elif op == "intersect":
            out = L & R
        else:  # minus
            out = L - R
        return Table(attributes=left.attributes, rows=[list(r) for r in out])

    if op == "times":
        attrs = left.attributes + right.attributes
        check_duplicate_attributes(attrs)
        rows = [l + r for l in left.rows for r in right.rows]
        return Table(attributes=attrs, rows=rows)
    if op == "join":
        if cond is None:
            raise EvalError("join requires a condition")
        attrs = left.attributes + right.attributes
        check_duplicate_attributes(attrs)
        rows = []
        for l in left.rows:
            for r in right.rows:
                join_comparisons += 1
                row = l + r
                if matches(cond, attrs, row):
                    rows.append(row)
        return Table(attributes=attrs, rows=rows)

    raise EvalError(f"not implemented: {op}")



def matches(cond, attrs: list[str], row: list) -> bool:
    """True if row satisfies condition AST (Compare/And/Or/Not)."""
    if isinstance(cond, Compare):
        left = value_of(cond.left, attrs, row)
        right = value_of(cond.right, attrs, row)
        return compare(left, cond.op, right)
    if isinstance(cond, And):
        return matches(cond.left, attrs, row) and matches(cond.right, attrs, row)
    if isinstance(cond, Or):
        return matches(cond.left, attrs, row) or matches(cond.right, attrs, row)
    if isinstance(cond, Not):
        return not matches(cond.cond, attrs, row)
    raise ValueError(f"not implemented: {type(cond)}")


def value_of(operand, attrs, row):
    if isinstance(operand, Num):
        return operand.value
    if isinstance(operand, Str):
        s = operand.value
        if len(s) >= 2 and s[0] == "'" and s[-1] == "'": #check if the string is wrapped in quotes
            s = s[1:-1].replace("''", "'") #replace double quotes with single quotes
        return s
    if isinstance(operand, Attr):
        key = f"{operand.relation}.{operand.name}" if operand.relation else operand.name # if the relation is not None, add the relation name to the attribute name
        count = attrs.count(key)
        if count == 0:
            raise EvalError(f"name, unknown attribute {key}")
        if count > 1:
            raise EvalError(f"schema, ambiguous attribute {key}")
        return row[attrs.index(key)]

    raise ValueError(f"not implemented: {type(operand)}")

def compare(left, op, right):
    left = normalize(left) #normalize to remove quotes from strings
    right = normalize(right)
    if op in ("<", "<=", ">", ">=") and type(left) is not type(right):
        # int vs str after norm (normalize to remove quotes from strings incase you missed the comment above)
        if isinstance(left, (int, float)) and isinstance(right, str) or \
           isinstance(right, (int, float)) and isinstance(left, str):
            raise EvalError("type, number compared to string")


    if op == "=":  return left == right
    if op == "!=": return left != right
    if op == "<":  return left < right
    if op == "<=": return left <= right
    if op == ">":  return left > right
    if op == ">=": return left >= right
    raise ValueError(op)

def format_result(table: Table) -> str:
    header = ", ".join(table.attributes)
    lines = [f"result ({header}) = {{"]
    for row in table.rows:
        cells = ", ".join(str(v) for v in row)
        lines.append(f"    {cells}")
    lines.append("}")
    return "\n".join(lines)

if __name__ == "__main__":
    from pathlib import Path
    from tokeniser import tokenise
    from parser import Parser
    from table import load_relation
    from eval import evaluate

    def normalize(text: str) -> str:
        return text.strip().replace("\r", "").replace("\n", "")

    ROOT = Path(__file__).resolve().parent.parent
    data = (ROOT / "tests" / "1" / "data.txt").read_text(encoding="utf-8")
    query = (ROOT / "tests" / "1" / "query.txt").read_text(encoding="utf-8")
    correct = (ROOT / "tests" / "1" / "result.txt").read_text(encoding="utf-8")
    catalog = load_relation(data)
    ast = Parser(tokenise(query)).parse()
    result = evaluate(ast, catalog)
    print(correct)
    print(format_result(result))
    if normalize(format_result(result)) == normalize(correct):
        print("Test passed")
    else:
        print("Test failed")
