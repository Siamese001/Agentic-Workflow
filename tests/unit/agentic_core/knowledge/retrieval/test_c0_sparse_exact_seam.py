"""W1–W2 generic C0 sparse/lexical seam — neutral fixtures only."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchResult,
)
from agentic_core.knowledge.retrieval.c0_sparse_exact_seam import (
    SparseLexicalLaneStatus,
    SparseLexicalQuerySpec,
    dedupe_hybrid_by_chunk_id,
    evidence_items_from_merged_hybrid,
    fec_sparse_refs_from_lane_outcomes,
    filter_candidates_exact_subphrase,
    format_sparse_lane_receipt,
    merge_dense_sparse_rrf,
    query_sparse_lexical_lane,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    SUPPORT_STATUS_EMPTY,
)


class _StubSparseIndex:
    """Hermetic sparse backend for unit tests."""

    def __init__(self, hits: list[dict[str, Any]], *, available: bool = True):
        self._hits = list(hits)
        self._available = available

    @property
    def is_available(self) -> bool:
        return self._available

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        return list(self._hits)[:top_k]


def test_exact_subphrase_filter_returns_matching_rows() -> None:
    phrase = "alpha beta gamma"
    corpus = (
        ("id-a", "prefix alpha beta gamma suffix", {"k": "v"}),
        ("id-b", "no match here", {}),
    )
    out = filter_candidates_exact_subphrase(corpus, phrase)
    assert len(out) == 1
    assert out[0][0] == "id-a"


def test_query_lane_unavailable_for_empty_collection_name() -> None:
    spec = SparseLexicalQuerySpec(
        lane_id="lane-neutral-1",
        query_text="any",
        sparse_index_collection_name="",
    )
    out = query_sparse_lexical_lane(spec)
    assert out.status == SparseLexicalLaneStatus.UNAVAILABLE
    assert out.hits == ()
    assert "UNAVAILABLE" in out.receipt_ref


def test_query_lane_unavailable_for_unknown_collection() -> None:
    spec = SparseLexicalQuerySpec(
        lane_id="lane-neutral-2",
        query_text="query text",
        sparse_index_collection_name="nonexistent_collection_handle",
    )
    out = query_sparse_lexical_lane(spec)
    assert out.status == SparseLexicalLaneStatus.UNAVAILABLE


def test_query_lane_ok_when_stub_returns_hits(monkeypatch: pytest.MonkeyPatch) -> None:
    hits = [
        {
            "id": "chunk-neutral-a",
            "content": "document alpha beta gamma tail",
            "score": 0.91,
            "metadata": {"layer": "L3", "source_document_id": "src-neutral-1"},
            "source": "sparse_fts",
        },
    ]
    stub = _StubSparseIndex(hits)
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: stub,
    )
    spec = SparseLexicalQuerySpec(
        lane_id="lane-neutral-3",
        query_text="alpha beta gamma",
        top_k=5,
        sparse_index_collection_name="code_chunks",
        metadata_filter={"layer": "L3"},
    )
    out = query_sparse_lexical_lane(spec)
    assert out.status == SparseLexicalLaneStatus.OK
    assert len(out.hits) == 1
    assert out.hits[0].chunk_id == "chunk-neutral-a"
    assert out.hits[0].lexical_score == pytest.approx(0.91)


def test_query_lane_empty_not_ok_when_stub_returns_no_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _StubSparseIndex([])
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: stub,
    )
    spec = SparseLexicalQuerySpec(
        lane_id="lane-neutral-4",
        query_text="unique token zyxwvutsrq",
        sparse_index_collection_name="code_chunks",
    )
    out = query_sparse_lexical_lane(spec)
    assert out.status == SparseLexicalLaneStatus.EMPTY
    assert out.hits == ()
    assert out.status != SparseLexicalLaneStatus.OK
    assert "EMPTY" in out.receipt_ref


def test_metadata_filter_yields_empty_lane(monkeypatch: pytest.MonkeyPatch) -> None:
    hits = [
        {
            "id": "c1",
            "content": "body one",
            "score": 0.5,
            "metadata": {"layer": "L2"},
            "source": "sparse_fts",
        },
    ]
    stub = _StubSparseIndex(hits)
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: stub,
    )
    spec = SparseLexicalQuerySpec(
        lane_id="lane-neutral-5",
        query_text="body",
        sparse_index_collection_name="code_chunks",
        metadata_filter={"layer": "L9"},
    )
    out = query_sparse_lexical_lane(spec)
    assert out.status == SparseLexicalLaneStatus.EMPTY


def test_merge_rrf_preserves_dense_and_lexical_scores() -> None:
    dense = [
        HybridSearchResult(
            chunk_id="d1",
            content="vector one",
            metadata={"m": 1},
            combined_score=0.9,
            source="vector",
            vector_score=0.9,
            lexical_score=0.0,
        ),
    ]
    sparse = [
        HybridSearchResult(
            chunk_id="s1",
            content="lexical one",
            metadata={"m": 2},
            combined_score=0.85,
            source="lexical",
            vector_score=0.0,
            lexical_score=0.85,
        ),
    ]
    merged = merge_dense_sparse_rrf(dense, sparse)
    by_id = {r.chunk_id: r for r in merged}
    assert by_id["d1"].vector_score == pytest.approx(0.9)
    assert by_id["d1"].lexical_score == pytest.approx(0.0)
    assert by_id["s1"].lexical_score == pytest.approx(0.85)
    assert by_id["s1"].vector_score == pytest.approx(0.0)


def test_merge_ordering_deterministic_with_tiebreak() -> None:
    dense = [
        HybridSearchResult("a", "a", {}, 0.5, "vector", 0.5, 0.0),
        HybridSearchResult("b", "b", {}, 0.5, "vector", 0.5, 0.0),
    ]
    sparse = [
        HybridSearchResult("b", "b", {}, 0.5, "lexical", 0.0, 0.5),
        HybridSearchResult("a", "a", {}, 0.5, "lexical", 0.0, 0.5),
    ]
    m1 = merge_dense_sparse_rrf(dense, sparse)
    m2 = merge_dense_sparse_rrf(dense, sparse)
    assert [r.chunk_id for r in m1] == [r.chunk_id for r in m2]


def test_dedupe_prefers_higher_combined_score() -> None:
    rows = [
        HybridSearchResult("x", "low", {}, 0.2, "lexical", 0.0, 0.2),
        HybridSearchResult("x", "high", {}, 0.8, "lexical", 0.0, 0.8),
    ]
    deduped = dedupe_hybrid_by_chunk_id(rows)
    assert len(deduped) == 1
    assert deduped[0].combined_score == pytest.approx(0.8)


def test_evidence_items_encode_dense_and_sparse_methods() -> None:
    merged = [
        HybridSearchResult(
            chunk_id="both-1",
            content="merged body",
            metadata={"source_document_id": "doc-neutral-9"},
            combined_score=0.4,
            source="hybrid",
            vector_score=0.7,
            lexical_score=0.6,
        ),
    ]
    items = evidence_items_from_merged_hybrid(
        merged,
        lane_id="lane-neutral-merge",
        query_vec_ref="qv:neutral:1",
        retrieval_run_ref="run:neutral:1",
    )
    assert len(items) == 1
    assert items[0].dense_score == pytest.approx(0.7)
    assert items[0].bm25_score == pytest.approx(0.6)
    assert "dense" in items[0].retrieval_method
    assert "sparse" in items[0].retrieval_method


def test_fec_accepts_sparse_search_refs_without_schema_change() -> None:
    ref = format_sparse_lane_receipt("lane-neutral-fec", SparseLexicalLaneStatus.EMPTY, 0)
    bundle = fec_sparse_refs_from_lane_outcomes(ref, ref)
    fec = FinalEvidenceContract(
        request_id="req-neutral",
        run_id="run-neutral",
        app_id="neutral_fixture_app",
        trace_id="trace-neutral",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_EMPTY,
        sparse_search_refs=bundle,
    )
    assert fec.sparse_search_refs == bundle
    assert not fec.support_status_is_passing()


def test_format_receipt_escapes_colons_in_lane_id() -> None:
    r = format_sparse_lane_receipt("lane:with:colons", SparseLexicalLaneStatus.OK, 3)
    assert "lane_with_colons" in r
    assert "status=OK" in r
