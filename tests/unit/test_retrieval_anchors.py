"""
Phase 2 Wave 2 — RetrievalAnchor Tests

Tests that:
- RetrievalAnchor requires all fields
- AnchoredResult pairs content with anchor
- enforce_anchor_coverage blocks unanchored retrieval use
- Negative: reasoning without anchors raises AnchorViolationError
"""

from __future__ import annotations

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_retrieval_anchors", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_retrieval_anchors", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_retrieval_anchors", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_retrieval_anchors", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_retrieval_anchors", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_retrieval_anchors", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_retrieval_anchors", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_retrieval_anchors", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_retrieval_anchors", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_retrieval_anchors", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_retrieval_anchors", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_retrieval_anchors", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_retrieval_anchors", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_retrieval_anchors", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_retrieval_anchors", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_retrieval_anchors", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_retrieval_anchors", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_retrieval_anchors", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_retrieval_anchors", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_retrieval_anchors", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_retrieval_anchors", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_retrieval_anchors", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_retrieval_anchors", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_retrieval_anchors")
# REMOVED: _emit_applies_guardrail("p0", "test_retrieval_anchors", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_retrieval_anchors", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_retrieval_anchors", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_retrieval_anchors", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_retrieval_anchors", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_retrieval_anchors", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_retrieval_anchors", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_retrieval_anchors", "write_through")
# REMOVED: _emit_writes_through("p1", "test_retrieval_anchors", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_retrieval_anchors", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_retrieval_anchors", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_retrieval_anchors", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_retrieval_anchors", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_retrieval_anchors", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_retrieval_anchors", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_retrieval_anchors", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_retrieval_anchors", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_retrieval_anchors", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_retrieval_anchors", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_retrieval_anchors", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_retrieval_anchors", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_retrieval_anchors", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_retrieval_anchors", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_retrieval_anchors")
# REMOVED: _emit_gated_by_confidence("p1", "test_retrieval_anchors", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_retrieval_anchors")
# REMOVED: emit_determinism_digest("p0", "test_retrieval_anchors")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_retrieval_anchors", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_retrieval_anchors", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_retrieval_anchors", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_retrieval_anchors", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_retrieval_anchors", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_retrieval_anchors", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_retrieval_anchors", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_retrieval_anchors", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_retrieval_anchors", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_retrieval_anchors", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_retrieval_anchors", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_retrieval_anchors", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_retrieval_anchors", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_retrieval_anchors", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_retrieval_anchors", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_retrieval_anchors", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_retrieval_anchors", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_retrieval_anchors", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_retrieval_anchors", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_retrieval_anchors", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


def _make_anchor(
    source_doc_id: str = "doc-001",
    chunk_id: str = "chunk-001",
    char_start: int = 0,
    char_end: int = 100,
    version_hash: str = "abc123",
) -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=char_start,
        char_end=char_end,
        retrieved_at_utc=RetrievalAnchor.now_utc(),
        version_hash=version_hash,
    )


