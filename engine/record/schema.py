from __future__ import annotations
from dataclasses import dataclass
from typing import List, Any, Type


@dataclass(frozen=True)
class ColumnSchema:
    name: str
    dtype: Type
    nullable: bool = False


@dataclass
class TableSchema:
    columns: List[ColumnSchema]

    def validate_row(self, row: List[Any]) -> bool:
        """
        Ensure a row matches the schema types and nullability.
        """
        if len(row) != len(self.columns):
            return False
        for value, col in zip(row, self.columns):
            if value is None and not col.nullable:
                return False
            if value is not None and not isinstance(value, col.dtype):
                return False
        return True

    def column_names(self) -> List[str]:
        return [col.name for col in self.columns]
