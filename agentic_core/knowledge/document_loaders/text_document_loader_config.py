import logging
from pathlib import Path

# Configuration constants

log = logging.getLogger(__name__)


class TextDocumentLoader:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    def load(self) -> str:
        return self.file_path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def load_file(file_path: Path) -> str:
        return Path(file_path).read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def load_path(path: Path) -> str:
        return TextDocumentLoader.load_file(path)
