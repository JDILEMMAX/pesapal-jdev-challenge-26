# engine/executors/projection.py
from .base import Executor

class Projection(Executor):
    def __init__(self, source: Executor, columns):
        self.source = source
        # If columns contains Column("*"), we'll expand it during execution
        self.columns_ast = columns  # store AST objects, not names yet

    def execute(self):
        rows = self.source.execute()
        if not rows:
            return []

        # Determine column names
        if len(self.columns_ast) == 1 and self.columns_ast[0].name == "*":
            # Expand '*' to all columns from the first row
            columns = list(rows[0].keys())
        else:
            columns = [c.name for c in self.columns_ast]

        # Build projected rows
        return [{col: row[col] for col in columns} for row in rows]
