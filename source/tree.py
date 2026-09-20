from dataclasses import dataclass

#All of the nodes in the AST

#i mean it it should not be to hard to read what each part is

#base relation node
@dataclass
class Relation:
    name: str

#project node that lists the attributes to project
@dataclass
class Project:
    attrs: list[str]
    input: object   # another expr node

#select node that lists the condition to select
@dataclass
class Select:
    cond: object
    input: object


#rename node that renames the relation
@dataclass
class Rename:
    name: str
    input: object


#binary node that says what two relations to combine
@dataclass
class Binary:
    op: str   # union, minus, join, ...
    left: object
    right: object
    cond: object | None = None  # only for join


#compare node that says what two attributes to compare
@dataclass
class Compare:
    op: str
    left: object
    right: object

#attr node that says what attribute to project
@dataclass
class Attr:
    name: str
    relation: str | None = None  # Emp.DID → relation="Emp", name="DID"

#just a num
@dataclass
class Num:
    value: int

#just a string
@dataclass
class Str:
    value: str

#not node that says what condition to negate
@dataclass
class Not:
    cond: object

#and node that says what two conditions to combine
@dataclass
class And:
    left: object
    right: object

#or node that says what two conditions to combine
@dataclass
class Or:
    left: object
    right: object