from .base import Executor


class Limit(Executor):
    def __init__(self, source: Executor, limit: int, offset: int = 0):
        self.source = source
        self.limit = limit
        self.offset = offset

    def execute(self):
        rows = self.source.execute()
        if not rows:
            return rows

        start = self.offset if self.offset else 0
        end = start + self.limit if self.limit else len(rows)

        return rows[start:end]
