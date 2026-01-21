from .base import Executor
from engine.exceptions import EngineError

class DropTableExecutor(Executor):
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name

    def execute(self):
        if self.table_name not in self.engine.catalog.tables:
            raise EngineError(f"Table {self.table_name} does not exist")
        # Remove from catalog
        table = self.engine.catalog.tables.pop(self.table_name)
        # Remove physical storage
        if self.table_name in self.engine.table_files:
            file_id = self.engine.table_files.pop(self.table_name)
            # Optionally clear pager pages (simple in-memory)
            page = self.engine.pager.get_page(file_id)
            page.clear()
        return [{"dropped": self.table_name}]
