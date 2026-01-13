from typing import Dict
from engine.catalog.table import Table
from engine.exceptions import EngineError


class Catalog:
    """
    Central registry for all tables in the engine.
    """

    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def register_table(self, table: Table) -> None:
        if table.name in self.tables:
            raise EngineError(f"Table {table.name} already exists")
        self.tables[table.name] = table

    def get_table(self, name: str) -> Table:
        if name not in self.tables:
            raise EngineError(f"Table {name} does not exist")
        return self.tables[name]

    def list_tables(self) -> list[str]:
        return list(self.tables.keys())
