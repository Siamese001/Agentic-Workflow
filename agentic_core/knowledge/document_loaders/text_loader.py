"""Legacy compatibility shim — re-exports TextDocumentLoader from canonical location."""
from agentic_core.knowledge.document_loaders.text_document_loader_config import TextDocumentLoader
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = ['TextDocumentLoader']
