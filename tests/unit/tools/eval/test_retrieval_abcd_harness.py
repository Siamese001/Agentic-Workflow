"""Unit tests for the 4-cell A/B retrieval benchmark harness (Wave E).

All tests use mock retrievers so no ChromaDB, no BGE weights, no torch
required. The harness's metric math and cell orchestration are verified
end-to-end against known-correct rankings.

Coverage
--------
* _recall_at_k / _precision_at_k / _reciprocal_rank — edge cases
* evaluate_cell — happy path, empty retrieval, retriever-raising
* evaluate_all_cells — cell ordering + retriever_factory per-cell build
* load_manifest — JSON + missing-file + bad shape
* render_summary_table / render_json_report — format invariants
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.eval.retrieval_abcd_harness import (
    CalibrationQuery,
    CellConfig,
    CellResult,
    QueryResult,
    RetrievedChunk,
    _precision_at_k,
    _recall_at_k,
    _reciprocal_rank,
    _build_default_retriever_factory,
    evaluate_all_cells,
    evaluate_cell,
    load_manifest,
    render_json_report,
    render_summary_table,
)


# ---------------------------------------------------------------------------
# Metric math
# ---------------------------------------------------------------------------


def test_recall_at_k_perfect_retrieval():
    """All relevant docs in the top-k => recall 1.0."""
    assert _recall_at_k(["a", "b", "c"], ["a", "b"]) == 1.0


def test_recall_at_k_partial():
    """Half of the 2 relevant docs retrieved => 0.5."""
    assert _recall_at_k(["a", "x", "y"], ["a", "b"]) == 0.5


def test_recall_at_k_zero_when_no_overlap():
    assert _recall_at_k(["x", "y"], ["a", "b"]) == 0.0


def test_recall_at_k_returns_zero_for_empty_relevant_set():
    """Empty ground truth => safe 0.0 (no division by zero)."""
    assert _recall_at_k(["a"], []) == 0.0


def test_precision_at_k_counts_only_top_k():
    """Relevant docs beyond position k MUST NOT count toward precision."""
    # k=2 considers positions 0 and 1: only 'a' relevant, so 1/2=0.5
    assert _precision_at_k(["a", "x", "b"], ["a", "b"], k=2) == 0.5


def test_precision_at_k_zero_k_returns_zero():
    """Defensive: k=0 shouldn't raise."""
    assert _precision_at_k(["a"], ["a"], k=0) == 0.0


def test_reciprocal_rank_first_hit_at_position_1():
    assert _reciprocal_rank(["a", "b"], ["a"]) == 1.0


def test_reciprocal_rank_first_hit_at_position_3():
    """RR of 1/3 when the first relevant doc is at position 3."""
    assert _reciprocal_rank(["x", "y", "a", "b"], ["a", "b"]) == pytest.approx(1 / 3)


def test_reciprocal_rank_zero_when_no_hit():
    assert _reciprocal_rank(["x", "y"], ["a"]) == 0.0


# ---------------------------------------------------------------------------
# evaluate_cell
# ---------------------------------------------------------------------------


def _make_retriever(mapping: dict[str, list[RetrievedChunk]]):
    """Build a retriever that returns the pre-baked list for each query."""

    def _fake(query: str, collection: str) -> list[RetrievedChunk]:
        _ = collection  # unused in fake
        return mapping.get(query, [])

    return _fake


def test_evaluate_cell_aggregates_metrics_across_queries():
    """Two queries, different retrievals — aggregate means are arithmetic."""
    queries = [
        CalibrationQuery(query="q1", relevant_doc_ids=frozenset({"a"}), category="x"),
        CalibrationQuery(query="q2", relevant_doc_ids=frozenset({"b"}), category="x"),
    ]
    retriever = _make_retriever(
        {
            # q1: perfect - a at position 1 => recall 1.0, precision@2 = 0.5, RR = 1.0
            "q1": [RetrievedChunk(doc_id="a"), RetrievedChunk(doc_id="z")],
            # q2: miss entirely => recall 0, precision 0, RR 0
            "q2": [RetrievedChunk(doc_id="x"), RetrievedChunk(doc_id="y")],
        }
    )
    cell = CellConfig(name="baseline", collection="col_a", reranker_mode="none")
    result = evaluate_cell(cell, queries, retriever, top_k=2)

    assert result.cell_name == "baseline"
    assert result.num_queries == 2
    assert result.mean_recall_at_k == pytest.approx(0.5)  # (1.0 + 0.0) / 2
    assert result.mean_precision_at_k == pytest.approx(0.25)  # (0.5 + 0.0) / 2
    assert result.mean_reciprocal_rank == pytest.approx(0.5)  # (1.0 + 0.0) / 2
    assert result.hit_rate_at_k == pytest.approx(0.5)  # 1 hit / 2 queries
    assert len(result.per_query) == 2


