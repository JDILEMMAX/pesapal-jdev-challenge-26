from dataclasses import dataclass
from typing import List, Union


# Base AST node
@dataclass
class ASTNode:
    pass


# Expressions
@dataclass
class Column(ASTNode):
    name: str


@dataclass
class Literal(ASTNode):
    value: Union[str, int]


@dataclass
class BinaryExpression(ASTNode):
    left: Column
    operator: str  # '=', '<', '>'
    right: Literal


# Statements
@dataclass
class CreateTable(ASTNode):
    name: str
    columns: List[str]


@dataclass
class Insert(ASTNode):
    table: str
    values: List[Literal]


@dataclass
class Select(ASTNode):
    columns: List[Column]
    table: str
    where: Union[BinaryExpression, None] = None


@dataclass
class ShowTables(ASTNode):
    """Represents a SHOW TABLES statement."""
    pass
