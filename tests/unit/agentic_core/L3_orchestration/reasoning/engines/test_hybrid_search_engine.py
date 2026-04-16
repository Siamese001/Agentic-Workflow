"""Wave D2.1 unit tests for BM25 lexical backend + RRF fusion.

Coverage requirements (Wave D plan §3 Slice D2.1 and the D2.1 prompt):

1. BM25 backend returns lexical matches deterministically
2. fusion combines dense + lexical results into one ranked list
3. dense-only fallback works (BM25 empty)
4. BM25-only fallback works (dense empty)
5. result ordering is stable and serializable

Plus non-regression:
- default call (enable_lexical=False) is byte-identical to pre-D2.1 behavior
- signature stays usable by existing callers (141 call-sites surveyed)
"""

from __future__ import annotations

import inspect
import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from agentic_core.L3_orchestration.reasoning.engines import (
    hybrid_search_engine as hse_module,
)
from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _vec_result(
    chunk_id: str,
    *,
    combined_score: float = 0.5,
    content: str = "",
    metadata: dict[str, Any] | None = None,
) -> HybridSearchResult:
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=content or f"vector-content-{chunk_id}",
        metadata=dict(metadata or {"origin": "vector"}),
        combined_score=combined_score,
        source="vector",
        vector_score=combined_score,
        lexical_score=0.0,
    )


def _lex_result(
    chunk_id: str,
    *,
    combined_score: float = 0.5,
    content: str = "",
    metadata: dict[str, Any] | None = None,
) -> HybridSearchResult:
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=content or f"lexical-content-{chunk_id}",
        metadata=dict(metadata or {"origin": "lexical"}),
        combined_score=combined_score,
        source="lexical",
        vector_score=0.0,
        lexical_score=combined_score,
    )


class _StubSparseIndex:
    """Deterministic stand-in for ``SparseIndex`` used in unit tests.

    Avoids touching the on-disk sidecar DBs so the test suite is hermetic
    and runnable in CI containers without ``data/cache/sparse/*.db``.
    """

    def __init__(self, hits: list[dict[str, Any]], *, available: bool = True):
        self._hits = list(hits)
        self._available = available
        self.search_calls: list[tuple[str, int]] = []

    @property
    def is_available(self) -> bool:
        return self._available

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        self.search_calls.append((query, top_k))
        return list(self._hits)


def _fake_chroma_client_for(rows: list[tuple[str, str, dict[str, Any], float]]):
    """Build a chroma-style client that returns the requested (id, doc, meta, distance) rows."""
    ids = [r[0] for r in rows]
    docs = [r[1] for r in rows]
    metas = [r[2] for r in rows]
    distances = [r[3] for r in rows]
    fake_col = MagicMock()
    fake_col.query.return_value = {
        "ids": [ids],
        "documents": [docs],
        "metadatas": [metas],
        "distances": [distances],
    }
    fake_client = MagicMock()
    fake_client.get_collection.return_value = fake_col
    return fake_client


# ---------------------------------------------------------------------------
# Requirement 1 — BM25 backend returns lexical matches deterministically
# ---------------------------------------------------------------------------


