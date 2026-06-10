"""apps_rg Chroma client helper — E2E-11 recovery wiring."""

from __future__ import annotations

import pytest

from apps_rg.runtime.c0.chroma_persistent_client import (
    ensure_apps_rg_chroma_client,
    reset_apps_rg_chroma_client_cache_for_tests,
)
from tools.retrieval.vector_errors import VectorUnavailableError
from tools.retrieval.vector_store import ChromaVectorStore


class _Live:
    def heartbeat(self):
        return 1

    def clear_system_cache(self):
        pass


class _Dead:
    def heartbeat(self):
        raise AttributeError("'RustBindingsAPI' object has no attribute 'bindings'")

    def clear_system_cache(self):
        pass


class _SeqLoader:
    def __init__(self, clients):
        self._clients = list(clients)
        self._i = 0

    def get(self, wait_timeout=None):
        return self._clients[self._i] if self._i < len(self._clients) else None

    def invalidate(self):
        self._i += 1

    def is_loading(self):
        return False


def test_ensure_apps_rg_chroma_client_rebuilds_dead_client(tmp_path, monkeypatch):
    reset_apps_rg_chroma_client_cache_for_tests()
    chroma_dir = tmp_path / "chroma"
    chroma_dir.mkdir()
    live = _Live()
    store = ChromaVectorStore(chroma_path=chroma_dir)
    store._loader = _SeqLoader([_Dead(), live])
    monkeypatch.setattr(
        "apps_rg.runtime.c0.chroma_persistent_client.ChromaVectorStore",
        lambda chroma_path: store,
    )
    client = ensure_apps_rg_chroma_client(str(chroma_dir))
    assert client is live


def test_ensure_apps_rg_chroma_client_raises_on_empty_path():
    with pytest.raises(ValueError, match="chroma_path"):
        ensure_apps_rg_chroma_client("")


def test_real_persistent_client_recovers_via_apps_rg_helper(tmp_path):
    pytest.importorskip("chromadb")
    reset_apps_rg_chroma_client_cache_for_tests()
    chroma_dir = tmp_path / "chroma"
    c1 = ensure_apps_rg_chroma_client(str(chroma_dir))
    assert c1.heartbeat()

    close_fn = getattr(c1, "close", None)
    if not callable(close_fn):
        pytest.skip("this chromadb build has no client.close()")
    close_fn()

    c2 = ensure_apps_rg_chroma_client(str(chroma_dir))
    assert c2.heartbeat()
    assert isinstance(c2.list_collections(), list)
