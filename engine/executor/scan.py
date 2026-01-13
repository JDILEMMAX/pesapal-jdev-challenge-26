from .base import Executor


class TableScan(Executor):
    def __init__(self, storage_engine, table_name):
        self.storage_engine = storage_engine
        self.table_name = table_name

    def execute(self):
        return self.storage_engine.get_rows(self.table_name)
