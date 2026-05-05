from abc import ABC, abstractmethod
from pathlib import Path


class BlobStorage(ABC):
    @abstractmethod
    async def read_text(self, path: str) -> str: ...


class FileSystemBlobStorage(BlobStorage):
    def __init__(self, base_path: Path = Path("data/blobs")):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def read_text(self, path: str) -> str:
        full_path = self.base_path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Blob not found: {path}")
        return full_path.read_text(encoding="utf-8")
