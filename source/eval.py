from table import Table
from tree import *

class EvalError(Exception):
    pass

def as_set(table: Table) -> set[tuple]:
    result = set()
    for row in table.rows:
        result.add(tuple(row))
    return result

def from_set(attrs: list[str], rows: set[tuple]) -> Table:
    result = []
    for row in rows:
        result.append(list(row))
    return Table(attributes=attrs, rows=result)

def same_schema(a: Table, b: Table) -> bool:
    return a.attributes == b.attributes

def relation_label(node) -> str | None:
    """Name used to qualify columns for a join side."""
    if isinstance(node, Relation):
        return node.name
    if isinstance(node, Rename):
        return node.name
    return None  # already qualified / nested

def qualify(table: Table, name: str | None) -> Table:
    if name is None:
        return table
    attrs = [f"{name}.{a.split('.')[-1]}" for a in table.attributes]
    return Table(attributes=attrs, rows=[list(r) for r in table.rows])

def normalize(v):
    if isinstance(v, str) and len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v

def evaluate(node, catalog: dict[str, Table]) -> Table:
    if isinstance(node, Relation):
        if node.name not in catalog:
            raise EvalError(f"name, unknown relation {node.name}")
        return catalog[node.name]    

    if isinstance(node, Select):
        child = evaluate(node.input, catalog)
        kept = []
        for row in child.rows:
            if matches(node.cond, child.attributes, row):
                kept.append(row)
        return Table(attributes=child.attributes, rows=kept)

    if isinstance(node, Project):
        seen = set()
        for attr in node.attrs:
            if attr in seen:
                raise EvalError(f"schema, duplicate attribute {attr}")
            seen.add(attr)

        child = evaluate(node.input, catalog)
        for attr in node.attrs:
            if attr not in child.attributes:
                raise EvalError(f"name, unknown attribute {attr}")
        indexes = [child.attributes.index(a) for a in node.attrs]
        rows = []
        seen = set()
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
        return Table(attributes=attrs, rows=list(child.rows))

    raise ValueError(f"not implemented: {type(node)}")

def eval_binary(op, left, right, cond):
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
        rows = [l + r for l in left.rows for r in right.rows]
        return Table(attributes=attrs, rows=rows)
    if op == "join":
        if cond is None:
            raise EvalError("join requires a condition")
        attrs = left.attributes + right.attributes
        rows = []
        for l in left.rows:
            for r in right.rows:
                row = l + r
                if matches(cond, attrs, row):
                    rows.append(row)
        return Table(attributes=attrs, rows=rows)
    
    raise EvalError(f"not implemented: {op}")
    


def matches(cond, attrs: list[str], row: list) -> bool:
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
        key = f"{operand.relation}.{operand.name}" if operand.relation else operand.name
        if key not in attrs:
            raise EvalError(f"name, unknown attribute {key}")
        return row[attrs.index(key)]

    raise ValueError(f"not implemented: {type(operand)}")

def compare(left, op, right):
    left = normalize(left)
    right = normalize(right)
    if op in ("<", "<=", ">", ">=") and type(left) is not type(right):
        # int vs str after norm
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
