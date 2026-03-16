"""Plan 3 — Agentic RAG Hardening Tests.

Covers:
- Gap 3: query_planner imports (no NameError at construction)
- Gap 4: SovereignRAGManager._fuse_results RRF fusion + deduplication
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_plan3_agentic_rag_hardening")
_emit_applies_guardrail("p0", "test_plan3_agentic_rag_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_plan3_agentic_rag_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_plan3_agentic_rag_hardening", "state_snapshot")
emit_replay_key("p0", "test_plan3_agentic_rag_hardening")
emit_determinism_digest("p0", "test_plan3_agentic_rag_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Gap 3: query_planner — no NameError at construction
# ---------------------------------------------------------------------------


class TestQueryPlannerImports:
    """query_planner must be constructable without NameError."""

    def test_query_planner_imports_without_error(self):
        from agentic_core.L1_cognition.engines.query_planner import query_planner

        assert query_planner is not None

    def test_query_planner_instantiates_without_error(self):
        from agentic_core.L1_cognition.engines.query_planner import query_planner

        planner = query_planner()
        assert planner is not None
        assert planner.engine is not None
        assert planner.cache is not None

    def test_query_planner_accepts_none_engine(self):
        from agentic_core.L1_cognition.engines.query_planner import query_planner

        planner = query_planner(engine=None, cache=None)
        assert planner.engine is not None

    def test_query_planner_cache_get_set_roundtrip(self):
        from agentic_core.L1_cognition.engines.query_planner import query_planner

        planner = query_planner()
        planner.cache.set("key1", {"value": 42})
        result = planner.cache.get("key1")
        assert result == {"value": 42}

    def test_query_planner_cache_get_missing_returns_none(self):
        from agentic_core.L1_cognition.engines.query_planner import query_planner

        planner = query_planner()
        assert planner.cache.get("nonexistent") is None

    def test_query_planner_all_exported(self):
        import agentic_core.L1_cognition.engines.query_planner as mod

        assert hasattr(mod, "__all__")
        assert "query_planner" in mod.__all__


# ---------------------------------------------------------------------------
# Gap 4: _fuse_results — RRF fusion + deduplication
# ---------------------------------------------------------------------------


class TestRRFFusion:
    """SovereignRAGManager._fuse_results must implement proper RRF, not concatenation."""

    def _make_manager(self):
        from unittest.mock import patch

        with patch("agentic_core.knowledge.reasoning.SovereignRAGManagerAgent.SovereignBaseAgent.__init__"):
            from agentic_core.knowledge.reasoning.SovereignRAGManagerAgent import (
                SovereignRAGManager,
            )

            mgr = object.__new__(SovereignRAGManager)
            mgr.logger = __import__("logging").getLogger("test")
            return mgr

    def test_fuse_empty_lists_returns_empty(self):
        mgr = self._make_manager()
        result = mgr._fuse_results([], [])
        assert result == []

    def test_fuse_vector_only_returns_sorted_by_rrf(self):
        mgr = self._make_manager()
        vector = [
            {"id": "a", "score": 0.9, "text": "alpha"},
            {"id": "b", "score": 0.8, "text": "beta"},
        ]
        result = mgr._fuse_results(vector, [])
        ids = [r["id"] for r in result]
        assert ids == ["a", "b"], "First vector result should rank highest"

    def test_fuse_bm25_only_returns_sorted(self):
        mgr = self._make_manager()
        bm25 = [
            {"id": "x", "score": 5.0, "text": "xray"},
            {"id": "y", "score": 3.0, "text": "yankee"},
        ]
        result = mgr._fuse_results([], bm25)
        ids = [r["id"] for r in result]
        assert ids == ["x", "y"]

    def test_fuse_deduplication_same_id_in_both_lists(self):
        """Same doc in vector and BM25 must appear only once with boosted RRF score."""
        mgr = self._make_manager()
        vector = [{"id": "shared", "score": 0.9, "text": "shared doc", "source": "vector"}]
        bm25 = [{"id": "shared", "score": 8.0, "text": "shared doc", "source": "bm25"}]
        result = mgr._fuse_results(vector, bm25)
        assert len(result) == 1, "Duplicate id must be deduplicated"
        assert result[0]["id"] == "shared"

    def test_fuse_shared_doc_has_higher_score_than_single_list(self):
        """Doc appearing in both lists must have higher RRF score than one appearing in only one."""
        mgr = self._make_manager()
        vector = [
            {"id": "both", "score": 0.8, "text": "in both"},
            {"id": "vec_only", "score": 0.9, "text": "vector only"},
        ]
        bm25 = [
            {"id": "both", "score": 5.0, "text": "in both"},
        ]
        result = mgr._fuse_results(vector, bm25)
        scores = {r["id"]: r["score"] for r in result}
        assert scores["both"] > scores["vec_only"], "Doc in both lists must rank above doc in only one list"

    def test_fuse_rrf_score_formula_k60(self):
        """RRF score for rank-1 doc with k=60 must be 1/(60+1) = 1/61."""
        mgr = self._make_manager()
        vector = [{"id": "only", "score": 1.0, "text": "doc"}]
        result = mgr._fuse_results(vector, [], k=60)
        expected = round(1.0 / 61.0, 8)
        assert result[0]["score"] == pytest.approx(expected, rel=1e-6)

    def test_fuse_result_docs_contain_score_field(self):
        mgr = self._make_manager()
        vector = [{"id": "d1", "score": 0.5, "text": "t1"}]
        result = mgr._fuse_results(vector, [])
        assert "score" in result[0]
        assert isinstance(result[0]["score"], float)

    def test_fuse_deterministic_identical_inputs(self):
        """Identical inputs must produce identical output order."""
        mgr = self._make_manager()
        vector = [
            {"id": "a", "score": 0.9, "text": "a"},
            {"id": "b", "score": 0.8, "text": "b"},
        ]
        bm25 = [
            {"id": "c", "score": 5.0, "text": "c"},
            {"id": "a", "score": 4.0, "text": "a"},
        ]
        result1 = mgr._fuse_results(vector, bm25)
        result2 = mgr._fuse_results(vector, bm25)
        assert [r["id"] for r in result1] == [r["id"] for r in result2]

    def test_fuse_no_mutation_of_input_lists(self):
        """_fuse_results must not mutate the input lists."""
        mgr = self._make_manager()
        vector = [{"id": "a", "score": 0.9, "text": "a"}]
        bm25 = [{"id": "b", "score": 5.0, "text": "b"}]
        v_before = [dict(d) for d in vector]
        b_before = [dict(d) for d in bm25]
        mgr._fuse_results(vector, bm25)
        assert vector == v_before
        assert bm25 == b_before