class TestLexicalBackendReturnsDeterministicMatches:
    def test_lexical_search_maps_sparse_hits_to_hybrid_results(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [
            {
                "id": "a",
                "content": "alpha document",
                "score": 0.9,
                "metadata": {"layer": "L3"},
                "source": "sparse_fts",
            },
            {
                "id": "b",
                "content": "bravo document",
                "score": 0.4,
                "metadata": {"layer": "L2"},
                "source": "sparse_fts",
            },
        ]
        stub = _StubSparseIndex(hits)

        def _fake_get_sparse_index(name: str) -> Any:
            return stub

        import agentic_core.L4_state.utils.memory.bm25_store as bm25_mod

        monkeypatch.setattr(bm25_mod, "get_sparse_index", _fake_get_sparse_index)

        engine = HybridSearchEngine()
        out = engine._lexical_search("alpha bravo", collection_name="code_chunks", governance_filter=None)
        assert [r.chunk_id for r in out] == ["a", "b"]
        assert out[0].source == "lexical"
        assert out[0].lexical_score == pytest.approx(0.9)
        assert out[0].vector_score == 0.0
        assert out[0].metadata == {"layer": "L3"}
        assert out[1].combined_score == pytest.approx(0.4)

    def test_lexical_search_is_deterministic_across_invocations(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        hits = [
            {"id": "x", "content": "x", "score": 0.8, "metadata": {}, "source": "s"},
            {"id": "y", "content": "y", "score": 0.3, "metadata": {}, "source": "s"},
        ]
        stub = _StubSparseIndex(hits)
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: stub,
        )

        engine = HybridSearchEngine()
        a = engine._lexical_search("q", "code_chunks", None)
        b = engine._lexical_search("q", "code_chunks", None)
        assert [r.chunk_id for r in a] == [r.chunk_id for r in b]
        assert [r.combined_score for r in a] == [r.combined_score for r in b]

    def test_lexical_search_returns_empty_when_index_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: None,
        )
        engine = HybridSearchEngine()
        assert engine._lexical_search("q", "unknown_collection", None) == []

    def test_lexical_search_returns_empty_when_index_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stub = _StubSparseIndex([], available=False)
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: stub,
        )
        engine = HybridSearchEngine()
        assert engine._lexical_search("q", "code_chunks", None) == []

    def test_lexical_search_swallows_sidecar_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _RaisingIndex:
            @property
            def is_available(self) -> bool:
                return True

            def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
                raise RuntimeError("simulated sqlite corruption")

        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _RaisingIndex(),
        )
        engine = HybridSearchEngine()
        # Must NOT raise — lexical failure is soft per the D2.1 contract.
        assert engine._lexical_search("q", "code_chunks", None) == []

    def test_lexical_search_empty_query_returns_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # The normalize_query branch short-circuits BEFORE any sidecar work.
        # Force-assert this by poisoning get_sparse_index to raise.
        def _explode(_n: str) -> Any:
            raise AssertionError("should not reach sparse backend for empty query")

        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            _explode,
        )
        engine = HybridSearchEngine()
        assert engine._lexical_search("", "code_chunks", None) == []
        assert engine._lexical_search("   ", "code_chunks", None) == []
        assert engine._lexical_search(None, "code_chunks", None) == []  # type: ignore[arg-type]

    def test_lexical_search_applies_governance_filter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [
            {
                "id": "keep",
                "content": "c",
                "score": 0.9,
                "metadata": {"layer": "L3"},
                "source": "s",
            },
            {
                "id": "drop",
                "content": "c",
                "score": 0.8,
                "metadata": {"layer": "L0"},
                "source": "s",
            },
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        engine = HybridSearchEngine()
        out = engine._lexical_search("q", "code_chunks", governance_filter={"layers": ["L3"]})
        assert [r.chunk_id for r in out] == ["keep"]


# ---------------------------------------------------------------------------
# Requirement 2 — fusion combines dense + lexical into one ranked list
# ---------------------------------------------------------------------------


class TestRrfFusion:
    def test_rrf_fuses_disjoint_result_sets(self) -> None:
        vec = [_vec_result("v1"), _vec_result("v2")]
        lex = [_lex_result("l1"), _lex_result("l2")]
        fused = HybridSearchEngine._rrf_fuse(vec, lex, k=60)
        assert {r.chunk_id for r in fused} == {"v1", "v2", "l1", "l2"}
        # rank-1 entries (v1, l1) must outrank rank-2 entries (v2, l2).
        rank_by_id = {r.chunk_id: i for i, r in enumerate(fused)}
        assert rank_by_id["v1"] < rank_by_id["v2"]
        assert rank_by_id["l1"] < rank_by_id["l2"]

    def test_rrf_boosts_items_present_in_both_lists(self) -> None:
        # "shared" is rank-1 in both lists -> should get the highest fused score.
        vec = [_vec_result("shared"), _vec_result("vec_only")]
        lex = [_lex_result("shared"), _lex_result("lex_only")]
        fused = HybridSearchEngine._rrf_fuse(vec, lex, k=60)
        top = fused[0]
        assert top.chunk_id == "shared"
        assert top.source == "hybrid"
        # Fused score for shared = 1/61 + 1/61 = 2/61
        assert top.combined_score == pytest.approx(2.0 / 61.0)

    def test_rrf_preserves_per_list_scores(self) -> None:
        vec = [_vec_result("shared", combined_score=0.77)]
        lex = [_lex_result("shared", combined_score=0.33)]
        [fused_shared] = HybridSearchEngine._rrf_fuse(vec, lex, k=60)
        assert fused_shared.vector_score == pytest.approx(0.77)
        assert fused_shared.lexical_score == pytest.approx(0.33)
        # combined_score becomes the RRF score, NOT the per-list score.
        assert fused_shared.combined_score == pytest.approx(2.0 / 61.0)

    def test_rrf_source_tagging(self) -> None:
        vec = [_vec_result("both"), _vec_result("vonly")]
        lex = [_lex_result("both"), _lex_result("lonly")]
        fused = HybridSearchEngine._rrf_fuse(vec, lex)
        src_by_id = {r.chunk_id: r.source for r in fused}
        assert src_by_id["both"] == "hybrid"
        assert src_by_id["vonly"] == "vector"
        assert src_by_id["lonly"] == "lexical"

    def test_rrf_metadata_prefers_vector_side_when_both_present(self) -> None:
        vec = [_vec_result("both", metadata={"from": "vector", "richness": "high"})]
        lex = [_lex_result("both", metadata={"from": "lexical"})]
        [fused] = HybridSearchEngine._rrf_fuse(vec, lex)
        assert fused.metadata == {"from": "vector", "richness": "high"}

    def test_rrf_ordering_is_deterministic_with_ties(self) -> None:
        # Rank-1 and rank-2 within one list get different RRF scores (no
        # real tie); use a ties-only scenario below to exercise the
        # chunk_id ascending tie-break.
        vec_tied = [_vec_result("charlie", combined_score=0.5)]
        lex_tied = [_lex_result("charlie", combined_score=0.5)]
        fused_tied = HybridSearchEngine._rrf_fuse(vec_tied, lex_tied)
        assert len(fused_tied) == 1
        assert fused_tied[0].chunk_id == "charlie"

        # Explicit ordering-tie scenario: two chunks each appearing at rank-1
        # exclusively in one list each -> identical RRF score 1/61.
        vec_one = [_vec_result("zzz")]
        lex_one = [_lex_result("aaa")]
        fused_tie = HybridSearchEngine._rrf_fuse(vec_one, lex_one)
        # Both earn RRF score 1/61 -> chunk_id ascending tiebreak -> "aaa" first.
        assert [r.chunk_id for r in fused_tie] == ["aaa", "zzz"]

    def test_rrf_empty_inputs_return_empty_list(self) -> None:
        assert HybridSearchEngine._rrf_fuse([], []) == []

    def test_rrf_deduplicates_chunk_id_within_each_list(self) -> None:
        # If the caller forgot to dedup, RRF must still use first-seen rank.
        vec = [
            _vec_result("dup", combined_score=0.9),
            _vec_result("dup", combined_score=0.1),
            _vec_result("other"),
        ]
        lex: list[HybridSearchResult] = []
        fused = HybridSearchEngine._rrf_fuse(vec, lex)
        chunk_ids = [r.chunk_id for r in fused]
        assert chunk_ids.count("dup") == 1
        assert set(chunk_ids) == {"dup", "other"}


# ---------------------------------------------------------------------------
# Requirement 3 — dense-only fallback works (BM25 empty)
# ---------------------------------------------------------------------------


class TestDenseOnlyFallback:
    def test_search_default_behavior_unchanged_without_enable_lexical(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Default call (enable_lexical not supplied) MUST behave exactly as
        # pre-D2.1: dense-only, no sparse probe, no lexical_score.
        def _explode(_n: str) -> Any:
            raise AssertionError("lexical backend must not be invoked when enable_lexical=False")

        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            _explode,
        )

        fake_client = _fake_chroma_client_for([("v1", "d1", {}, 0.1), ("v2", "d2", {}, 0.3)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks")
        assert [r.chunk_id for r in results] == ["v1", "v2"]
        assert all(r.source == "vector" for r in results)
        assert all(r.lexical_score == 0.0 for r in results)

    def test_search_dense_only_when_lexical_enabled_but_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # enable_lexical=True, but sparse sidecar returns no hits -> fall
        # through to the byte-identical dense-only path.
        stub = _StubSparseIndex([])
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: stub,
        )

        fake_client = _fake_chroma_client_for([("v1", "d1", {}, 0.1), ("v2", "d2", {}, 0.4)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        assert [r.chunk_id for r in results] == ["v1", "v2"]
        assert all(r.source == "vector" for r in results)
        # Vector score semantics preserved: score = 1 - distance.
        assert results[0].combined_score == pytest.approx(0.9)
        assert results[1].combined_score == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Requirement 4 — BM25-only fallback works (dense empty)
# ---------------------------------------------------------------------------


class TestBm25OnlyFallback:
    def test_search_returns_lexical_when_chroma_client_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [
            {"id": "a", "content": "ca", "score": 0.9, "metadata": {}, "source": "s"},
            {"id": "b", "content": "cb", "score": 0.4, "metadata": {}, "source": "s"},
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        engine = HybridSearchEngine(chroma_client=None)
        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        assert [r.chunk_id for r in results] == ["a", "b"]
        assert all(r.source == "lexical" for r in results)
        assert results[0].lexical_score == pytest.approx(0.9)

    def test_search_returns_empty_when_both_backends_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex([]),
        )
        engine = HybridSearchEngine(chroma_client=None)
        assert engine.search("q", collection_name="code_chunks", enable_lexical=True) == []


# ---------------------------------------------------------------------------
# Requirement 2 (continued) — fusion inside search()
# ---------------------------------------------------------------------------


class TestSearchFusesWhenBothBackendsProduceResults:
    def test_search_rrf_fuses_vector_and_lexical(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Vector hits: v1, v2. Lexical hits: l1, l2. Fully disjoint.
        hits = [
            {"id": "l1", "content": "cl1", "score": 0.9, "metadata": {}, "source": "s"},
            {"id": "l2", "content": "cl2", "score": 0.6, "metadata": {}, "source": "s"},
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        fake_client = _fake_chroma_client_for([("v1", "cv1", {}, 0.1), ("v2", "cv2", {}, 0.3)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        ids = {r.chunk_id for r in results}
        assert ids == {"v1", "v2", "l1", "l2"}

        # Rank-1 entries from each list come before rank-2 entries.
        idx = {r.chunk_id: i for i, r in enumerate(results)}
        assert idx["v1"] < idx["v2"]
        assert idx["l1"] < idx["l2"]

    def test_search_rrf_boosts_shared_chunks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # "shared" appears rank-1 in both lists -> top of the fused output.
        hits = [
            {
                "id": "shared",
                "content": "c",
                "score": 0.9,
                "metadata": {},
                "source": "s",
            },
            {
                "id": "lex_only",
                "content": "c",
                "score": 0.5,
                "metadata": {},
                "source": "s",
            },
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        fake_client = _fake_chroma_client_for([("shared", "c", {}, 0.1), ("vec_only", "c", {}, 0.3)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        assert results[0].chunk_id == "shared"
        assert results[0].source == "hybrid"


# ---------------------------------------------------------------------------
# Requirement 5 — result ordering is stable and serializable
# ---------------------------------------------------------------------------


class TestResultOrderingStableAndSerializable:
    def test_fused_results_are_json_serializable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from dataclasses import asdict

        hits = [
            {"id": "a", "content": "ca", "score": 0.9, "metadata": {"k": 1}, "source": "s"},
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        fake_client = _fake_chroma_client_for([("b", "cb", {}, 0.2)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        # HybridSearchResult is a dataclass; asdict round-trips through JSON.
        payload = [asdict(r) for r in results]
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)
        assert decoded == payload

    def test_fused_results_are_stably_ordered_across_runs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [
            {"id": "x", "content": "c", "score": 0.9, "metadata": {}, "source": "s"},
            {"id": "y", "content": "c", "score": 0.4, "metadata": {}, "source": "s"},
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        fake_client = _fake_chroma_client_for([("v1", "c", {}, 0.1), ("v2", "c", {}, 0.3)])
        engine_a = HybridSearchEngine(chroma_client=fake_client)
        engine_a._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])
        engine_b = HybridSearchEngine(chroma_client=fake_client)
        engine_b._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        ids_a = [r.chunk_id for r in engine_a.search("q", collection_name="code_chunks", enable_lexical=True)]
        ids_b = [r.chunk_id for r in engine_b.search("q", collection_name="code_chunks", enable_lexical=True)]
        assert ids_a == ids_b

    def test_fused_result_field_types_are_primitives(self, monkeypatch: pytest.MonkeyPatch) -> None:
        hits = [
            {"id": "a", "content": "ca", "score": 0.9, "metadata": {"k": 1}, "source": "s"},
        ]
        monkeypatch.setattr(
            "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
            lambda _n: _StubSparseIndex(hits),
        )
        fake_client = _fake_chroma_client_for([("b", "cb", {}, 0.2)])
        engine = HybridSearchEngine(chroma_client=fake_client)
        engine._bge_model = MagicMock(encode=lambda q: [[0.1] * 4])

        results = engine.search("q", collection_name="code_chunks", enable_lexical=True)
        for r in results:
            assert isinstance(r.chunk_id, str)
            assert isinstance(r.content, str)
            assert isinstance(r.metadata, dict)
            assert isinstance(r.combined_score, float)
            assert isinstance(r.vector_score, float)
            assert isinstance(r.lexical_score, float)
            assert isinstance(r.source, str)
            assert r.source in {"vector", "lexical", "hybrid"}


# ---------------------------------------------------------------------------
# Non-regression — signature stability
# ---------------------------------------------------------------------------


class TestSignatureStability:
    def test_search_retains_existing_parameters(self) -> None:
        sig = inspect.signature(HybridSearchEngine.search)
        params = sig.parameters
        # Pre-D2.1 parameter set must still be present with their defaults.
        assert "query" in params
        assert "query_embedding" in params
        assert "collection_name" in params and params["collection_name"].default == "code_chunks"
        assert "governance_filter" in params and params["governance_filter"].default is None
        assert "metadata_filter" in params and params["metadata_filter"].default is None
        assert "authority_rerank" in params and params["authority_rerank"].default is False
        assert "collapse_group_dedup_max" in params and params["collapse_group_dedup_max"].default is None

    def test_search_adds_enable_lexical_kwarg_with_false_default(self) -> None:
        sig = inspect.signature(HybridSearchEngine.search)
        assert "enable_lexical" in sig.parameters
        assert sig.parameters["enable_lexical"].default is False

    def test_rrf_k_constant_is_exposed_on_class(self) -> None:
        assert hasattr(HybridSearchEngine, "RRF_K")
        assert isinstance(HybridSearchEngine.RRF_K, int)
        assert HybridSearchEngine.RRF_K > 0

    def test_module_still_exposes_public_helpers(self) -> None:
        # hybrid_search convenience wrapper and get_global_hybrid_engine must
        # remain accessible — pre-D2.1 integration points surveyed in the
        # 141 call-sites scan.
        assert hasattr(hse_module, "hybrid_search")
        assert hasattr(hse_module, "get_global_hybrid_engine")
        assert hasattr(hse_module, "HybridSearchEngine")
        assert hasattr(hse_module, "HybridSearchResult")


# ===========================================================================
# Wave D2.2 — expand_results_with_parent_child (collapse-group parent lift)
# ===========================================================================


def _child_result(
    chunk_id: str,
    *,
    collapse_group: str,
    heading_path: str,
    combined_score: float = 0.5,
    extra_metadata: dict[str, Any] | None = None,
) -> HybridSearchResult:
    """Build a child-style HybridSearchResult with the two linkage fields."""
    meta: dict[str, Any] = {
        "collapse_group": collapse_group,
        "heading_path": heading_path,
    }
    if extra_metadata:
        meta.update(extra_metadata)
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"content-{chunk_id}",
        metadata=meta,
        combined_score=combined_score,
        source="vector",
        vector_score=combined_score,
        lexical_score=0.0,
    )


# ---------------------------------------------------------------------------
# Requirement 1 — parent is added when linkage exists
# ---------------------------------------------------------------------------


class TestParentAddedWhenLinkageExists:
    def test_single_child_lifts_one_synthetic_parent(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="docs",
            heading_path="README > Installation > Prerequisites",
        )
        out = engine.expand_results_with_parent_child([child])
        # Synthetic parent prepended; child preserved at the tail.
        assert len(out) == 2
        assert out[0].source == "parent"
        assert out[0].metadata["heading_path"] == "README > Installation"
        assert out[0].metadata["collapse_group"] == "docs"
        assert out[0].metadata["is_synthetic_parent"] is True
        assert out[1] is child

    def test_parent_id_has_namespaced_prefix(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="fwk",
            heading_path="Root > Sub",
        )
        out = engine.expand_results_with_parent_child([child])
        assert out[0].chunk_id.startswith(HybridSearchEngine.PARENT_SYNTHETIC_PREFIX + ":")
        # Deterministic id contents: prefix, collapse_group, parent_path.
        assert out[0].chunk_id == "__parent__:fwk:Root"

    def test_parent_inherits_child_combined_score(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="docs",
            heading_path="A > B > C",
            combined_score=0.83,
        )
        [parent, _] = engine.expand_results_with_parent_child([child])
        assert parent.combined_score == pytest.approx(0.83)

    def test_parent_vector_and_lexical_scores_are_zero(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="docs",
            heading_path="A > B",
            combined_score=0.7,
        )
        [parent, _] = engine.expand_results_with_parent_child([child])
        assert parent.vector_score == 0.0
        assert parent.lexical_score == 0.0

    def test_grandparent_lifted_at_max_depth_two(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="docs",
            heading_path="A > B > C > D",
        )
        out = engine.expand_results_with_parent_child([child], max_depth=2)
        parents = [r for r in out if r.source == "parent"]
        paths = [p.metadata["heading_path"] for p in parents]
        assert "A > B > C" in paths  # depth 1 parent
        assert "A > B" in paths  # depth 2 grandparent
        depths = {p.metadata["heading_path"]: p.metadata["expansion_depth"] for p in parents}
        assert depths["A > B > C"] == 1
        assert depths["A > B"] == 2

    def test_max_depth_one_does_not_lift_grandparent(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result(
            "c1",
            collapse_group="docs",
            heading_path="A > B > C",
        )
        out = engine.expand_results_with_parent_child([child], max_depth=1)
        parents = [r for r in out if r.source == "parent"]
        assert len(parents) == 1
        assert parents[0].metadata["heading_path"] == "A > B"


# ---------------------------------------------------------------------------
# Requirement 2 — no-op when linkage is missing
# ---------------------------------------------------------------------------


class TestNoopWhenLinkageMissing:
    def test_empty_input_returns_empty_list(self) -> None:
        engine = HybridSearchEngine()
        assert engine.expand_results_with_parent_child([]) == []

    def test_missing_collapse_group_is_noop(self) -> None:
        engine = HybridSearchEngine()
        r = HybridSearchResult(
            chunk_id="c1",
            content="x",
            metadata={"heading_path": "A > B"},  # no collapse_group
            combined_score=0.5,
            source="vector",
        )
        out = engine.expand_results_with_parent_child([r])
        assert out == [r]

    def test_missing_heading_path_is_noop(self) -> None:
        engine = HybridSearchEngine()
        r = HybridSearchResult(
            chunk_id="c1",
            content="x",
            metadata={"collapse_group": "docs"},  # no heading_path
            combined_score=0.5,
            source="vector",
        )
        out = engine.expand_results_with_parent_child([r])
        assert out == [r]

    def test_single_segment_heading_path_is_noop(self) -> None:
        engine = HybridSearchEngine()
        r = _child_result("c1", collapse_group="docs", heading_path="RootOnly")
        out = engine.expand_results_with_parent_child([r])
        assert out == [r]

    def test_max_depth_zero_is_passthrough(self) -> None:
        engine = HybridSearchEngine()
        r = _child_result("c1", collapse_group="docs", heading_path="A > B > C")
        out = engine.expand_results_with_parent_child([r], max_depth=0)
        assert out == [r]

    def test_negative_max_depth_is_passthrough(self) -> None:
        engine = HybridSearchEngine()
        r = _child_result("c1", collapse_group="docs", heading_path="A > B > C")
        out = engine.expand_results_with_parent_child([r], max_depth=-5)
        assert out == [r]

    def test_heading_path_with_only_separators_is_noop(self) -> None:
        # "   >    >   " tokenizes to zero non-empty segments -> no parent.
        engine = HybridSearchEngine()
        r = _child_result("c1", collapse_group="docs", heading_path="   >    >   ")
        out = engine.expand_results_with_parent_child([r])
        # The stripped heading_path has 0 segments, so the segments<2 guard
        # triggers -> noop (no parent minted).
        assert out == [r]

    def test_none_metadata_is_noop_not_error(self) -> None:
        engine = HybridSearchEngine()
        r = HybridSearchResult(
            chunk_id="c1",
            content="x",
            metadata={},
            combined_score=0.5,
            source="vector",
        )
        out = engine.expand_results_with_parent_child([r])
        assert out == [r]


# ---------------------------------------------------------------------------
# Requirement 3 — duplicate parent expansion is deduped deterministically
# ---------------------------------------------------------------------------


class TestDuplicateParentDeduped:
    def test_two_children_sharing_parent_emit_one_synthetic(self) -> None:
        engine = HybridSearchEngine()
        a = _child_result("a", collapse_group="docs", heading_path="A > B > C1", combined_score=0.4)
        b = _child_result("b", collapse_group="docs", heading_path="A > B > C2", combined_score=0.9)
        out = engine.expand_results_with_parent_child([a, b])
        parents = [r for r in out if r.source == "parent"]
        assert len(parents) == 1
        assert parents[0].metadata["heading_path"] == "A > B"
        # Parent inherits the MAX child combined_score (deterministic).
        assert parents[0].combined_score == pytest.approx(0.9)

    def test_different_collapse_groups_do_not_merge(self) -> None:
        engine = HybridSearchEngine()
        a = _child_result("a", collapse_group="groupA", heading_path="A > B")
        b = _child_result("b", collapse_group="groupB", heading_path="A > B")
        out = engine.expand_results_with_parent_child([a, b])
        parents = [r for r in out if r.source == "parent"]
        assert len(parents) == 2
        collapse_groups = {p.metadata["collapse_group"] for p in parents}
        assert collapse_groups == {"groupA", "groupB"}

    def test_existing_parent_in_list_is_not_duplicated(self) -> None:
        engine = HybridSearchEngine()
        # "A > B" is the ACTUAL parent of "A > B > C" and is already in the list.
        existing_parent = _child_result(
            "real_parent",
            collapse_group="docs",
            heading_path="A > B",
            combined_score=0.6,
        )
        child = _child_result(
            "child",
            collapse_group="docs",
            heading_path="A > B > C",
            combined_score=0.8,
        )
        out = engine.expand_results_with_parent_child([existing_parent, child])
        # No synthetic row with heading_path "A > B" — the REAL parent is
        # already present, so minting a synthetic would duplicate it.
        synthetic_ab = [r for r in out if r.source == "parent" and r.metadata.get("heading_path") == "A > B"]
        assert synthetic_ab == []
        # Real parent + child are both preserved, in original order, at the
        # tail of the output (after any higher-level synthetic grandparents).
        real_tail = [r for r in out if r.source != "parent"]
        assert real_tail == [existing_parent, child]

    def test_parent_order_follows_first_seen_child(self) -> None:
        engine = HybridSearchEngine()
        # Two distinct parents; child_x is seen before child_y in input.
        cx = _child_result("cx", collapse_group="X", heading_path="Xroot > child")
        cy = _child_result("cy", collapse_group="Y", heading_path="Yroot > child")
        out = engine.expand_results_with_parent_child([cx, cy])
        parents = [r for r in out if r.source == "parent"]
        # Parent of cx (collapse_group=X) must appear before parent of cy.
        assert parents[0].metadata["collapse_group"] == "X"
        assert parents[1].metadata["collapse_group"] == "Y"


# ---------------------------------------------------------------------------
# Requirement 4 — original child results are preserved
# ---------------------------------------------------------------------------


class TestOriginalChildrenPreserved:
    def test_all_input_results_appear_in_output(self) -> None:
        engine = HybridSearchEngine()
        inputs = [
            _child_result("a", collapse_group="g", heading_path="R > a"),
            _child_result("b", collapse_group="g", heading_path="R > b"),
            _child_result("c", collapse_group="g", heading_path="R > c"),
        ]
        out = engine.expand_results_with_parent_child(inputs)
        out_ids = {r.chunk_id for r in out}
        for r in inputs:
            assert r.chunk_id in out_ids, f"input {r.chunk_id} was dropped"

    def test_original_child_order_preserved_after_synthetic_parents(self) -> None:
        engine = HybridSearchEngine()
        inputs = [
            _child_result("z", collapse_group="g", heading_path="R > z"),
            _child_result("a", collapse_group="g", heading_path="R > a"),
            _child_result("m", collapse_group="g", heading_path="R > m"),
        ]
        out = engine.expand_results_with_parent_child(inputs)
        # Strip synthetic parents; remaining order must equal input order.
        real = [r for r in out if r.source != "parent"]
        assert [r.chunk_id for r in real] == ["z", "a", "m"]

    def test_original_result_objects_are_not_mutated(self) -> None:
        engine = HybridSearchEngine()
        child = _child_result("c1", collapse_group="g", heading_path="A > B")
        original_metadata = dict(child.metadata)
        original_score = child.combined_score
        engine.expand_results_with_parent_child([child])
        assert child.metadata == original_metadata
        assert child.combined_score == original_score

    def test_input_list_is_not_mutated(self) -> None:
        engine = HybridSearchEngine()
        a = _child_result("a", collapse_group="g", heading_path="A > B")
        b = _child_result("b", collapse_group="g", heading_path="A > B > C")
        inputs = [a, b]
        inputs_snapshot = list(inputs)
        engine.expand_results_with_parent_child(inputs)
        assert inputs == inputs_snapshot


# ---------------------------------------------------------------------------
# Requirement 5 — expanded results remain serializable and stable
# ---------------------------------------------------------------------------


class TestExpandedResultsSerializableAndStable:
    def test_expanded_results_are_json_serializable(self) -> None:
        from dataclasses import asdict

        engine = HybridSearchEngine()
        children = [
            _child_result("a", collapse_group="g", heading_path="A > B > a"),
            _child_result("b", collapse_group="g", heading_path="A > B > b"),
        ]
        out = engine.expand_results_with_parent_child(children)
        payload = [asdict(r) for r in out]
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)
        assert decoded == payload

    def test_expansion_is_stable_across_repeated_invocations(self) -> None:
        engine_a = HybridSearchEngine()
        engine_b = HybridSearchEngine()
        children = [
            _child_result("x", collapse_group="g", heading_path="A > B > x", combined_score=0.5),
            _child_result("y", collapse_group="g", heading_path="A > B > y", combined_score=0.7),
            _child_result("z", collapse_group="h", heading_path="R > z", combined_score=0.6),
        ]
        out_a = engine_a.expand_results_with_parent_child(children)
        out_b = engine_b.expand_results_with_parent_child(children)
        assert [r.chunk_id for r in out_a] == [r.chunk_id for r in out_b]
        assert [r.combined_score for r in out_a] == [r.combined_score for r in out_b]

    def test_expanded_result_field_types_are_primitives(self) -> None:
        engine = HybridSearchEngine()
        children = [
            _child_result("a", collapse_group="g", heading_path="A > B > C"),
        ]
        out = engine.expand_results_with_parent_child(children)
        for r in out:
            assert isinstance(r.chunk_id, str)
            assert isinstance(r.content, str)
            assert isinstance(r.metadata, dict)
            assert isinstance(r.combined_score, float)
            assert isinstance(r.vector_score, float)
            assert isinstance(r.lexical_score, float)
            assert isinstance(r.source, str)
        # source tag must be either a real retrieval source or "parent".
        allowed_sources = {"vector", "lexical", "hybrid", "parent"}
        assert all(r.source in allowed_sources for r in out)

    def test_expansion_returns_new_list_not_input_reference(self) -> None:
        engine = HybridSearchEngine()
        inputs = [_child_result("a", collapse_group="g", heading_path="A > B")]
        out = engine.expand_results_with_parent_child(inputs)
        assert out is not inputs

    def test_expansion_chains_cleanly_with_search_output_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # The public contract of expand_results_with_parent_child is that it
        # consumes a list[HybridSearchResult] — i.e. the exact shape returned
        # by search(). This test proves the chaining works end-to-end on the
        # RRF-fused output from D2.1 without any glue code.
        fused = HybridSearchEngine._rrf_fuse(
            [
                HybridSearchResult(
                    chunk_id="cvec",
                    content="v",
                    metadata={
                        "collapse_group": "fwk",
                        "heading_path": "Root > Section > Sub",
                    },
                    combined_score=0.5,
                    source="vector",
                    vector_score=0.5,
                )
            ],
            [
                HybridSearchResult(
                    chunk_id="clex",
                    content="l",
                    metadata={
                        "collapse_group": "fwk",
                        "heading_path": "Root > Section > Sub",
                    },
                    combined_score=0.3,
                    source="lexical",
                    lexical_score=0.3,
                )
            ],
        )
        engine = HybridSearchEngine()
        expanded = engine.expand_results_with_parent_child(fused)
        # At least one synthetic parent appears because both fused children
        # share the "Root > Section" parent heading_path.
        parents = [r for r in expanded if r.source == "parent"]
        assert len(parents) == 1
        assert parents[0].metadata["heading_path"] == "Root > Section"


# ---------------------------------------------------------------------------
# Non-regression — signature and class-level constants
# ---------------------------------------------------------------------------


class TestParentChildSignatureStability:
    def test_expand_signature_unchanged(self) -> None:
        sig = inspect.signature(HybridSearchEngine.expand_results_with_parent_child)
        params = sig.parameters
        assert "results" in params
        assert "max_depth" in params and params["max_depth"].default == 1

    def test_class_level_constants_exposed(self) -> None:
        assert hasattr(HybridSearchEngine, "PARENT_SYNTHETIC_PREFIX")
        assert hasattr(HybridSearchEngine, "PARENT_HEADING_SEPARATOR")
        assert HybridSearchEngine.PARENT_HEADING_SEPARATOR == " > "
        assert HybridSearchEngine.PARENT_SYNTHETIC_PREFIX == "__parent__"


# ===========================================================================
# Wave D2.3 — expand_results_with_adg (bounded callers + callees expansion)
# ===========================================================================


def _adg_linked_result(
    chunk_id: str,
    *,
    node_id: int | str,
    combined_score: float = 0.5,
    metadata: dict[str, Any] | None = None,
) -> HybridSearchResult:
    meta: dict[str, Any] = {"node_id": node_id}
    if metadata:
        meta.update(metadata)
    return HybridSearchResult(
        chunk_id=chunk_id,
        content=f"content-{chunk_id}",
        metadata=meta,
        combined_score=combined_score,
        source="vector",
        vector_score=combined_score,
        lexical_score=0.0,
    )


def _neighbour(
    neighbour_id: int | str,
    *,
    adg_name: str | None = None,
    file_path: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {"id": neighbour_id}
    if adg_name is not None:
        row["adg_name"] = adg_name
    if file_path is not None:
        row["file_path"] = file_path
    return row


# ---------------------------------------------------------------------------
# Requirement 1 — callers/callees added when linkage exists
# ---------------------------------------------------------------------------


class TestAdgCallersAndCalleesAdded:
    def test_single_parent_callers_and_callees_are_lifted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda nid: [_neighbour(100 + nid, adg_name="up")])
        monkeypatch.setattr(engine, "get_callees", lambda nid: [_neighbour(200 + nid, adg_name="dn")])
        parent = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([parent])
        sources = [r.source for r in out]
        assert sources.count("adg") == 2
        assert sources[-1] == "vector"  # original preserved at the tail
        caller = next(r for r in out if r.metadata.get("adg_relation") == "callers")
        callee = next(r for r in out if r.metadata.get("adg_relation") == "callees")
        assert caller.metadata["node_id"] == "105"
        assert callee.metadata["node_id"] == "205"
        assert caller.content == "up"
        assert callee.content == "dn"

    def test_adg_chunk_id_is_namespaced_and_deterministic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(42)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        out = engine.expand_results_with_adg([_adg_linked_result("p1", node_id=7)])
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 1
        assert synthetic[0].chunk_id == "__adg__:callers:42"
        assert synthetic[0].chunk_id.startswith(HybridSearchEngine.ADG_SYNTHETIC_PREFIX + ":")

    def test_limit_per_relation_caps_fanout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(
            engine,
            "get_callers",
            lambda _n: [_neighbour(i, adg_name=f"c{i}") for i in range(10)],
        )
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        out = engine.expand_results_with_adg(
            [_adg_linked_result("p1", node_id=1)],
            limit_per_relation=3,
        )
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 3
        # The first three neighbours (by helper's returned order) win.
        assert [r.metadata["node_id"] for r in synthetic] == ["0", "1", "2"]

    def test_relation_types_restricts_to_callers_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        calls_log: list[str] = []

        def _fake_callers(_n: int) -> list[dict[str, Any]]:
            calls_log.append("callers")
            return [_neighbour(1)]

        def _fake_callees(_n: int) -> list[dict[str, Any]]:
            calls_log.append("callees")
            return [_neighbour(2)]

        monkeypatch.setattr(engine, "get_callers", _fake_callers)
        monkeypatch.setattr(engine, "get_callees", _fake_callees)
        out = engine.expand_results_with_adg(
            [_adg_linked_result("p1", node_id=1)],
            relation_types=["callers"],
        )
        assert calls_log == ["callers"]
        synthetic = [r for r in out if r.source == "adg"]
        assert [r.metadata["adg_relation"] for r in synthetic] == ["callers"]

    def test_unknown_relation_types_are_ignored(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [_neighbour(2)])
        # "imports" and "importers" are intentionally NOT in the D2.3 default
        # relation set. Passing them alongside a known relation should keep
        # callers and ignore the rest without error.
        out = engine.expand_results_with_adg(
            [_adg_linked_result("p1", node_id=1)],
            relation_types=["callers", "imports", "importers", "bogus"],
        )
        synthetic = [r for r in out if r.source == "adg"]
        relations = {r.metadata["adg_relation"] for r in synthetic}
        assert relations == {"callers"}

    def test_parent_metadata_linkage_stored_on_synthetic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(99, adg_name="up")])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        out = engine.expand_results_with_adg([_adg_linked_result("p1", node_id=7)])
        synthetic = [r for r in out if r.source == "adg"]
        assert synthetic[0].metadata["adg_parent_chunk_id"] == "p1"
        assert synthetic[0].metadata["adg_parent_node_id"] == 7
        assert synthetic[0].metadata["is_synthetic_adg_expansion"] is True


# ---------------------------------------------------------------------------
# Requirement 2 — no-op when node linkage is missing
# ---------------------------------------------------------------------------


class TestAdgNoopWhenLinkageMissing:
    def test_empty_input_returns_empty_list(self) -> None:
        engine = HybridSearchEngine()
        assert engine.expand_results_with_adg([]) == []

    def test_no_node_id_metadata_is_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _explode(_n: int) -> list[dict[str, Any]]:
            raise AssertionError("helper must not be called when node_id absent")

        monkeypatch.setattr(engine, "get_callers", _explode)
        monkeypatch.setattr(engine, "get_callees", _explode)
        r = HybridSearchResult(chunk_id="p1", content="", metadata={}, combined_score=0.5, source="vector")
        out = engine.expand_results_with_adg([r])
        assert out == [r]

    def test_unparseable_node_id_is_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _explode(_n: int) -> list[dict[str, Any]]:
            raise AssertionError("helper must not be called for unparseable node_id")

        monkeypatch.setattr(engine, "get_callers", _explode)
        monkeypatch.setattr(engine, "get_callees", _explode)
        r = _adg_linked_result("p1", node_id="not-an-int")
        out = engine.expand_results_with_adg([r])
        assert out == [r]

    def test_limit_zero_is_passthrough(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _explode(_n: int) -> list[dict[str, Any]]:
            raise AssertionError("helper must not be called when limit is 0")

        monkeypatch.setattr(engine, "get_callers", _explode)
        monkeypatch.setattr(engine, "get_callees", _explode)
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r], limit_per_relation=0)
        assert out == [r]

    def test_empty_relation_types_is_passthrough(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _explode(_n: int) -> list[dict[str, Any]]:
            raise AssertionError("helper must not be called for empty relation_types")

        monkeypatch.setattr(engine, "get_callers", _explode)
        monkeypatch.setattr(engine, "get_callees", _explode)
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r], relation_types=[])
        assert out == [r]

    def test_only_unknown_relation_types_is_passthrough(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [_neighbour(2)])
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r], relation_types=["imports", "bogus"])
        # No known relations in the filter -> passthrough.
        assert out == [r]

    def test_empty_helper_return_does_not_emit_synthetic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r])
        assert out == [r]


# ---------------------------------------------------------------------------
# Requirement 3 — sqlite / ADG failures swallowed safely
# ---------------------------------------------------------------------------


class TestAdgExpansionSwallowsFailures:
    def test_sqlite_operational_error_degrades_to_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import sqlite3

        engine = HybridSearchEngine()

        def _raising(_n: int) -> list[dict[str, Any]]:
            raise sqlite3.OperationalError("simulated adg db lock")

        monkeypatch.setattr(engine, "get_callers", _raising)
        monkeypatch.setattr(engine, "get_callees", _raising)
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r])
        # No synthetic rows — failure was swallowed.
        assert out == [r]

    def test_runtime_error_in_helper_degrades_to_noop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _raising(_n: int) -> list[dict[str, Any]]:
            raise RuntimeError("unexpected adg failure")

        monkeypatch.setattr(engine, "get_callers", _raising)
        monkeypatch.setattr(engine, "get_callees", _raising)
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r])
        assert out == [r]

    def test_partial_failure_preserves_successful_relation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()

        def _fail_callers(_n: int) -> list[dict[str, Any]]:
            raise RuntimeError("callers helper is down")

        monkeypatch.setattr(engine, "get_callers", _fail_callers)
        monkeypatch.setattr(engine, "get_callees", lambda _n: [_neighbour(99, adg_name="ok")])
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r])
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 1
        assert synthetic[0].metadata["adg_relation"] == "callees"
        assert synthetic[0].content == "ok"

    def test_malformed_neighbour_rows_are_skipped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        # Mix of malformed entries: non-dict, missing id, empty-string id.
        bad_rows: list[Any] = [
            "not-a-dict",
            {"not_id": "stuff"},  # missing 'id'
            {"id": ""},  # empty id
            {"id": 77, "adg_name": "ok"},  # valid
        ]
        monkeypatch.setattr(engine, "get_callers", lambda _n: bad_rows)
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        r = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([r], limit_per_relation=10)
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 1
        assert synthetic[0].metadata["node_id"] == "77"


