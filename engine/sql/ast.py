from dataclasses import dataclass
from typing import List, Union, Optional


# =========================
# Base AST node
# =========================

@dataclass
class ASTNode:
    pass


# =========================
# Expressions
# =========================

@dataclass
class Column(ASTNode):
    name: str


@dataclass
class Literal(ASTNode):
    value: Union[str, int, float, bool]


@dataclass
class BinaryExpression(ASTNode):
    left: Column
    operator: str  # '=', '<', '>', '<=', '>=', '!='
    right: Literal


# =========================
# Data Types & Constraints
# =========================

@dataclass
class DataType(ASTNode):
    """
    Represents a SQL data type.

    Examples:
      INTEGER
      FLOAT
      VARCHAR(100)
      BOOLEAN
      DATE
      TIMESTAMP
    """
    name: str
    args: Optional[List[int]] = None  # e.g. VARCHAR(100)


@dataclass
class ColumnConstraint(ASTNode):
    """
    Represents a column-level constraint.
    Enforcement happens later.
    """
    kind: str  # PRIMARY_KEY, NOT_NULL, UNIQUE, AUTO_INCREMENT, FOREIGN_KEY
    ref_table: Optional[str] = None
    ref_column: Optional[str] = None


@dataclass
class ColumnDef(ASTNode):
    """
    Full column definition inside CREATE TABLE.
    """
    name: str
    dtype: DataType
    constraints: List[ColumnConstraint]


# =========================
# Statements (DDL / DML)
# =========================

@dataclass
class CreateTable(ASTNode):
    """
    CREATE TABLE statement.

    Backward-compatible:
      - columns may still be a simple list (legacy)
      - new parser will pass List[ColumnDef]
    """
    name: str
    columns: Union[List[str], List[ColumnDef]]


@dataclass
class DropTable(ASTNode):
    name: str


@dataclass
class Insert(ASTNode):
    table: str
    values: List[Literal]


@dataclass
class Update(ASTNode):
    table: str
    assignments: dict[str, Literal]
    where: Optional[BinaryExpression] = None


@dataclass
class Delete(ASTNode):
    table: str
    where: Optional[BinaryExpression] = None


@dataclass
class Select(ASTNode):
    columns: List[Column]
    table: str
    where: Optional[BinaryExpression] = None
    order_by: Optional[List[tuple]] = None  # List of (column_name, direction: 'ASC'|'DESC')
    limit: Optional[int] = None
    offset: Optional[int] = None
    group_by: Optional[List[Column]] = None
    having: Optional[BinaryExpression] = None


@dataclass
class ShowTables(ASTNode):
    """Represents a SHOW TABLES statement."""
    pass

@dataclass
class Join(ASTNode):
    """
    Represents an INNER JOIN between two tables.
    """
    left_table: str
    right_table: str
    left_column: str
    right_column: str
