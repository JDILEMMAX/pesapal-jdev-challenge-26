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
            columns = [c.name.lower() for c in self.columns_ast]

        # Build projected rows, handling aggregate functions in column names
        result = []
        for row in rows:
            projected_row = {}
            for col in columns:
                if col.startswith("count("):
                    # count(*) or count(column) — use the aggregate value directly
                    # This is already computed by GroupBy executor
                    projected_row[col] = row.get(col)
                else:
                    projected_row[col] = row.get(col)
            result.append(projected_row)
        
        return result
