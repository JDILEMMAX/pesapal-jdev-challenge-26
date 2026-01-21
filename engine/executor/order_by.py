from .base import Executor


class OrderBy(Executor):
    def __init__(self, source: Executor, order_by):
        self.source = source
        self.order_by = order_by  # List of (column_name, direction)

    def execute(self):
        rows = self.source.execute()
        if not rows or not self.order_by:
            return rows

        # Sort by each column in order_by, handling multiple columns
        for col_name, direction in reversed(self.order_by):
            reverse = (direction.upper() == "DESC")
            rows = sorted(rows, key=lambda r: r.get(col_name, None) or "", reverse=reverse)

        return rows
