# engine/storage_engine.py
from engine.storage.file_manager import FileManager
from engine.storage.pager import Pager
from engine.record.page_layout import RowPage
from engine.exceptions import EngineError

class StorageEngine:
    """Minimal storage engine interface for M2 query execution."""
    def __init__(self, db_path="data/dbfile", page_size=4096):
        self.file_manager = FileManager(db_path)
        self.pager = Pager(self.file_manager, page_size)
        self.tables = {}  # table_name -> column names
        self.rows = {}    # table_name -> list of dicts

    def create_table(self, table_name: str, columns: list[str]):
        if table_name in self.tables:
            raise EngineError(f"Table {table_name} already exists")
        self.tables[table_name] = columns
        self.rows[table_name] = []

    def insert_row(self, table_name: str, values: list):
        if table_name not in self.tables:
            raise EngineError(f"Table {table_name} does not exist")
        if len(values) != len(self.tables[table_name]):
            raise EngineError(f"Expected {len(self.tables[table_name])} values, got {len(values)}")
        self.rows[table_name].append(dict(zip(self.tables[table_name], values)))

    def get_rows(self, table_name: str):
        if table_name not in self.tables:
            raise EngineError(f"Table {table_name} does not exist")
        return self.rows[table_name]
