from .base import Executor


class InsertExecutor(Executor):
    def __init__(self, storage_engine, table, values):
        self.storage_engine = storage_engine
        self.table = table
        self.values = [v.value for v in values]

    def execute(self):
        self.storage_engine.insert_row(self.table, self.values)
        return {"status": "OK"}