def test_evaluate_cell_truncates_to_top_k():
    """Retriever returns 10 chunks but top_k=3 => only first 3 count."""
    queries = [
        CalibrationQuery(query="q1", relevant_doc_ids=frozenset({"z"}), category=""),
    ]
    retriever = _make_retriever(
        {
            # "z" is at position 5 (0-indexed 4) — inside top-5 but outside top-3
            "q1": [RetrievedChunk(doc_id=d) for d in ["a", "b", "c", "d", "z"]],
        }
    )
    cell = CellConfig(name="c", collection="col", reranker_mode="none")

    # top_k=3: z is NOT in top-3, so recall=0, precision=0, RR=0
    r3 = evaluate_cell(cell, queries, retriever, top_k=3)
    assert r3.mean_recall_at_k == 0.0
    assert r3.mean_reciprocal_rank == 0.0

    # top_k=5: z IS in top-5 at position 5, so recall=1, RR=1/5
    r5 = evaluate_cell(cell, queries, retriever, top_k=5)
    assert r5.mean_recall_at_k == 1.0
    assert r5.mean_reciprocal_rank == pytest.approx(0.2)


def test_evaluate_cell_records_zero_metrics_when_retriever_raises():
    """Retriever RuntimeError must NOT crash the cell run; the bad query
    scores zero and the loop continues. Protects large A/B runs from
    losing all data when one query has a config typo."""
    queries = [
        CalibrationQuery(query="q_bad", relevant_doc_ids=frozenset({"a"}), category=""),
        CalibrationQuery(query="q_ok", relevant_doc_ids=frozenset({"b"}), category=""),
    ]

    def _flaky(query: str, collection: str) -> list[RetrievedChunk]:
        _ = collection
        if query == "q_bad":
            raise RuntimeError("collection not found")
        return [RetrievedChunk(doc_id="b")]

    cell = CellConfig(name="c", collection="col", reranker_mode="none")
    result = evaluate_cell(cell, queries, _flaky, top_k=5)

    # q_bad -> zeros, q_ok -> 1.0 => mean = 0.5
    assert result.mean_recall_at_k == pytest.approx(0.5)
    assert len(result.per_query) == 2
    assert result.per_query[0].retrieved_doc_ids == []  # q_bad: empty list recorded


def test_evaluate_cell_empty_retrieval_produces_zero_without_crashing():
    queries = [
        CalibrationQuery(query="q", relevant_doc_ids=frozenset({"a"}), category=""),
    ]
    retriever = _make_retriever({})  # returns [] for anything
    cell = CellConfig(name="c", collection="col", reranker_mode="none")
    result = evaluate_cell(cell, queries, retriever, top_k=5)
    assert result.mean_recall_at_k == 0.0
    assert result.hit_rate_at_k == 0.0


# ---------------------------------------------------------------------------
# evaluate_all_cells
# ---------------------------------------------------------------------------


def test_evaluate_all_cells_calls_factory_once_per_cell():
    """The factory must be invoked exactly once per cell, and the result
    order must match the input cell order (critical for the A/B report)."""
    queries = [
        CalibrationQuery(query="q", relevant_doc_ids=frozenset({"a"}), category=""),
    ]
    cells = [
        CellConfig(name="baseline", collection="col_a", reranker_mode="none"),
        CellConfig(name="contextualized", collection="col_b", reranker_mode="heuristic"),
        CellConfig(name="late_chunked", collection="col_c", reranker_mode="none"),
        CellConfig(name="both", collection="col_d", reranker_mode="cross_encoder"),
    ]

    factory_calls: list[str] = []

    def _factory(cell: CellConfig):
        factory_calls.append(cell.name)
        # every retriever returns the single relevant doc so recall == 1
        return lambda q, c: [RetrievedChunk(doc_id="a")]

    results = evaluate_all_cells(cells, queries, _factory, top_k=5)

    assert factory_calls == ["baseline", "contextualized", "late_chunked", "both"]
    assert [r.cell_name for r in results] == [
        "baseline",
        "contextualized",
        "late_chunked",
        "both",
    ]
    for r in results:
        assert r.mean_recall_at_k == 1.0


