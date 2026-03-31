import logging
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
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
