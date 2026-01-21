from dataclasses import dataclass, field
from typing import Type, List, Optional


@dataclass
class Column:
    """
    Metadata for a single column.
    Independent of physical storage.
    """

    name: str
    dtype: Type
    nullable: bool = False
    primary_key: bool = False
    auto_increment: bool = False
    constraints: List[str] = field(default_factory=list)  # e.g., ['PRIMARY_KEY', 'NOT_NULL', 'AUTO_INCREMENT']
