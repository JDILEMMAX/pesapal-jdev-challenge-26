import os
from tempfile import NamedTemporaryFile

from engine.storage.file_manager import FileManager
from engine.storage.pager import Pager
from engine.record.schema import ColumnSchema, TableSchema
from engine.record.record import Record
from engine.catalog.column import Column
from engine.catalog.table import Table
from engine.catalog.catalog import Catalog
from engine.record.page_layout import RowPage
from engine.storage.page import Page


def run_multi_row_test():
    print("=== Multi-Row Per Page Test ===")

    # Temporary storage file
    with NamedTemporaryFile(delete=False) as tmpfile:
        file_path = tmpfile.name

    print(f"Temporary storage file: {file_path}")

    # FileManager & Pager
    fm = FileManager(file_path)
    pager = Pager(fm, page_size=64)  # small pages for testing overflow

    # Table schema and record handler
    columns = [
        ColumnSchema("id", int, False),
        ColumnSchema("name", str, False),
        ColumnSchema("balance", float, True),
    ]
    schema = TableSchema(columns)
    record_handler = Record(schema)

    # Rows to store
    rows = [
        [1, "Alice", 100.5],
        [2, "Bob", None],
        [3, "Charlie", 250.0],
        [4, "Diana", 400.75],
        [5, "Eve", 50.25],
    ]

    # Keep track of pages used
    page_num = 0
    page = RowPage(pager.get_page(page_num))

    for row in rows:
        encoded = record_handler.encode(row)
        if not page.add_row(encoded):
            # Flush current page and start new page
            pager.flush_page(page_num)
            page_num += 1
            page = RowPage(pager.get_page(page_num))
            if not page.add_row(encoded):
                raise RuntimeError("Row too large to fit in empty page")
        print(f"Inserted row into page {page_num}: {row}")

    # Flush last page
    pager.flush_page(page_num)

    # Read back all pages
    for p_num in range(page_num + 1):
        page = RowPage(pager.get_page(p_num))
        rows_data = page.get_rows()
        print(f"\nPage {p_num} rows:")
        for rdata in rows_data:
            print(record_handler.decode(rdata))

    # Cleanup
    os.unlink(file_path)
    print("\nTemporary storage file removed.")
    print("=== Multi-Row Test Complete ===")


if __name__ == "__main__":
    run_multi_row_test()
