from table import Table
from tree import *

def evaluate(node, catalog: dict[str, Table]) -> Table:
    if isinstance(node, Relation):
        return catalog[node.name]          # look up the table

    if isinstance(node, Select):
        child = evaluate(node.input, catalog)
        kept = []
        for row in child.rows:
            if matches(node.cond, child.attributes, row):
                kept.append(row)
        return Table(attributes=child.attributes, rows=kept)
    raise ValueError(f"not implemented: {type(node)}")

def matches(cond, attrs: list[str], row: list) -> bool:
    if isinstance(cond, Compare):
        left = value_of(cond.left, attrs, row)
        right = value_of(cond.right, attrs, row)
        return compare(left, cond.op, right)

    #later im going to add stuff like AND, OR, NOT, etc.


def value_of(operand, attrs, row):
    if isinstance(operand, Num):
        return operand.value
    if isinstance(operand, Str):
        return operand.value   # may need to strip quotes later
    if isinstance(operand, Attr):
        i = attrs.index(operand.name)
        return row[i]

def compare(left, op, right):
    if op == "=":  return left == right
    if op == "!=": return left != right
    if op == "<":  return left < right
    if op == "<=": return left <= right
    if op == ">":  return left > right
    if op == ">=": return left >= right
    raise ValueError(op)