class TestRetrievalAnchor:
    def test_retrieval_returns_anchors(self):
        from agentic_core.L4_state.types.retrieval_anchor_types import (
            AnchoredResult,
            AnchorViolationError,
            RetrievalAnchor,
            enforce_anchor_coverage,
        )
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
            _emit_agent_executes_agent,
            _emit_applies_guardrail,  # noqa: E402
            _emit_authorize_and_execute,
            _emit_blocks_direct_write,
            _emit_captures_evaluation_metric,
            _emit_captures_execution_output,
            _emit_captures_pattern,
            _emit_captures_runtime_anomaly,
            _emit_checks_agent_registry,
            _emit_coordinates_agents,
            _emit_dispatches_agent,
            _emit_dispatches_execution_plan,
            _emit_dispatches_healing_run,
            _emit_emits_metric_event,
            _emit_escalates_failure,
            _emit_escalates_to_human,
            _emit_execution_terminates_at_uwg,
            _emit_feeds_meta_learning,
            _emit_gated_by_confidence,
            _emit_hard_fails_untranscripted,
            _emit_improves_agent_policy,
            _emit_invokes_eval,
            _emit_invokes_evaluation,
            _emit_links_execution_to_snapshot,
            _emit_links_incident_trace,  # noqa: E402
            _emit_observes_runtime_state,
            _emit_orchestrates_workflow,
            _emit_proposal_commits_routing,
            _emit_pulls_context,
            _emit_reads_environ,
            _emit_reads_policy_state,  # noqa: E402
            _emit_reads_runtime_state,
            _emit_records_execution_trace,  # noqa: E402
            _emit_records_healing_outcome,
            _emit_records_incident_event,
            _emit_records_learning_event,
            _emit_records_telemetry_event,
            _emit_records_tool_invocation,
            _emit_records_workflow_lineage,
            _emit_routes_through,
            _emit_routes_to_agent,
            _emit_routes_to_capability,
            _emit_signs_execution_trace,  # noqa: E402
            _emit_snapshots_state,  # noqa: E402
            _emit_stores_embedding,
            _emit_stores_learning_state,
            _emit_transcripts_response,
            _emit_triggers_alert,
            _emit_updates_meta_learning_state,
            _emit_updates_monitoring_state,
            _emit_updates_routing_strategy,
            _emit_validated_by_safety_plane,
            _emit_validates_agent_capability,
            _emit_validates_capability,
            _emit_verifies_boundary,
            _emit_verifies_policy,
            _emit_writes_learning_snapshot,
            _emit_writes_observability_log,
            _emit_writes_through,  # noqa: E402
            _emit_writes_via_uwg,
            emit_determinism_digest,  # noqa: E402
            emit_replay_key,  # noqa: E402

        anchor = _make_anchor()
        result = AnchoredResult(content="some retrieved text", anchor=anchor)
        assert result.anchor.source_doc_id == "doc-001"
        assert result.anchor.chunk_id == "chunk-001"
        assert result.anchor.char_start == 0
        assert result.anchor.char_end == 100
        assert result.anchor.version_hash == "abc123"
        assert result.anchor.retrieved_at_utc

    def test_anchor_to_dict_has_all_fields(self):
        anchor = _make_anchor()
        d = anchor.to_dict()
        assert set(d.keys()) == {
            "source_doc_id",
            "chunk_id",
            "char_start",
            "char_end",
            "retrieved_at_utc",
            "version_hash",
        }

    def test_anchor_rejects_empty_source_doc_id(self):
        with pytest.raises(ValueError, match="source_doc_id"):
            RetrievalAnchor(
                source_doc_id="",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_chunk_id(self):
        with pytest.raises(ValueError, match="chunk_id"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_inverted_offsets(self):
        with pytest.raises(ValueError, match="char_end"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=100,
                char_end=50,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="abc",
            )

    def test_anchor_rejects_empty_version_hash(self):
        with pytest.raises(ValueError, match="version_hash"):
            RetrievalAnchor(
                source_doc_id="doc-001",
                chunk_id="chunk-001",
                char_start=0,
                char_end=10,
                retrieved_at_utc=RetrievalAnchor.now_utc(),
                version_hash="",
            )


class TestAnchorCoverageEnforcement:
    def test_empty_retrieval_context_passes_with_no_anchors(self):
        enforce_anchor_coverage([], [])

    def test_reasoning_requires_anchors_when_retrieval_present(self):
        anchor = _make_anchor()
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert AnchorViolationError.VIOLATION_CODE in str(exc_info.value)
        assert "empty" in str(exc_info.value)

    def test_reasoning_without_anchors_is_rejected(self):
        anchor = _make_anchor(chunk_id="chunk-A")
        result = AnchoredResult(content="text", anchor=anchor)
        with pytest.raises(AnchorViolationError) as exc_info:
            enforce_anchor_coverage([result], [])
        assert "MISSING_RETRIEVAL_ANCHOR" in str(exc_info.value)

    def test_uncovered_chunk_raises_violation(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        with pytest.raises(AnchorViolationError, match="chunk-B"):
            enforce_anchor_coverage([result_a, result_b], [anchor_a])

    def test_full_coverage_passes(self):
        anchor_a = _make_anchor(chunk_id="chunk-A")
        anchor_b = _make_anchor(chunk_id="chunk-B")
        result_a = AnchoredResult(content="text-a", anchor=anchor_a)
        result_b = AnchoredResult(content="text-b", anchor=anchor_b)
        enforce_anchor_coverage([result_a, result_b], [anchor_a, anchor_b])

    def test_violation_error_code_is_constant(self):
        assert AnchorViolationError.VIOLATION_CODE == "MISSING_RETRIEVAL_ANCHOR"
