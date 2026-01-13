from dataclasses import dataclass
from typing import List
from engine.catalog.column import Column
from engine.record.schema import TableSchema


@dataclass
class Table:
    """
    Table metadata and schema information.
    Connects schema to physical storage.
    """

    name: str
    columns: List[Column]

    def schema(self) -> TableSchema:
        col_schemas = [
            TableSchema.ColumnSchema(c.name, c.dtype, c.nullable) for c in self.columns
        ]
        return TableSchema(col_schemas)
