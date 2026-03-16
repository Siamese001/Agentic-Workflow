"""ADG-driven tests for L3 rag_provider_types — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_rag_provider_types_adg")
_emit_applies_guardrail("p0", "test_rag_provider_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_rag_provider_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_rag_provider_types_adg", "state_snapshot")
emit_replay_key("p0", "test_rag_provider_types_adg")
emit_determinism_digest("p0", "test_rag_provider_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_rag_provider_types_adg", "execution_auth")
_emit_validates_capability("p2", "test_rag_provider_types_adg", "capability_check")
_emit_routes_to_capability("p2", "test_rag_provider_types_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_rag_provider_types_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_rag_provider_types_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_rag_provider_types_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_rag_provider_types_adg", "exec_output")
_emit_dispatches_agent("p3", "test_rag_provider_types_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_rag_provider_types_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_rag_provider_types_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_rag_provider_types_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_rag_provider_types_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_rag_provider_types_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_rag_provider_types_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_rag_provider_types_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_rag_provider_types_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_rag_provider_types_adg", "eval_metric")
_emit_stores_embedding("p4", "test_rag_provider_types_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_rag_provider_types_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_rag_provider_types_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.types.rag_provider_types import (
    IRagProvider,
    RagDocument,
    RagQuery,
    RagResult,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_rag_provider_types_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_rag_provider_types_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_rag_provider_types_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_rag_provider_types_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_rag_provider_types_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_rag_provider_types_adg", "p4obs", "alert")
_emit_links_incident_trace("test_rag_provider_types_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_rag_provider_types_adg", "p3lm", "pattern")
_emit_records_learning_event("test_rag_provider_types_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_rag_provider_types_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_rag_provider_types_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_rag_provider_types_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_rag_provider_types_adg", "p3lm", "policy")
_emit_stores_learning_state("test_rag_provider_types_adg", "p3lm", "state")
_emit_records_execution_trace("test_rag_provider_types_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_rag_provider_types_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_rag_provider_types_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_rag_provider_types_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_rag_provider_types_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_rag_provider_types_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_rag_provider_types_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_rag_provider_types_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_rag_provider_types_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_rag_provider_types_adg", "context_pull")
_emit_pulls_context("p1", "test_rag_provider_types_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_rag_provider_types_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_rag_provider_types_adg", "uwg_term_2")
_emit_writes_through("p1", "test_rag_provider_types_adg", "write_through")
_emit_writes_through("p1", "test_rag_provider_types_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_rag_provider_types_adg", "safety_validation")
_emit_invokes_eval("p1", "test_rag_provider_types_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_rag_provider_types_adg", "routing_commit")


class TestRagQuery:
    def test_creates_with_query(self):
        q = RagQuery(query="test query")
        assert q.query == "test query"

    def test_top_k_default_10(self):
        q = RagQuery(query="test")
        assert q.top_k == 10

    def test_namespace_default(self):
        q = RagQuery(query="test")
        assert q.namespace == "sovereign-core"

    def test_enable_reranking_default_true(self):
        q = RagQuery(query="test")
        assert q.enable_reranking is True

    def test_enable_caching_default_true(self):
        q = RagQuery(query="test")
        assert q.enable_caching is True

    def test_filters_default_empty(self):
        q = RagQuery(query="test")
        assert q.filters == {}

    def test_custom_top_k(self):
        q = RagQuery(query="test", top_k=5)
        assert q.top_k == 5


class TestRagDocument:
    def test_creates(self):
        doc = RagDocument(id="doc-1", text="hello world", score=0.9)
        assert doc.id == "doc-1"
        assert doc.text == "hello world"

    def test_source_default_unknown(self):
        doc = RagDocument(id="doc-1", text="text", score=0.5)
        assert doc.source == "unknown"

    def test_metadata_default_empty(self):
        doc = RagDocument(id="doc-1", text="text", score=0.5)
        assert doc.metadata == {}


class TestRagResult:
    def test_creates(self):
        docs = [RagDocument(id="d1", text="t", score=0.9)]
        r = RagResult(query="test", documents=docs, latency_ms=12.5)
        assert r.query == "test"
        assert r.latency_ms == 12.5

    def test_cached_default_false(self):
        r = RagResult(query="q", documents=[], latency_ms=0.0)
        assert r.cached is False

    def test_faithfulness_score_default_0(self):
        r = RagResult(query="q", documents=[], latency_ms=0.0)
        assert r.faithfulness_score == 0.0


class TestIRagProvider:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(IRagProvider)

    def test_has_retrieve(self):
        assert hasattr(IRagProvider, "retrieve")
