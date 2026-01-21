from __future__ import annotations
from typing import Any


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
        return bytes(self.data[offset:offset + length])

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
        """Reset all page bytes to zero."""
        self.data[:] = b"\x00" * self.size


class RowPage:
    """
    Wraps a Page to store multiple variable-length rows safely.

    Header layout (4 bytes total):
      bytes 0-1: next_free offset (2 bytes)
      bytes 2-3: row_count (2 bytes)

    Notes:
      - Offsets are reconstructed strictly using row_count.
      - Partially written or corrupted rows beyond row_count are ignored.
      - Supports future extensions: UPDATE/DELETE can use offsets for in-place updates.
    """

    HEADER_SIZE = 4  # 2 bytes for next_free + 2 bytes for row_count

    def __init__(self, page: Page):
        self.page = page

        # --- Read header ---
        raw_next_free = self.page.read(0, 2)
        raw_row_count = self.page.read(2, 2)

        self.next_free = int.from_bytes(raw_next_free, "big") or self.HEADER_SIZE
        self.row_count = int.from_bytes(raw_row_count, "big") or 0

        # --- Rebuild row offsets safely ---
        # Scan through page data sequentially, skipping rows with negative length (logically deleted)
        self.offsets = []
        idx = self.HEADER_SIZE
        
        # Scan until we reach next_free or page end
        while idx < self.next_free and idx + 2 <= self.page.size:
            # Read length as signed integer (negative = deleted)
            raw_len = self.page.read(idx, 2)
            length = int.from_bytes(raw_len, "big", signed=False)
            signed_length = int.from_bytes(raw_len, "big", signed=True)
            
            if signed_length < 0:
                # Deleted row - skip it but use absolute value to know how much to skip
                actual_length = -signed_length
                idx += 2 + actual_length
                continue
            
            # Check if row is within bounds
            if length == 0 or idx + 2 + length > self.page.size or idx + 2 + length > self.next_free:
                break
            
            self.offsets.append(idx)
            idx += 2 + length
        
        # Update row_count to reflect valid rows
        self.row_count = len(self.offsets)
        self.page.write(2, self.row_count.to_bytes(2, "big"))


    def can_fit(self, data: bytes) -> bool:
        """Check if a row can fit in the remaining page space."""
        return self.next_free + 2 + len(data) <= self.page.size

    def add_row(self, data: bytes) -> bool:
        """
        Add a row to the page.

        Returns:
            True if successful, False if row would overflow the page.
        """
        row_len = len(data)
        if not self.can_fit(data):
            return False

        # Write row length prefix
        self.page.write(self.next_free, row_len.to_bytes(2, "big"))
        self.next_free += 2

        # Write row data
        self.page.write(self.next_free, data)
        self.offsets.append(self.next_free - 2)
        self.next_free += row_len

        # Update header (next_free and row_count)
        self.row_count += 1
        self.page.write(0, self.next_free.to_bytes(2, "big"))
        self.page.write(2, self.row_count.to_bytes(2, "big"))

        return True

    def get_rows(self) -> list[bytes]:
        """
        Retrieve all valid rows.

        Ignores any deleted rows (marked with negative length) or partially written rows.
        """
        rows = []
        for offset in self.offsets:
            if offset + 2 > self.page.size or offset + 2 > self.next_free:
                continue

            raw_len = self.page.read(offset, 2)
            signed_length = int.from_bytes(raw_len, "big", signed=True)
            
            if signed_length < 0:  # Deleted row
                continue
            
            length = signed_length
            if length == 0 or offset + 2 + length > self.page.size or offset + 2 + length > self.next_free:
                continue

            rows.append(self.page.read(offset + 2, length))

        return rows

    # --- Future-proof methods for in-place updates/deletes ---
    def update_row(self, index: int, new_data: bytes) -> bool:
        """Replace a row by index if new_data length matches existing row length."""
        if index < 0 or index >= len(self.offsets):
            return False
        offset = self.offsets[index]
        old_len = int.from_bytes(self.page.read(offset, 2), "big")
        if len(new_data) != old_len:
            return False  # only support in-place updates of same length for now
        self.page.write(offset + 2, new_data)
        return True

    def delete_row(self, index: int) -> bool:
        """Mark a row as deleted by setting its length to 0xFFFF (marker for deleted)."""
        if index < 0 or index >= len(self.offsets):
            return False
        offset = self.offsets[index]
        # Use 0xFFFF as deletion marker (or read old length and negate to preserve it)
        old_length = int.from_bytes(self.page.read(offset, 2), "big")
        # Store old length negated so we can skip the right number of bytes
        self.page.write(offset, (-old_length).to_bytes(2, "big", signed=True))
        return True
