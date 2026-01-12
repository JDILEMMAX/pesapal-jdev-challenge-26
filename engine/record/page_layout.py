from engine.storage.page import Page

class RowPage:
    """
    Wraps a Page to store multiple variable-length rows.
    Uses first 2 bytes as next_free pointer.
    """
    HEADER_SIZE = 2  # bytes to store next_free offset

    def __init__(self, page: Page):
        self.page = page
        # read next_free from page header if non-zero
        raw = self.page.read(0, self.HEADER_SIZE)
        self.next_free = int.from_bytes(raw, 'big')
        if self.next_free == 0:
            self.next_free = self.HEADER_SIZE
        self.offsets = []

    def can_fit(self, data: bytes) -> bool:
        """Check if a row can fit in the remaining page space."""
        return self.next_free + 2 + len(data) <= self.page.size

    def add_row(self, data: bytes) -> bool:
        """Add a row to the page. Returns False if overflow."""
        row_len = len(data)
        if not self.can_fit(data):
            return False
        # write row length
        self.page.write(self.next_free, row_len.to_bytes(2, 'big'))
        self.next_free += 2
        # write row data
        self.page.write(self.next_free, data)
        self.offsets.append(self.next_free - 2)
        self.next_free += row_len
        # update header
        self.page.write(0, (self.next_free).to_bytes(self.HEADER_SIZE, 'big'))
        return True

    def get_rows(self) -> list[bytes]:
        """Retrieve all rows from the page."""
        rows = []
        idx = self.HEADER_SIZE
        while idx < self.next_free:
            length = int.from_bytes(self.page.read(idx, 2), 'big')
            idx += 2
            row_data = self.page.read(idx, length)
            rows.append(row_data)
            idx += length
        return rows
