from .base import Executor

class JoinExecutor(Executor):
    """
    Nested-loop INNER JOIN executor. Read-only.
    """
    def __init__(self, engine, left_table, right_table, left_column, right_column):
        self.engine = engine
        self.left_table = left_table.upper()
        self.right_table = right_table.upper()
        # Handle qualified column names (e.g., "u.id" -> extract "id")
        self.left_column = self._extract_column_name(left_column).lower()
        self.right_column = self._extract_column_name(right_column).lower()

        self.left_rows = list(engine.scan_table(self.left_table))
        self.right_rows = list(engine.scan_table(self.right_table))

    def _extract_column_name(self, col_ref):
        """Extract column name from qualified reference (table.column -> column)"""
        if "." in col_ref:
            return col_ref.split(".")[1]
        return col_ref

    def execute(self):
        result = []
        for lrow in self.left_rows:
            for rrow in self.right_rows:
                if lrow[self.left_column] == rrow[self.right_column]:
                    # Preserve left-table columns when keys collide (left wins)
                    combined = {**rrow, **lrow}
                    result.append(combined)
        return result
