from .base import Executor


class TableScan(Executor):
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name
        self.table = self.engine.catalog.get_table(table_name)

    def execute(self):
        # Materialize all rows (M2 is small enough for this)
        return list(self.engine.scan_table(self.table_name))
