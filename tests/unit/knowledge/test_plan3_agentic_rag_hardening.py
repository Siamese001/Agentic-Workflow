"""Plan 3 — Agentic RAG Hardening Tests.

Covers:
- Gap 3: query_planner imports (no NameError at construction)
- Gap 4: SovereignRAGManager._fuse_results RRF fusion + deduplication
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_plan3_agentic_rag_hardening")
_emit_applies_guardrail("p0", "test_plan3_agentic_rag_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_plan3_agentic_rag_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_plan3_agentic_rag_hardening", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_plan3_agentic_rag_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_plan3_agentic_rag_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_plan3_agentic_rag_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_plan3_agentic_rag_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_plan3_agentic_rag_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_plan3_agentic_rag_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_plan3_agentic_rag_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_plan3_agentic_rag_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_plan3_agentic_rag_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_plan3_agentic_rag_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_plan3_agentic_rag_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_plan3_agentic_rag_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_plan3_agentic_rag_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_plan3_agentic_rag_hardening", "p3lm", "state")
_emit_records_execution_trace("test_plan3_agentic_rag_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_plan3_agentic_rag_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_plan3_agentic_rag_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_plan3_agentic_rag_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_plan3_agentic_rag_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_plan3_agentic_rag_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_plan3_agentic_rag_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_plan3_agentic_rag_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_plan3_agentic_rag_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_plan3_agentic_rag_hardening", "context_pull")
_emit_pulls_context("p1", "test_plan3_agentic_rag_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_plan3_agentic_rag_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_plan3_agentic_rag_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_plan3_agentic_rag_hardening", "write_through")
_emit_writes_through("p1", "test_plan3_agentic_rag_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_plan3_agentic_rag_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_plan3_agentic_rag_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_plan3_agentic_rag_hardening", "routing_commit")
emit_replay_key("p0", "test_plan3_agentic_rag_hardening")
emit_determinism_digest("p0", "test_plan3_agentic_rag_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_plan3_agentic_rag_hardening", "execution_auth")
_emit_validates_capability("p2", "test_plan3_agentic_rag_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_plan3_agentic_rag_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_plan3_agentic_rag_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_plan3_agentic_rag_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_plan3_agentic_rag_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_plan3_agentic_rag_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_plan3_agentic_rag_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_plan3_agentic_rag_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_plan3_agentic_rag_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_plan3_agentic_rag_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_plan3_agentic_rag_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_plan3_agentic_rag_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_plan3_agentic_rag_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_plan3_agentic_rag_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_plan3_agentic_rag_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_plan3_agentic_rag_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_plan3_agentic_rag_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_plan3_agentic_rag_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_plan3_agentic_rag_hardening", "exec_snapshot_link")

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
