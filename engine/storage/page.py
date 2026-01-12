from __future__ import annotations
from typing import Any
import struct

class Page:
    """
    Represents a fixed-size page of bytes in memory.
    Provides safe read/write access with bounds checking.
    """
    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Page size must be positive")
        self.size = size
        self.data = bytearray(size)

    def read(self, offset: int, length: int) -> bytes:
        """
        Read `length` bytes starting from `offset`.
        Raises IndexError if out of bounds.
        """
        if offset < 0 or length < 0 or offset + length > self.size:
            raise IndexError("Read exceeds page boundaries")
        return bytes(self.data[offset:offset+length])

    def write(self, offset: int, content: bytes) -> None:
        """
        Write bytes into the page at given offset.
        Raises IndexError if out of bounds.
        """
        end = offset + len(content)
        if offset < 0 or end > self.size:
            raise IndexError("Write exceeds page boundaries")
        self.data[offset:end] = content

    def clear(self) -> None:
        """Reset page data to zero."""
        self.data[:] = b'\x00' * self.size
