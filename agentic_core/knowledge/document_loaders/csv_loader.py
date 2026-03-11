"""Legacy compatibility shim — aliases CsvDocumentLoader as CSVDocumentLoader."""

from agentic_core.knowledge.document_loaders.csv_document_loader_config import (
    CsvDocumentLoader as _CsvDocumentLoader,
)


class CSVDocumentLoader(_CsvDocumentLoader):
    """Legacy alias preserving the ALL-CAPS naming convention used by callers."""

    pass


__all__ = ["CSVDocumentLoader"]