# ---------------------------------------------------------------------------
# Manifest loading
# ---------------------------------------------------------------------------


def test_load_manifest_json_roundtrip(tmp_path):
    manifest = tmp_path / "m.json"
    manifest.write_text(
        json.dumps(
            {
                "queries": [
                    {"query": "q1", "relevant_doc_ids": ["a", "b"], "category": "exact"},
                    {"query": "q2", "relevant_doc_ids": ["c"]},
                ]
            }
        ),
        encoding="utf-8",
    )
    queries = load_manifest(manifest)
    assert len(queries) == 2
    assert queries[0].query == "q1"
    assert queries[0].relevant_doc_ids == frozenset({"a", "b"})
    assert queries[0].category == "exact"
    # Missing category defaults to empty string — keeps the dataclass frozen-safe.
    assert queries[1].category == ""


def test_load_manifest_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "nope.json")


def test_load_manifest_wrong_shape(tmp_path):
    """Manifest missing 'queries' key must fail loud, not silently return []."""
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"unexpected": "shape"}), encoding="utf-8")
    with pytest.raises(ValueError, match="must be an object with 'queries'"):
        load_manifest(manifest)


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def _mk_cell_result(name: str, recall: float, rerank: str = "none") -> CellResult:
    return CellResult(
        cell_name=name,
        collection=f"col_{name}",
        reranker_mode=rerank,
        top_k=20,
        num_queries=5,
        mean_recall_at_k=recall,
        mean_precision_at_k=0.5,
        mean_reciprocal_rank=0.7,
        hit_rate_at_k=0.9,
        per_query=[],
    )


def test_render_summary_table_contains_every_cell_name():
    results = [
        _mk_cell_result("baseline", 0.50),
        _mk_cell_result("contextualized", 0.65, "heuristic"),
        _mk_cell_result("late_chunked", 0.62),
        _mk_cell_result("both", 0.78, "cross_encoder"),
    ]
    table = render_summary_table(results)
    for name in ("baseline", "contextualized", "late_chunked", "both"):
        assert name in table
    # Header present
    assert "Recall@K" in table
    assert "MRR" in table


def test_render_json_report_is_valid_json_with_schema_version():
    results = [_mk_cell_result("baseline", 0.5)]
    report = render_json_report(results, top_k=20, timestamp="20260424T100000Z")
    # Must be JSON-serializable (asdict handles dataclasses).
    serialized = json.dumps(report)
    parsed = json.loads(serialized)
    assert parsed["schema_version"] == "1.0"
    assert parsed["top_k"] == 20
    assert parsed["generated_at_utc"] == "20260424T100000Z"
    assert len(parsed["cells"]) == 1
    assert parsed["cells"][0]["cell_name"] == "baseline"


# ---------------------------------------------------------------------------
# Default retriever factory (SovereignChromaClient glue)
# ---------------------------------------------------------------------------


def test_default_retriever_factory_sets_reranker_env_before_retrieval(monkeypatch):
    """The factory must flip RERANKER env to the cell's mode so that
    reranker_factory.get_reranker() returns the right backend when the
    retrieve() function (or downstream caller) consults it."""
    monkeypatch.delenv("RERANKER", raising=False)

    fake_client = MagicMock()
    fake_client.query.return_value = {
        "ids": [["d1"]],
        "documents": [["text"]],
        "metadatas": [[{}]],
        "distances": [[0.2]],
    }

    factory = _build_default_retriever_factory(fake_client)
    cell = CellConfig(name="c", collection="col", reranker_mode="cross_encoder")
    retrieve = factory(cell)

    import os

    assert os.environ["RERANKER"] == "cross_encoder"

    out = retrieve("some query", "col")
    assert len(out) == 1
    assert out[0].doc_id == "d1"
    # Chroma distance 0.2 -> score 0.8 (inversion).
    assert out[0].score == pytest.approx(0.8)


def test_default_retriever_factory_handles_empty_chroma_response():
    """Chroma returning empty shells must produce an empty RetrievedChunk
    list, not crash on index arithmetic."""
    fake_client = MagicMock()
    fake_client.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }
    factory = _build_default_retriever_factory(fake_client)
    cell = CellConfig(name="c", collection="col", reranker_mode="none")
    retrieve = factory(cell)
    assert retrieve("q", "col") == []
