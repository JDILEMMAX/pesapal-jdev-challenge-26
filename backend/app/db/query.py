from typing import List

from engine.sql.ast import Select, Insert, CreateTable
from engine.planner.logical import (
    LogicalScan,
    LogicalFilter,
    LogicalProjection,
    LogicalInsert,
)
from engine.executor.scan import TableScan
from engine.executor.filter import Filter
from engine.executor.projection import Projection
from engine.executor.insert import InsertExecutor
from engine.exceptions import QueryError

# Moving query.py to backend/app/db/ is fine because its internal imports like from engine.* 
# still work as long as the project root is in sys.path, which your manage.py ensures with 
# sys.path.insert(0, ROOT_DIR). This makes Python treat engine/ as a top-level package, 
# so the internal engine-related imports in query.py continue to resolve correctly. 
# The only files that may need adjustments are scripts run directly outside this context 
# (like test harnesses), which either need the project root added to sys.path or relative 
# imports to access query.py.

# ---------- PLANNING ----------
def build_plan(ast):
    """Convert AST into a logical plan tree."""
    if isinstance(ast, Select):
        plan = LogicalScan(ast.table)
        if ast.where is not None:
            plan = LogicalFilter(plan, ast.where)
        return LogicalProjection(plan, ast.columns)

    if isinstance(ast, Insert):
        return LogicalInsert(ast.table, ast.values)

    if isinstance(ast, CreateTable):
        return ast  # executed directly

    raise QueryError(f"Unsupported AST node: {type(ast)}")


# ---------- EXECUTION ----------
def execute_plan(plan, engine) -> List[dict]:
    """
    Execute a logical plan or AST node using the real Engine.
    """

    # CREATE TABLE
    if isinstance(plan, CreateTable):
        # plan.columns = List[(name, sql_type)]
        engine.create_table(plan.name, plan.columns)
        return []

    # INSERT
    if isinstance(plan, LogicalInsert):
        executor = InsertExecutor(engine, plan.table, plan.values)
        return executor.execute()

    # SELECT
    executor = _build_executor(plan, engine)
    return executor.execute()


# ---------- HELPER ----------
def _build_executor(plan, engine):
    if isinstance(plan, LogicalScan):
        return TableScan(engine, plan.table)

    if isinstance(plan, LogicalFilter):
        source = _build_executor(plan.source, engine)
        return Filter(source, plan.predicate)

    if isinstance(plan, LogicalProjection):
        source = _build_executor(plan.source, engine)
        return Projection(source, plan.columns)

    raise QueryError(f"Unsupported logical plan: {type(plan)}")
