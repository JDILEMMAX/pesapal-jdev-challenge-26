from .base import Executor


class InsertExecutor(Executor):
    def __init__(self, engine, table_name, values):
        self.engine = engine
        self.table_name = table_name
        self.values = [v.value for v in values]

    def execute(self):
        self.engine.insert_row(self.table_name, self.values)
        return []
