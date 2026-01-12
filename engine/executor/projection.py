from .base import Executor

class Projection(Executor):
    def __init__(self, source: Executor, columns):
        self.source = source
        self.columns = [c.name for c in columns]

    def execute(self):
        rows = self.source.execute()
        return [{col: row[col] for col in self.columns} for row in rows]
