from engine.storage.page import Page
from engine.storage.file_manager import FileManager
from typing import Dict, Iterator


class Pager:
    """
    Manages page caching and coordination between memory and disk.
    """

    def __init__(self, file_manager: FileManager, page_size: int = 4096):
        self.file_manager = file_manager
        self.page_size = page_size
        self.cache: Dict[int, Page] = {}

    def get_page(self, page_num: int) -> Page:
        """
        Return a page from cache or load from disk if not present.
        Newly allocated pages are always zeroed to prevent phantom rows.
        """
        if page_num in self.cache:
            return self.cache[page_num]

        # Attempt to read page from disk
        try:
            data = self.file_manager.read_page(page_num, self.page_size)
        except FileNotFoundError:
            data = None  # page does not exist yet

        # Create a new Page in memory
        page = Page(self.page_size)

        if not data or all(b == 0 for b in data):
            # New page or completely empty → zero out
            page.clear()
        else:
            # Existing page → load data
            page.write(0, data)

        self.cache[page_num] = page
        return page

    def flush_page(self, page_num: int) -> None:
        """
        Write cached page back to disk.
        """
        if page_num not in self.cache:
            return
        page = self.cache[page_num]
        self.file_manager.write_page(page_num, page.data)

    def iter_pages(self, file_id: int) -> Iterator[Page]:
        """
        Iterate through pages starting from file_id until an empty page is reached.
        """
        page_num = file_id
        while True:
            page = self.get_page(page_num)
            if all(b == 0 for b in page.data):
                break
            yield page
            page_num += 1
