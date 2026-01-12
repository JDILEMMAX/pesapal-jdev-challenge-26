from dataclasses import dataclass
from typing import List, Union
from engine.sql.ast import *

@dataclass
class LogicalPlanNode:
    pass

@dataclass
class LogicalCreate(LogicalPlanNode):
    table: str
    columns: List[str]

@dataclass
class LogicalInsert(LogicalPlanNode):
    table: str
    values: List[Literal]

@dataclass
class LogicalScan(LogicalPlanNode):
    table: str

@dataclass
class LogicalFilter(LogicalPlanNode):
    source: LogicalPlanNode
    predicate: BinaryExpression

@dataclass
class LogicalProjection(LogicalPlanNode):
    source: LogicalPlanNode
    columns: List[Column]
