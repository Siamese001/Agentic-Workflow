"""
Phase 4 — Wave 1 Tests: ML write envelope enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.ml_write_intent_types import (
    MLWriteEnvelopeViolation,
    MLWriteIntent,
    MLWriteIntentExecutor,
    execute_ml_write_intent_outside_sandbox,
    is_commit_sandbox_active,
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
)

# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ml_write_envelope", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ml_write_envelope", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ml_write_envelope", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ml_write_envelope", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ml_write_envelope", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ml_write_envelope", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ml_write_envelope", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ml_write_envelope", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ml_write_envelope", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ml_write_envelope", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ml_write_envelope", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ml_write_envelope", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ml_write_envelope", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ml_write_envelope", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ml_write_envelope", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ml_write_envelope", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ml_write_envelope", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ml_write_envelope", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ml_write_envelope", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ml_write_envelope", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ml_write_envelope", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ml_write_envelope", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ml_write_envelope", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ml_write_envelope")
# REMOVED: _emit_applies_guardrail("p0", "test_ml_write_envelope", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ml_write_envelope", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ml_write_envelope", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_ml_write_envelope", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ml_write_envelope", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ml_write_envelope", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ml_write_envelope", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_ml_write_envelope", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ml_write_envelope", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ml_write_envelope", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ml_write_envelope", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ml_write_envelope", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ml_write_envelope", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ml_write_envelope", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ml_write_envelope", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ml_write_envelope", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ml_write_envelope", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ml_write_envelope", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ml_write_envelope", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ml_write_envelope", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ml_write_envelope", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ml_write_envelope", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ml_write_envelope", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ml_write_envelope")
# REMOVED: _emit_gated_by_confidence("p1", "test_ml_write_envelope", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ml_write_envelope")
# REMOVED: emit_determinism_digest("p0", "test_ml_write_envelope")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ml_write_envelope", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ml_write_envelope", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ml_write_envelope", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ml_write_envelope", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ml_write_envelope", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ml_write_envelope", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ml_write_envelope", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ml_write_envelope", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ml_write_envelope", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ml_write_envelope", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ml_write_envelope", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ml_write_envelope", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ml_write_envelope", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ml_write_envelope", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ml_write_envelope", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ml_write_envelope", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ml_write_envelope", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ml_write_envelope", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ml_write_envelope", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ml_write_envelope", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestMLWriteIntent:
    def test_build_pattern_store_intent(self):
        intent = MLWriteIntent(
            kind="pattern_store",
            payload={"pattern_id": "p-001", "domain": "agentic_core"},
        )
        assert intent.kind == "pattern_store"
        assert intent.requires_commit is True
        assert len(intent.intent_hash) == 64

    def test_build_cache_set_intent(self):
        intent = MLWriteIntent(
            kind="cache_set",
            payload={"key": "k1", "value": "v1", "ttl": 3600},
        )
        assert intent.kind == "cache_set"
        assert len(intent.intent_hash) == 64

    def test_intent_hash_stable(self):
        payload = {"key": "k", "value": "v"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="cache_set", payload=payload)
        assert i1.intent_hash == i2.intent_hash

    def test_intent_hash_differs_by_kind(self):
        payload = {"key": "k"}
        i1 = MLWriteIntent(kind="cache_set", payload=payload)
        i2 = MLWriteIntent(kind="pattern_store", payload=payload)
        assert i1.intent_hash != i2.intent_hash

    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError, match="kind must be one of"):
            MLWriteIntent(kind="direct_pinecone_write", payload={})  # type: ignore[arg-type]

    def test_requires_commit_false_raises(self):
        with pytest.raises(ValueError, match="requires_commit must be True"):
            MLWriteIntent(kind="cache_set", payload={}, requires_commit=False)

    def test_non_dict_payload_raises(self):
        with pytest.raises(TypeError, match="payload must be a dict"):
            MLWriteIntent(kind="cache_set", payload="raw_string")  # type: ignore[arg-type]

    def test_canonical_bytes_deterministic(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"a": 1})
        assert intent.canonical_bytes() == intent.canonical_bytes()


class TestMLWriteSandbox:
    def test_sandbox_inactive_by_default(self):
        assert is_commit_sandbox_active() is False

    def test_sandbox_active_inside_context(self):
        with MLWriteIntentExecutor():
            assert is_commit_sandbox_active() is True

    def test_sandbox_inactive_after_context(self):
        with MLWriteIntentExecutor():
            pass
        assert is_commit_sandbox_active() is False

    def test_ml_write_allowed_inside_commit_sandbox(self):
        intent = MLWriteIntent(kind="pattern_store", payload={"pattern_id": "p-sandbox"})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "pattern_store"
        assert result["intent_hash"] == intent.intent_hash

    def test_ml_write_blocked_outside_commit_sandbox(self):
        """
        Negative: executing MLWriteIntent outside the sandbox raises
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX code.
        """
        executor = MLWriteIntentExecutor()
        intent = MLWriteIntent(kind="cache_set", payload={"key": "k"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            executor.execute(intent)

    def test_direct_write_outside_sandbox_raises(self):
        """
        Negative: direct ML write attempt (simulated via
        execute_ml_write_intent_outside_sandbox) raises MLWriteEnvelopeViolation.
        """
        intent = MLWriteIntent(kind="pattern_store", payload={"domain": "apps_rg"})
        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            execute_ml_write_intent_outside_sandbox(intent)

    def test_violation_error_carries_violation_code(self):
        err = MLWriteEnvelopeViolation("test")
        assert "ML_WRITE_OUTSIDE_SANDBOX" in str(err)

    def test_sandbox_restores_state_on_exception(self):
        """Sandbox must deactivate even if execute() raises."""
        try:
            with MLWriteIntentExecutor():
                assert is_commit_sandbox_active() is True
                raise RuntimeError("simulated failure")
        except RuntimeError:  # guardian: allow-silent-swallower
            pass
        assert is_commit_sandbox_active() is False

    def test_cache_set_allowed_inside_sandbox(self):
        intent = MLWriteIntent(kind="cache_set", payload={"key": "ast-result", "ttl": 3600})
        with MLWriteIntentExecutor() as executor:
            result = executor.execute(intent)
        assert result["executed"] is True
        assert result["kind"] == "cache_set"
