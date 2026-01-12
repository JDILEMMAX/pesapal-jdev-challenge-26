import os
from tempfile import NamedTemporaryFile

from engine.storage.file_manager import FileManager
from engine.storage.pager import Pager
from engine.record.schema import ColumnSchema, TableSchema
from engine.record.record import Record
from engine.catalog.column import Column
from engine.catalog.table import Table
from engine.catalog.catalog import Catalog

def run_test():
    print("=== Milestone 1 Core Storage Engine Test Harness ===")

    # 1️⃣ Create a temporary file to simulate disk
    with NamedTemporaryFile(delete=False) as tmpfile:
        file_path = tmpfile.name

    print(f"Temporary storage file: {file_path}")

    # 2️⃣ Initialize FileManager and Pager
    fm = FileManager(file_path)
    pager = Pager(fm, page_size=128)  # small page for testing

    # 3️⃣ Create a table schema
    columns = [
        ColumnSchema("id", int, False),
        ColumnSchema("name", str, False),
        ColumnSchema("balance", float, True)
    ]
    schema = TableSchema(columns)
    record_handler = Record(schema)

    # 4️⃣ Encode some records and write to pages
    rows = [
        [1, "Alice", 100.5],
        [2, "Bob", None],
        [3, "Charlie", 250.0]
    ]

    for i, row in enumerate(rows):
        page = pager.get_page(i)  # one row per page for simplicity
        encoded = record_handler.encode(row)
        page.write(0, encoded)
        pager.flush_page(i)
        print(f"Written row {i} to page {i}: {row}")

    # 5️⃣ Read back records and decode
    for i in range(len(rows)):
        page = pager.get_page(i)
        data = page.read(0, 128)
        decoded_row = record_handler.decode(data)
        print(f"Read row {i} from page {i}: {decoded_row}")

    # 6️⃣ Create catalog and register a table
    table_columns = [
        Column("id", int, False),
        Column("name", str, False),
        Column("balance", float, True)
    ]
    table = Table("customers", table_columns)
    catalog = Catalog()
    catalog.register_table(table)
    print(f"Registered tables in catalog: {catalog.list_tables()}")
    retrieved_table = catalog.get_table("customers")
    print(f"Retrieved table: {retrieved_table.name}, columns: {[c.name for c in retrieved_table.columns]}")

    # 7️⃣ Cleanup temporary file
    os.unlink(file_path)
    print("Temporary storage file removed.")
    print("=== Test Harness Complete ===")

if __name__ == "__main__":
    run_test()
