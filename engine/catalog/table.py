from dataclasses import dataclass
from typing import List
from engine.catalog.column import Column
from engine.record.schema import TableSchema, ColumnSchema

@dataclass
class Table:
    """
    Table metadata and schema information.
    Connects schema to physical storage.
    """

    name: str
    columns: List[Column]
    file_id: int = -1  # optional storage identifier

    @property
    def schema(self) -> TableSchema:
        """
        Dynamically generate TableSchema from columns.
        """
        col_schemas = [
            ColumnSchema(c.name, c.dtype, c.nullable) for c in self.columns
        ]
        return TableSchema(col_schemas)
