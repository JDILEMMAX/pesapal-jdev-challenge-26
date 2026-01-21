from typing import List
from engine.sql.ast import Select, Insert, CreateTable, Update, Delete, DropTable, Join
from engine.planner.logical import (
    LogicalScan,
    LogicalFilter,
    LogicalProjection,
    LogicalInsert,
    LogicalUpdate,
    LogicalDelete,
    LogicalDrop,
)
from engine.executor.scan import TableScan
from engine.executor.filter import Filter
from engine.executor.projection import Projection
from engine.executor.insert import InsertExecutor
from engine.executor.update import UpdateExecutor
from engine.executor.delete import DeleteExecutor
from engine.executor.drop import DropTableExecutor
from engine.executor.join import JoinExecutor
from engine.executor.order_by import OrderBy
from engine.executor.limit import Limit
from engine.executor.group_by import GroupBy
from engine.exceptions import QueryError

# Moving query.py to backend/app/db/ is fine because its internal imports like from engine.* 
# still work as long as the project root is in sys.path, which your manage.py ensures with 
# sys.path.insert(0, ROOT_DIR). This makes Python treat engine/ as a top-level package, 
# so the internal engine-related imports in query.py continue to resolve correctly. 
# The only files that may need adjustments are scripts run directly outside this context 
# (like test harnesses), which either need the project root added to sys.path or relative 
# imports to access query.py.

# --------------------------
# PLANNING
# --------------------------
def build_plan(ast):
    """
    Convert AST into a logical plan tree.
    """
    if isinstance(ast, Select):
        # If the SELECT's table is a Join AST, pass the Join through so the executor
        # builder can construct a JoinExecutor instead of treating it as a plain scan.
        if isinstance(ast.table, Join):
            plan = ast.table
        else:
            plan = LogicalScan(ast.table)
        if ast.where:
            plan = LogicalFilter(plan, ast.where)
        projection = LogicalProjection(plan, ast.columns)
        # Store SELECT AST for query shaping (ORDER BY, LIMIT, GROUP BY, etc.)
        projection.select_ast = ast
        return projection

    if isinstance(ast, Insert):
        return LogicalInsert(ast.table, ast.values)

    if isinstance(ast, CreateTable):
        return ast  # executed directly

    if isinstance(ast, DropTable):
        return LogicalDrop(ast.name)

    if isinstance(ast, Update):
        return LogicalUpdate(ast.table, ast.assignments, ast.where)

    if isinstance(ast, Delete):
        return LogicalDelete(ast.table, ast.where)
    
    if isinstance(ast, Join):
        # For now, pass Join AST as-is, executor builder will handle it
        return ast

    raise QueryError(f"Unsupported AST node: {type(ast)}")


# --------------------------
# EXECUTION
# --------------------------
def execute_plan(plan, engine) -> List[dict]:
    """
    Execute a logical plan or AST node using the real Engine.
    """

    # CREATE TABLE
    if isinstance(plan, CreateTable):
        engine.create_table(plan.name, plan.columns)
        return []

    # INSERT
    if isinstance(plan, LogicalInsert):
        executor = InsertExecutor(engine, plan.table, plan.values)
        return executor.execute()

    # DROP TABLE
    if isinstance(plan, LogicalDrop):
        executor = DropTableExecutor(engine, plan.table)
        return executor.execute()

    # UPDATE
    if isinstance(plan, LogicalUpdate):
        executor = UpdateExecutor(
            engine, plan.table, plan.assignments, plan.predicate
        )
        return executor.execute()

    # DELETE
    if isinstance(plan, LogicalDelete):
        executor = DeleteExecutor(engine, plan.table, plan.predicate)
        return executor.execute()

    # SELECT pipeline
    executor = _build_executor(plan, engine)
    return executor.execute()


# --------------------------
# EXECUTOR BUILDER (SELECT pipeline)
# --------------------------
def _build_executor(plan, engine):
    """
    Recursively build executor tree from logical plan nodes.
    """
    if isinstance(plan, LogicalScan):
        return TableScan(engine, plan.table)

    if isinstance(plan, LogicalFilter):
        source = _build_executor(plan.source, engine)
        return Filter(source, plan.predicate)

    if isinstance(plan, LogicalProjection):
        source = _build_executor(plan.source, engine)
        executor = Projection(source, plan.columns)
        
        # Apply query shaping on top of projection
        select_ast = plan.select_ast if hasattr(plan, 'select_ast') else None
        if select_ast and hasattr(select_ast, 'group_by') and select_ast.group_by:
            executor = GroupBy(executor, select_ast.group_by, select_ast.having)
        if select_ast and hasattr(select_ast, 'order_by') and select_ast.order_by:
            executor = OrderBy(executor, select_ast.order_by)
        if select_ast and (hasattr(select_ast, 'limit') and select_ast.limit or hasattr(select_ast, 'offset') and select_ast.offset):
            executor = Limit(executor, select_ast.limit, select_ast.offset)
        
        return executor
    
    if isinstance(plan, Join):
        return JoinExecutor(
            engine,
            plan.left_table,
            plan.right_table,
            plan.left_column,
            plan.right_column
        )

    raise QueryError(f"Unsupported logical plan: {type(plan)}")
