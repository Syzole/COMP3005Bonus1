from dataclasses import dataclass

"""
AST nodes for the query tree, this is what the parser will take after the tokenizer
Each class maps to someting in the EBNF grammar
The parser builds these and the tree will walk them to get the query plan
"""


#base relation node
@dataclass
class Relation:
    """relation[name] -> relation_expr"""
    name: str

#project node that lists the attributes to project
@dataclass
class Project:
    """project[attributes](input) -> project_expr"""
    attrs: list[str]
    input: object   # another expr node

#select node that lists the condition to select
@dataclass
class Select:
    """select[condition](input) -> select_expr"""
    cond: object
    input: object


#rename node that renames the relation
@dataclass
class Rename:
    """rename[name](input) -> rename_expr"""
    name: str
    input: object


#binary node that says what two relations to combine
@dataclass
class Binary:
    """binary[op](union, intersect, minus, join, times)(expr) -> binary_expr"""
    op: str   # union, minus, join, ...
    left: object
    right: object
    cond: object | None = None  # only for join


#compare node that says what two attributes to compare
@dataclass
class Compare:
    op: str # <, >, =, <=, >=, !=
    left: object
    right: object

#attr node that says what attribute to project
@dataclass
class Attr:
    """Attribute: Name, or EMP.DID when relation is set"""
    name: str
    relation: str | None = None  # Emp.DID → relation="Emp", name="DID"

#everything below here is simple nodes that are just values or conditions

@dataclass
class Num:
    value: int

@dataclass
class Str:
    value: str

@dataclass
class Not:
    cond: object

@dataclass
class And:
    left: object
    right: object

@dataclass
class Or:
    left: object
    right: object

#below here is the logic for formatting the tree since parser splits it up into these nodes
def format_operand(node) -> str:
    """
    Take Attr or Num or Strings, and return a string representation of the value
    Emp.DID -> 'Emp.DID', Age -> 'Age', 30 -> '30'
    """
    if isinstance(node, Attr):
        return f"{node.relation}.{node.name}" if node.relation else node.name
    elif isinstance(node, Num):
        return str(node.value)
    elif isinstance(node, Str):
        return node.value
    return str(node)

def format_condition(node) -> str:
    """
    Take a condition AST and flatten it into a string using recursion if its And or Or or Not
    if its a Compare, just format the operands
    """
    if isinstance(node, Compare):
        return f"{format_operand(node.left)} {node.op} {format_operand(node.right)}"
    elif isinstance(node, And):
        return f"{format_condition(node.left)} and {format_condition(node.right)}"
    elif isinstance(node, Or):
        return f"{format_condition(node.left)} or {format_condition(node.right)}"
    elif isinstance(node, Not):
        return f"not {format_condition(node.cond)}"
    return str(node)

def format_tree(node) -> str:
    return "\n".join(walk_tree(node, prefix="", is_last=True, is_root=True))

def label_and_children(node) -> tuple[str, list[object]]:
    """
    Return (title, children) for printing the tree in a clean format
    chilldren is a list of (field_lablel, child_node):
        - child_node is None, then text-only field such as attrs, cond, name
        - child_node is a node, then we use recursion under that field (input, left, right)
    """
    if isinstance(node, Relation):
        return node.name, []

    elif isinstance(node, Project):
        return "Project", [
            (f"attrs: {', '.join(node.attrs)}", None),
            ("input", node.input),
        ]

    elif isinstance(node, Select):
        return "Select", [
            ("cond", node.cond),   # recurse
            ("input", node.input),
        ]

    
    elif isinstance(node, Compare):
        return f"{format_operand(node.left)} {node.op} {format_operand(node.right)}", []
    elif isinstance(node, And):
        return "And", [("left", node.left), ("right", node.right)]
    elif isinstance(node, Or):
        return "Or", [("left", node.left), ("right", node.right)]
    elif isinstance(node, Not):
        return "Not", [("cond", node.cond)]

    elif isinstance(node, Rename):
        return "Rename", [
            (f"name: {node.name}", None),
            ("input", node.input),
        ]
        
    elif isinstance(node, Binary):
        children = []
        if node.cond is not None:
            children.append((f"cond: {format_condition(node.cond)}", None))
        children.append(("left", node.left))
        children.append(("right", node.right))
        return node.op.capitalize(), children

    return repr(node), []

def walk_tree(node, prefix: str, is_last: bool, is_root: bool) -> list[str]:
    """
    Build the clean print lines for this node and its children

    prefix - indentation | guides from parents to this node
    is_last - True if this is the last child of its parent, mainly for the tree connector
    is_root - True if this is the root node, mainly for the tree connector and removing the └── line
    returns list of strings to print each line of the tree
    """
    label, children = label_and_children(node)
    if is_root:
        lines = [label]
    else:
        branch = "└── " if is_last else "├── "
        lines = [prefix + branch + label]
        prefix = prefix + ("    " if is_last else "│   ")
    for i, (child_label, child_node) in enumerate(children):
        last = i == len(children) - 1
        branch = "└── " if last else "├── "
        lines.append(prefix + branch + child_label)
        if child_node is None:
            continue  # attrs / cond — done
        next_prefix = prefix + ("    " if last else "│   ")
        # walk the AST node; force non-root so it gets a connector under "input"
        sub = walk_tree(child_node, next_prefix, True, False)
        lines.extend(sub)
    return lines
