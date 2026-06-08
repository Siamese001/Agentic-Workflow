"""W2 / PR3: C0.2 status truth (G6) + embedding parity (G9).

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

- G6: a dense lane must never report PASS with zero selected evidence (PASS-but-empty is invalid).
- G9: a stored-vs-query embedding dimension mismatch must fail loud (silent zero/garbage otherwise).

Pure product-mode unit tests (no APPS_RG_TEST_HARNESS, no real Chroma).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.c0 import c02_product_hybrid_retrieval as c02mod
from apps_rg.runtime.chroma_precomputed_collection import (
    EXPECTED_BGE_DIMENSION,
    assert_collection_embedding_parity,
)


# --------------------------- G9: embedding parity ---------------------------

class _PeekCollection:
    def __init__(self, embeddings, *, raise_on_peek: bool = False) -> None:
        self._embeddings = embeddings
        self._raise = raise_on_peek

    def peek(self, limit: int = 1):
        if self._raise:
            raise RuntimeError("peek not supported in this chroma version")
        return {"embeddings": self._embeddings}


def test_parity_raises_on_dimension_mismatch() -> None:
    collection = _PeekCollection([[0.0] * 384])  # MiniLM-style 384-dim
    with pytest.raises(RuntimeError) as excinfo:
        assert_collection_embedding_parity(collection)
    msg = str(excinfo.value)
    assert "parity violation" in msg
    assert "384-dim" in msg
    assert "bootstrap fact-vectors" in msg


def test_parity_ok_on_canonical_dimension() -> None:
    collection = _PeekCollection([[0.1] * EXPECTED_BGE_DIMENSION])
    assert_collection_embedding_parity(collection) is None


def test_parity_noop_on_empty_collection() -> None:
    assert assert_collection_embedding_parity(_PeekCollection([])) is None
    assert assert_collection_embedding_parity(_PeekCollection(None)) is None


def test_parity_fail_soft_when_peek_unavailable() -> None:
    assert assert_collection_embedding_parity(_PeekCollection([], raise_on_peek=True)) is None


def test_parity_handles_numpy_embeddings_without_truthiness_error() -> None:
    """Regression: Chroma peek() returns embeddings as a numpy array — must not raise
    'truth value of an array is ambiguous' (live AIG run, full_resume_a0c41812fbd0)."""
    np = pytest.importorskip("numpy")
    # Canonical dim as a 2-D numpy array -> no error, no raise.
    ok = _PeekCollection(np.zeros((1, EXPECTED_BGE_DIMENSION), dtype="float32"))
    assert assert_collection_embedding_parity(ok) is None
    # Wrong dim as a numpy array -> the parity violation still fires (not a truthiness crash).
    bad = _PeekCollection(np.zeros((1, 384), dtype="float32"))
    with pytest.raises(RuntimeError) as excinfo:
        assert_collection_embedding_parity(bad)
    assert "parity violation" in str(excinfo.value)


# --------------------------- G6: PASS-but-empty ---------------------------

def test_pass_but_empty_dense_lane_raises(monkeypatch, tmp_path) -> None:
    import chromadb

    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

    monkeypatch.setattr(c02mod, "product_hybrid_retrieval_required", lambda section_id: True)
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path))
    monkeypatch.setattr(
        "apps_rg.runtime.embedding_settings.apply_apps_rg_embedding_env_guards",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.embedding_settings.resolve_apps_rg_embedding_settings",
        lambda **kwargs: SimpleNamespace(route_result="CONTINUE", decisive_reason=""),
    )
    monkeypatch.setattr("chromadb.PersistentClient", lambda **kwargs: object())
    monkeypatch.setattr(
        "apps_rg.runtime.chroma_precomputed_collection.get_precomputed_embeddings_collection_for_query",
        lambda client, name: object(),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.chroma_precomputed_collection.assert_collection_embedding_parity",
        lambda collection, **kwargs: None,
    )
    # The contract-violating case: status PASS but zero selected evidence.
    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_binding._perform_bounded_section_retrieval",
        lambda *args, **kwargs: ([], [], "PASS", [], [], []),
    )

    with pytest.raises(C0EvidenceGapError) as excinfo:
        c02mod.perform_product_hybrid_retrieval(
            section_id="competencies",
            app_payload={},
            evidence_digest="digest",
            timestamp_iso="2026-06-08T00:00:00Z",
        )
    assert "PASS with zero selected evidence" in str(excinfo.value)
