"""Local stub shim for the chromadb package used in tests."""


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
