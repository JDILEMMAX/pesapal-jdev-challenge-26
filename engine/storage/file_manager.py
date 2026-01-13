from pathlib import Path
from typing import Union
from engine.exceptions import EngineError


class FileManager:
    """
    Handles low-level file operations for the storage engine.
    Manages reading/writing pages to disk.
    """

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def read_page(self, page_num: int, page_size: int) -> bytes:
        try:
            with self.path.open("rb") as f:
                f.seek(page_num * page_size)
                data = f.read(page_size)
                if len(data) < page_size:
                    # pad with zeros if file is smaller than requested
                    data += b"\x00" * (page_size - len(data))
                return data
        except Exception as e:
            raise EngineError(f"Failed to read page {page_num}") from e

    def write_page(self, page_num: int, data: bytes) -> None:
        try:
            with self.path.open("r+b") as f:
                f.seek(page_num * len(data))
                f.write(data)
        except FileNotFoundError:
            # File might be empty; create and write
            with self.path.open("wb") as f:
                f.seek(page_num * len(data))
                f.write(data)
        except Exception as e:
            raise EngineError(f"Failed to write page {page_num}") from e

    def flush(self) -> None:
        """For explicit syncing; in simple implementation, no-op."""
        pass
