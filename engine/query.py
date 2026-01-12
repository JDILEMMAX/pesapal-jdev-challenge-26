from typing import List

from engine.sql.ast import Select, Insert, CreateTable
from engine.planner.logical import LogicalScan, LogicalFilter, LogicalProjection, LogicalInsert
from engine.executor.scan import TableScan
from engine.executor.filter import Filter
from engine.executor.projection import Projection
from engine.executor.insert import InsertExecutor
from engine.exceptions import QueryError
from engine.catalog.column import Column
from engine.catalog.table import Table

# --- Minimal catalog for Milestone 2 ---
class Catalog:
    """Tracks tables and their data using StorageEngine."""
    def __init__(self, storage):
        self.storage = storage  # StorageEngine instance

    def register_table(self, table_name: str, columns: List[str]):
        self.storage.create_table(table_name, columns)

    def get_table(self, table_name: str):
        if table_name not in self.storage.tables:
            raise QueryError(f"Table '{table_name}' does not exist")
        return table_name  # For executors, we just pass the table name

# ---------- PLANNING ----------
def build_plan(ast):
    """Convert AST into a logical plan tree."""
    if isinstance(ast, Select):
        plan = LogicalScan(ast.table)
        if getattr(ast, "where", None) is not None:
            plan = LogicalFilter(plan, ast.where)
        return LogicalProjection(plan, ast.columns)

    if isinstance(ast, Insert):
        return LogicalInsert(ast.table, ast.values)

    if isinstance(ast, CreateTable):
        return ast  # handled directly at execution

    raise QueryError(f"Unsupported AST node: {type(ast)}")

# ---------- EXECUTION ----------
def execute_plan(plan, catalog: Catalog) -> List[dict]:
    """Execute a logical plan or AST node using the catalog/storage engine."""
    # CREATE TABLE
    if isinstance(plan, CreateTable):
        catalog.register_table(plan.name, [col_name for col_name, _ in plan.columns])
        return []

    # INSERT
    if isinstance(plan, LogicalInsert):
        executor = InsertExecutor(catalog.storage, plan.table, plan.values)
        return executor.execute()

    # SELECT / Filter / Projection
    executor = _build_executor(plan, catalog)
    return executor.execute()

# ---------- HELPER: build executor tree ----------
def _build_executor(plan, catalog: Catalog):
    """Recursively build executor tree from logical plan nodes."""
    if isinstance(plan, LogicalScan):
        table_name = catalog.get_table(plan.table)
        return TableScan(catalog.storage, table_name)

    if isinstance(plan, LogicalFilter):
        source = _build_executor(plan.source, catalog)
        return Filter(source, plan.predicate)

    if isinstance(plan, LogicalProjection):
        source = _build_executor(plan.source, catalog)
        return Projection(source, plan.columns)

    raise QueryError(f"Unsupported logical plan: {type(plan)}")
