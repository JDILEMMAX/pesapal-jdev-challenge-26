from .base import Executor

class JoinExecutor(Executor):
    """
    Nested-loop INNER JOIN executor. Read-only.
    """
    def __init__(self, engine, left_table, right_table, left_column, right_column):
        self.engine = engine
        self.left_table = left_table.upper()
        self.right_table = right_table.upper()
        self.left_column = left_column.lower()
        self.right_column = right_column.lower()

        self.left_rows = list(engine.scan_table(self.left_table))
        self.right_rows = list(engine.scan_table(self.right_table))

    def execute(self):
        result = []
        for lrow in self.left_rows:
            for rrow in self.right_rows:
                if lrow[self.left_column] == rrow[self.right_column]:
                    # Preserve left-table columns when keys collide (left wins)
                    combined = {**rrow, **lrow}
                    result.append(combined)
        return result
