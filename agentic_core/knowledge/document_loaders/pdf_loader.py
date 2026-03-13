"""Legacy compatibility shim — re-exports PDFDocumentLoader from canonical location."""

from agentic_core.knowledge.document_loaders.pdf_document_loader_config import PDFDocumentLoader

__all__ = ["PDFDocumentLoader"]
