"""Legacy compatibility shim — re-exports TextDocumentLoader from canonical location."""

from agentic_core.knowledge.document_loaders.text_document_loader_config import TextDocumentLoader

__all__ = ["TextDocumentLoader"]
