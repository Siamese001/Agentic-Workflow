"""Path-scoped Chroma PersistentClient with E2E-11 liveness recovery.

W1 (apps-rg-aig-e2e-remediation-e4b7c1) added ``ChromaVectorStore.ensure_client`` in
``tools/retrieval/vector_store.py`` but apps_rg dense-retrieval paths still created
ephemeral ``chromadb.PersistentClient`` instances. After the shared Chroma system is torn
down between sequential integrated lanes, the next lane raises
``'RustBindingsAPI' object has no attribute 'bindings'`` and cascades phase-1 abort.

This module is the apps_rg SSOT for obtaining a live client at a persist path.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from tools.retrieval.vector_store import ChromaVectorStore

_lock = threading.Lock()
_stores_by_path: dict[str, ChromaVectorStore] = {}


def ensure_apps_rg_chroma_client(chroma_path: str) -> Any:
    """Return a live Chroma PersistentClient for ``chroma_path``, rebuilding if torn down."""
    path = str(chroma_path or "").strip()
    if not path:
        raise ValueError("chroma_path is required")
    key = str(Path(path).resolve())
    with _lock:
        store = _stores_by_path.get(key)
        if store is None:
            store = ChromaVectorStore(chroma_path=Path(key))
            _stores_by_path[key] = store
    return store.ensure_client()


def reset_apps_rg_chroma_client_cache_for_tests() -> None:
    """Clear path-scoped store cache (tests only)."""
    with _lock:
        _stores_by_path.clear()


__all__ = [
    "ensure_apps_rg_chroma_client",
    "reset_apps_rg_chroma_client_cache_for_tests",
]
