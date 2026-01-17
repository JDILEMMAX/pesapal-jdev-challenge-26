from engine.storage.page import Page
from engine.storage.file_manager import FileManager
from typing import Dict, Iterator
from engine.exceptions import EngineError


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
        """
        if page_num in self.cache:
            return self.cache[page_num]

        data = self.file_manager.read_page(page_num, self.page_size)
        page = Page(self.page_size)
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
        page_num = file_id

        while True:
            page = self.get_page(page_num)

            # empty page → stop
            if all(b == 0 for b in page.data):
                break

            yield page
            page_num += 1
