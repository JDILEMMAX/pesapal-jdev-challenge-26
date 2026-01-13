from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class Column:
    """
    Metadata for a single column.
    Independent of physical storage.
    """

    name: str
    dtype: Type
    nullable: bool = False
