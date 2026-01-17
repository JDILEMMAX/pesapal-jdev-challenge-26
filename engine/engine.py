from pathlib import Path
from typing import List, Dict, Generator, Tuple
from engine.exceptions import EngineError
from engine.catalog.catalog import Catalog
from engine.catalog.table import Table
from engine.record.record import Record
from engine.record.schema import TableSchema, ColumnSchema
from engine.storage.file_manager import FileManager
from engine.storage.pager import Pager
from engine.record.page_layout import RowPage


SQL_TYPE_MAP = {
    "INT": int,
    "INTEGER": int,
    "TEXT": str,
    "STRING": str,
    "FLOAT": float,
    "REAL": float,
}


class Engine:
    """
    Top-level database engine façade.
    """

# That line in Engine.__init__(self, db_path: str = "data/dbfile", page_size: int = 4096) defines defaults,
# not the entry point itself. The actual entry point is connection.py, which decides when and how the engine
# is created. The db_path="data/dbfile" default exists so the engine can be instantiated without arguments
# (tests, REPL, harnesses), but in production the path should be chosen by connection.py. Conceptually, 
# db_path tells the engine where persistent storage lives on disk, while page_size=4096 configures how the 
# pager and file manager operate in memory (buffering, page layout, I/O granularity). So yes: connection.py 
# anchors the permanent storage, and page_size governs the in-memory paging mechanics, but the default values 
# are just fallbacks, not ownership.

    def __init__(self, db_path: str = "data/dbfile", page_size: int = 4096):
        self.catalog = Catalog()
        self.file_manager = FileManager(Path(db_path))
        self.pager = Pager(self.file_manager, page_size)

        self.table_files: Dict[str, int] = {}
        self.next_file_id = 0

    # ---------- TABLE OPS ----------

    def create_table(self, table_name: str, columns):
        """
        columns: List of (column_name, sql_type)
        Example: [("id", "INT"), ("name", "TEXT")]
        """

        if table_name in self.catalog.tables:
            raise EngineError(f"Table {table_name} already exists")

        col_schemas = []
        for name, sql_type in columns:
            sql_type = sql_type.upper()
            if sql_type not in SQL_TYPE_MAP:
                raise EngineError(f"Unsupported SQL type: {sql_type}")
            col_schemas.append(
                ColumnSchema(name=name, dtype=SQL_TYPE_MAP[sql_type], nullable=True)
            )

        schema = TableSchema(col_schemas)

        file_id = self.next_file_id
        self.next_file_id += 1
        self.table_files[table_name] = file_id

        table = Table(name=table_name, columns=[c.name for c in col_schemas])
        table.schema = schema
        table.file_id = file_id
        self.catalog.register_table(table)

        page = self.pager.get_page(file_id)
        page.clear()

    # ---------- INSERT ----------

    def insert_row(self, table_name: str, values: List):
        table = self.catalog.get_table(table_name)
        schema = table.schema

        if len(values) != len(schema.columns):
            raise EngineError(
                f"Expected {len(schema.columns)} values, got {len(values)}"
            )

        coerced = []
        for value, column in zip(values, schema.columns):
            try:
                coerced.append(column.dtype(value))
            except Exception:
                raise EngineError(
                    f"Invalid value '{value}' for column '{column.name}'"
                )

        record_bytes = Record.from_values(schema, coerced)

        file_id = self.table_files[table_name]

        page = self.pager.get_page(file_id)
        row_page = RowPage(page)

        if not row_page.add_row(record_bytes):
            page = self.pager.get_page(file_id + 1)
            row_page = RowPage(page)
            if not row_page.add_row(record_bytes):
                raise EngineError("Row too large to fit in page")

        self.pager.flush_page(file_id)

    # ---------- SCAN ----------

    def scan_table(self, table_name: str) -> Generator[Dict, None, None]:
        if table_name not in self.catalog.tables:
            raise EngineError(f"Table {table_name} does not exist")

        table = self.catalog.get_table(table_name)
        schema = table.schema
        record = Record(schema)

        file_id = self.table_files[table_name]

        for page in self.pager.iter_pages(file_id):
            row_page = RowPage(page)
            for raw in row_page.get_rows():
                values = record.decode(raw)
                yield dict(zip(schema.column_names(), values))

    def get_rows(self, table_name: str):
        """
        Compatibility helper for executors & legacy code.
        Materializes scan_table(). Avoid for large tables.
        """
        return list(self.scan_table(table_name))
