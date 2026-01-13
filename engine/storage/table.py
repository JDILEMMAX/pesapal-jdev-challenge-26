# engine/storage/table.py

from typing import List, Dict


class Table:
    def __init__(self, name: str, columns: List[str]):
        self.name = name
        self.columns = columns
        self._rows: List[Dict[str, any]] = []

    def insert_row(self, row: Dict[str, any]):
        if not all(col in row for col in self.columns):
            raise ValueError("Row missing required columns")
        self._rows.append(row)

    def rows(self):
        return self._rows
