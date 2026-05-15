"""Profile-driven sparse index resolution (generic core, neutral names)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L4_state.utils.memory import bm25_store


def test_get_sparse_index_accepts_sidecar_name_outside_allowlist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Any collection with ``<name>.db`` under sparse cache dir resolves (no app literals)."""
    coll = "neutral_fixture_collection"
    db = tmp_path / f"{coll}.db"
    db.write_bytes(b"")
    monkeypatch.setattr(bm25_store, "_SPARSE_DIR", tmp_path)
    monkeypatch.setattr(bm25_store, "_sparse_index_cache", {})
    assert bm25_store.sparse_sidecar_exists(coll) is True
    idx = bm25_store.get_sparse_index(coll)
    assert idx is not None
    assert idx.collection_name == coll


def test_get_sparse_index_returns_none_when_sidecar_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bm25_store, "_SPARSE_DIR", Path("/nonexistent/sparse/cache"))
    monkeypatch.setattr(bm25_store, "_sparse_index_cache", {})
    assert bm25_store.get_sparse_index("not_in_allowlist_xyz") is None
