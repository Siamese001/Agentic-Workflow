"""Local stub shim for the chromadb package used in tests."""

from vendor.chromadb_stub import (
    Client,
    Collection,
    HttpClient,
    PersistentClient,
    embedding_functions as _embedding_functions,
)

__all__ = [
    "Client",
    "Collection",
    "HttpClient",
    "PersistentClient",
    "embedding_functions",
]


class utils:  # pragma: no cover - namespace compatibility
    embedding_functions = _embedding_functions


embedding_functions = _embedding_functions
