"""W1 unit + integration tests: ChromaVectorStore rebuilds a dead client.

E2E-11: a shared ChromaDB PersistentClient torn down between sequential lane queries
raises ``'RustBindingsAPI' object has no attribute 'bindings'`` on its next call. The
store must detect the dead client (liveness probe), clear the system cache, rebuild, and
re-probe -- failing cleanly with VectorUnavailableError if recovery is impossible rather
than returning a dead client that would cascade-abort the integrated run.
"""
from __future__ import annotations

import pytest

from tools.retrieval.vector_errors import VectorUnavailableError
from tools.retrieval.vector_store import ChromaVectorStore


class _Live:
    def heartbeat(self):
        return 1

    def clear_system_cache(self):  # no-op so tests don't touch real chroma cache
        pass


class _Dead:
    def heartbeat(self):
        raise AttributeError("'RustBindingsAPI' object has no attribute 'bindings'")

    def clear_system_cache(self):
        pass


class _SeqLoader:
    """Returns clients in sequence; invalidate() advances. None entries model load failure."""

    def __init__(self, clients):
        self._clients = list(clients)
        self._i = 0

    def get(self, wait_timeout=None):
        return self._clients[self._i] if self._i < len(self._clients) else None

    def invalidate(self):
        self._i += 1

    def is_loading(self):
        return False


def test_client_is_alive_detects_dead_bindings():
    assert ChromaVectorStore._client_is_alive(_Live()) is True
    assert ChromaVectorStore._client_is_alive(_Dead()) is False
    # No heartbeat method -> cannot probe -> assume alive (don't churn unknown clients).
    assert ChromaVectorStore._client_is_alive(object()) is True


def test_ensure_client_rebuilds_dead_client():
    store = ChromaVectorStore()
    live = _Live()
    store._loader = _SeqLoader([_Dead(), live])
    assert store.ensure_client() is live  # advanced past the dead client and re-probed alive


def test_ensure_client_returns_live_without_rebuild():
    store = ChromaVectorStore()
    live = _Live()
    store._loader = _SeqLoader([live])
    assert store.ensure_client() is live


def test_ensure_client_raises_when_rebuild_returns_none():
    # Dead client, and the rebuild load fails (get -> None): must fail cleanly, not crash.
    store = ChromaVectorStore()
    store._loader = _SeqLoader([_Dead(), None])
    with pytest.raises(VectorUnavailableError):
        store.ensure_client()


def test_ensure_client_raises_when_rebuild_still_dead():
    # Dead client, and the rebuilt client is STILL dead (persistent teardown): re-probe
    # must catch it and raise rather than return a dead client (the cascade-abort path).
    store = ChromaVectorStore()
    store._loader = _SeqLoader([_Dead(), _Dead()])
    with pytest.raises(VectorUnavailableError):
        store.ensure_client()


def test_real_persistent_client_recovers_after_close(tmp_path):
    """Integration: a real ChromaDB client, closed (use-after-close), is rebuilt live."""
    pytest.importorskip("chromadb")
    store = ChromaVectorStore(chroma_path=tmp_path / "chroma")
    c1 = store.ensure_client()
    assert c1.heartbeat()  # alive

    close_fn = getattr(c1, "close", None)
    if not callable(close_fn):
        pytest.skip("this chromadb build has no client.close()")
    close_fn()  # the documented use-after-close teardown

    c2 = store.ensure_client()  # must detect dead client + rebuild
    assert c2.heartbeat()  # recovered
    assert isinstance(c2.list_collections(), list)
