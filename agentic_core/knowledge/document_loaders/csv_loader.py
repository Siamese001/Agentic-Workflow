"""Legacy compatibility shim — aliases CsvDocumentLoader as CSVDocumentLoader."""

from agentic_core.knowledge.document_loaders.csv_document_loader_config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    CsvDocumentLoader as _CsvDocumentLoader,
)


class CSVDocumentLoader(_CsvDocumentLoader):
    """Legacy alias preserving the ALL-CAPS naming convention used by callers."""

    pass


__all__ = ["CSVDocumentLoader"]
