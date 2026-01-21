from pathlib import Path
from typing import List, Dict, Generator, Any
from engine.exceptions import EngineError
from engine.catalog.catalog import Catalog
from engine.catalog.column import Column
from engine.catalog.table import Table
from engine.record.record import Record
from engine.storage.file_manager import FileManager
from engine.storage.pager import Pager
from engine.storage.page import RowPage


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

        # Map table name → starting page id
        self.table_files: Dict[str, int] = {}

        # Next available page id (global)
        self.next_file_id = 0

    # ------------------------------------------------------------------
    # INTERNAL: PAGE RANGE RESOLUTION
    # ------------------------------------------------------------------

    def _table_page_range(self, table_name: str) -> tuple[int, int]:
        """
        Return (start_page, end_page) for a table.
        end_page is exclusive.
        """
        table_name = table_name.upper()

        if table_name not in self.table_files:
            raise EngineError(f"Table {table_name} does not exist")

        start = self.table_files[table_name]

        # Find the next table start, if any
        starts = sorted(self.table_files.values())
        idx = starts.index(start)

        if idx + 1 < len(starts):
            end = starts[idx + 1]
        else:
            end = self.next_file_id

        return start, end

    # ------------------------------------------------------------------
    # TABLE OPERATIONS
    # ------------------------------------------------------------------

    def create_table(self, table_name: str, columns):
        table_name = table_name.upper()
        if table_name in self.catalog.tables:
            raise EngineError(f"Table {table_name} already exists")

        table_columns = []
        for col in columns:
            if hasattr(col, "dtype"):  # ColumnDef
                name = col.name
                sql_type = col.dtype.name.upper()
                constraints = [c.kind for c in col.constraints] if hasattr(col, 'constraints') else []
            else:
                name, sql_type = col
                sql_type = sql_type.upper()
                constraints = []

            if sql_type not in SQL_TYPE_MAP:
                raise EngineError(f"Unsupported SQL type: {sql_type}")

            # Parse constraint flags
            primary_key = "PRIMARY_KEY" in constraints
            auto_increment = "AUTO_INCREMENT" in constraints
            nullable = "NOT_NULL" not in constraints  # Default is nullable unless NOT_NULL specified

            table_columns.append(
                Column(
                    name=name,
                    dtype=SQL_TYPE_MAP[sql_type],
                    nullable=nullable,
                    primary_key=primary_key,
                    auto_increment=auto_increment,
                    constraints=constraints
                )
            )

        file_id = self.next_file_id
        self.next_file_id += 1
        self.table_files[table_name] = file_id

        table = Table(name=table_name, columns=table_columns)
        table.file_id = file_id
        self.catalog.register_table(table)

        page = self.pager.get_page(file_id)
        page.clear()

    # ------------------------------------------------------------------
    # INSERT
    # ------------------------------------------------------------------

    def insert_row(self, table_name: str, values: List[Any]):
        table_name = table_name.upper()
        table = self.catalog.get_table(table_name)
        schema = table.schema

        if len(values) != len(schema.columns):
            raise EngineError(
                f"Expected {len(schema.columns)} values, got {len(values)}"
            )

        coerced = []
        for value, column in zip(values, schema.columns):
            if value is None:
                if not column.nullable:
                    raise EngineError(f"Column '{column.name}' cannot be null (NOT NULL constraint)")
                coerced.append(None)
            else:
                try:
                    coerced.append(column.dtype(value))
                except Exception:
                    raise EngineError(
                        f"Invalid value '{value}' for column '{column.name}'"
                    )

        if all(v is None for v in coerced):
            raise EngineError("Cannot insert a row with all NULL values")

        # Enforce PRIMARY KEY uniqueness
        for idx, column in enumerate(table.columns):
            if column.primary_key and coerced[idx] is not None:
                # Check if this value already exists
                for existing_row in self.scan_table(table_name):
                    if existing_row.get(column.name.lower()) == coerced[idx]:
                        raise EngineError(f"PRIMARY KEY violation: duplicate value '{coerced[idx]}' in column '{column.name}'")

        record_bytes = Record.from_values(schema, coerced)

        start, end = self._table_page_range(table_name)

        # Try existing pages first
        for page_num in range(start, end):
            page = self.pager.get_page(page_num)
            row_page = RowPage(page)
            if row_page.add_row(record_bytes):
                self.pager.flush_page(page_num)
                return

        # Need a new page
        page_num = self.next_file_id
        self.next_file_id += 1

        page = self.pager.get_page(page_num)
        page.clear()
        row_page = RowPage(page)

        if not row_page.add_row(record_bytes):
            raise EngineError("Row too large to fit in page")

        self.pager.flush_page(page_num)

    # ------------------------------------------------------------------
    # SCAN
    # ------------------------------------------------------------------

    def scan_table(self, table_name: str) -> Generator[Dict, Any, None]:
        table_name = table_name.upper()
        table = self.catalog.get_table(table_name)
        schema = table.schema
        record = Record(schema)

        start, end = self._table_page_range(table_name)

        for page_num in range(start, end):
            page = self.pager.get_page(page_num)
            row_page = RowPage(page)

            for raw in row_page.get_rows():
                values = record.decode(raw)
                yield {
                    name.lower(): value
                    for name, value in zip(schema.column_names(), values)
                }

    def get_rows(self, table_name: str) -> List[Dict]:
        return list(self.scan_table(table_name))

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update_rows(
        self,
        table_name: str,
        set_values: Dict[str, Any],
        where_fn=None,
    ) -> List[Dict]:
        table_name = table_name.upper()
        table = self.catalog.get_table(table_name)
        schema = table.schema
        record = Record(schema)
        schema_names = schema.column_names()

        start, end = self._table_page_range(table_name)

        updated = 0

        for page_num in range(start, end):
            page = self.pager.get_page(page_num)
            row_page = RowPage(page)

            for idx, offset in enumerate(row_page.offsets):
                length = int.from_bytes(page.read(offset, 2), "big")
                if length == 0:
                    continue

                row_bytes = page.read(offset + 2, length)
                row_values = record.decode(row_bytes)

                row_dict = {
                    name.lower(): value
                    for name, value in zip(schema_names, row_values)
                }

                if where_fn and not where_fn(row_dict):
                    continue

                new_values = list(row_values)
                for col, val in set_values.items():
                    col_u = col.upper()
                    if col_u not in schema_names:
                        raise EngineError(f"Column {col} does not exist")
                    idx_col = schema_names.index(col_u)
                    new_values[idx_col] = schema.columns[idx_col].dtype(val)

                new_bytes = record.encode(new_values)
                if len(new_bytes) != length:
                    raise EngineError(
                        "In-place update failed: row size change not supported"
                    )

                row_page.update_row(idx, new_bytes)
                updated += 1

            self.pager.flush_page(page_num)

        return [{"updated": updated}]

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete_rows(self, table_name: str, where_fn=None) -> List[Dict]:
        table_name = table_name.upper()
        table = self.catalog.get_table(table_name)
        schema = table.schema
        record = Record(schema)
        schema_names = schema.column_names()

        start, end = self._table_page_range(table_name)

        deleted = 0

        for page_num in range(start, end):
            page = self.pager.get_page(page_num)
            row_page = RowPage(page)

            for idx, offset in enumerate(row_page.offsets):
                # Read length (negative = already deleted)
                raw_len = page.read(offset, 2)
                length = int.from_bytes(raw_len, "big", signed=False)
                signed_length = int.from_bytes(raw_len, "big", signed=True)
                
                if signed_length < 0:  # Already deleted
                    continue

                row_bytes = page.read(offset + 2, length)
                row_values = record.decode(row_bytes)

                row_dict = {
                    name.lower(): value
                    for name, value in zip(schema_names, row_values)
                }

                if where_fn and not where_fn(row_dict):
                    continue

                row_page.delete_row(idx)
                deleted += 1

            self.pager.flush_page(page_num)

        return [{"deleted": deleted}]