# ---------------------------------------------------------------------------
# Requirement 4 — duplicate expansions deduped deterministically
# ---------------------------------------------------------------------------


class TestAdgExpansionDedup:
    def test_two_parents_pointing_to_same_neighbour_emit_one_synthetic(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        engine = HybridSearchEngine()
        # Every parent returns the same neighbour via `callers`.
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(99, adg_name="shared")])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        parents = [
            _adg_linked_result("p1", node_id=1, combined_score=0.3),
            _adg_linked_result("p2", node_id=2, combined_score=0.9),
        ]
        out = engine.expand_results_with_adg(parents)
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 1
        # Dedup keeps max parent score.
        assert synthetic[0].combined_score == pytest.approx(0.9)
        assert synthetic[0].metadata["node_id"] == "99"

    def test_same_neighbour_via_both_relations_is_not_deduped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # A callers-relation neighbour and a callees-relation neighbour with
        # the same node_id are DIFFERENT ADG synthetics by design — the
        # relation direction matters.
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(50)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [_neighbour(50)])
        out = engine.expand_results_with_adg([_adg_linked_result("p1", node_id=1)])
        synthetic = [r for r in out if r.source == "adg"]
        assert len(synthetic) == 2
        relations = {r.metadata["adg_relation"] for r in synthetic}
        assert relations == {"callers", "callees"}

    def test_existing_synthetic_chunk_id_in_input_suppresses_dedup(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # If the input list already contains the synthetic id (e.g. from
        # a prior expansion round), we do NOT duplicate it.
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(42)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        preexisting = HybridSearchResult(
            chunk_id="__adg__:callers:42",
            content="pre",
            metadata={"node_id": "42"},
            combined_score=0.7,
            source="adg",
        )
        parent = _adg_linked_result("p1", node_id=5)
        out = engine.expand_results_with_adg([parent, preexisting])
        # Only the existing synthetic remains; no duplicate minted.
        synthetic = [r for r in out if r.chunk_id == "__adg__:callers:42"]
        assert len(synthetic) == 1

    def test_synthetic_order_follows_first_seen_parent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(
            engine,
            "get_callers",
            lambda nid: [_neighbour(nid * 10, adg_name=f"n{nid}")],
        )
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        parents = [
            _adg_linked_result("p1", node_id=3),
            _adg_linked_result("p2", node_id=7),
        ]
        out = engine.expand_results_with_adg(parents)
        synthetic_ids = [r.metadata["node_id"] for r in out if r.source == "adg"]
        # p1 (node_id=3) is seen first -> its neighbour "30" ranks first.
        assert synthetic_ids == ["30", "70"]


# ---------------------------------------------------------------------------
# Requirement 5 — original results preserved
# ---------------------------------------------------------------------------


class TestAdgOriginalsPreserved:
    def test_all_original_results_appear_in_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        inputs = [
            _adg_linked_result("a", node_id=1),
            _adg_linked_result("b", node_id=2),
        ]
        out = engine.expand_results_with_adg(inputs)
        original_ids = {r.chunk_id for r in inputs}
        out_ids = {r.chunk_id for r in out}
        assert original_ids.issubset(out_ids)

    def test_original_order_is_preserved_after_synthetics(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda nid: [_neighbour(nid * 100)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        inputs = [
            _adg_linked_result("zzz", node_id=1),
            _adg_linked_result("aaa", node_id=2),
            _adg_linked_result("mmm", node_id=3),
        ]
        out = engine.expand_results_with_adg(inputs)
        real = [r for r in out if r.source != "adg"]
        assert [r.chunk_id for r in real] == ["zzz", "aaa", "mmm"]

    def test_input_list_is_not_mutated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        a = _adg_linked_result("a", node_id=1)
        b = _adg_linked_result("b", node_id=2)
        inputs = [a, b]
        snapshot = list(inputs)
        engine.expand_results_with_adg(inputs)
        assert inputs == snapshot


# ---------------------------------------------------------------------------
# Requirement 6 — expanded output is serializable and stable
# ---------------------------------------------------------------------------


class TestAdgExpandedSerializableAndStable:
    def test_expanded_results_are_json_serializable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from dataclasses import asdict

        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1, adg_name="x")])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        out = engine.expand_results_with_adg([_adg_linked_result("p1", node_id=5)])
        payload = [asdict(r) for r in out]
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)
        assert decoded == payload

    def test_expansion_is_stable_across_two_engines(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _stub_callers(_n: int) -> list[dict[str, Any]]:
            return [_neighbour(11, adg_name="a"), _neighbour(22, adg_name="b")]

        def _stub_callees(_n: int) -> list[dict[str, Any]]:
            return [_neighbour(33, adg_name="c")]

        e1 = HybridSearchEngine()
        e2 = HybridSearchEngine()
        monkeypatch.setattr(e1, "get_callers", _stub_callers)
        monkeypatch.setattr(e1, "get_callees", _stub_callees)
        monkeypatch.setattr(e2, "get_callers", _stub_callers)
        monkeypatch.setattr(e2, "get_callees", _stub_callees)
        parent = _adg_linked_result("p1", node_id=5)
        out_a = e1.expand_results_with_adg([parent])
        out_b = e2.expand_results_with_adg([parent])
        assert [r.chunk_id for r in out_a] == [r.chunk_id for r in out_b]
        assert [r.combined_score for r in out_a] == [r.combined_score for r in out_b]

    def test_expanded_field_types_are_primitives(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(1, adg_name="x")])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        out = engine.expand_results_with_adg([_adg_linked_result("p1", node_id=5)])
        allowed_sources = {"vector", "lexical", "hybrid", "parent", "adg"}
        for r in out:
            assert isinstance(r.chunk_id, str)
            assert isinstance(r.content, str)
            assert isinstance(r.metadata, dict)
            assert isinstance(r.combined_score, float)
            assert isinstance(r.vector_score, float)
            assert isinstance(r.lexical_score, float)
            assert r.source in allowed_sources

    def test_expand_returns_new_list_not_input_reference(self, monkeypatch: pytest.MonkeyPatch) -> None:
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        inputs = [_adg_linked_result("p1", node_id=5)]
        out = engine.expand_results_with_adg(inputs)
        assert out is not inputs

    def test_chains_with_d2_1_and_d2_2_output_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # End-to-end: D2.1 RRF output -> D2.2 parent lift -> D2.3 ADG expansion.
        # Each stage consumes the same list[HybridSearchResult] shape.
        engine = HybridSearchEngine()
        monkeypatch.setattr(engine, "get_callers", lambda _n: [_neighbour(99)])
        monkeypatch.setattr(engine, "get_callees", lambda _n: [])
        fused = HybridSearchEngine._rrf_fuse(
            [
                HybridSearchResult(
                    chunk_id="c1",
                    content="v",
                    metadata={
                        "collapse_group": "fwk",
                        "heading_path": "Root > Section",
                        "node_id": 7,
                    },
                    combined_score=0.5,
                    source="vector",
                    vector_score=0.5,
                )
            ],
            [],
        )
        after_d22 = engine.expand_results_with_parent_child(fused)
        after_d23 = engine.expand_results_with_adg(after_d22)
        # Output contains original vector row, a synthetic parent row
        # (D2.2), and a synthetic ADG caller row (D2.3).
        sources = {r.source for r in after_d23}
        assert sources >= {"vector", "parent", "adg"}


# ---------------------------------------------------------------------------
# Non-regression — signature stability
# ---------------------------------------------------------------------------


class TestAdgSignatureStability:
    def test_expand_with_adg_signature_unchanged(self) -> None:
        sig = inspect.signature(HybridSearchEngine.expand_results_with_adg)
        params = sig.parameters
        assert "results" in params
        assert "relation_types" in params and params["relation_types"].default is None
        assert "limit_per_relation" in params and params["limit_per_relation"].default == 3

    def test_adg_class_constants_exposed(self) -> None:
        assert hasattr(HybridSearchEngine, "ADG_SYNTHETIC_PREFIX")
        assert HybridSearchEngine.ADG_SYNTHETIC_PREFIX == "__adg__"
        assert hasattr(HybridSearchEngine, "ADG_DEFAULT_RELATIONS")
        assert HybridSearchEngine.ADG_DEFAULT_RELATIONS == ("callers", "callees")
