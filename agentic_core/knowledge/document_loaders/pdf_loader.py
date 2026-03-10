"""Legacy compatibility shim — re-exports PDFDocumentLoader from canonical location."""

from agentic_core.knowledge.document_loaders.pdf_document_loader_config import PDFDocumentLoader

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["PDFDocumentLoader"]
