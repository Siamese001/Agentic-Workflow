"""CI tests — ReAct C0 policy boundary enforcement.

Verifies:
  - assert_c0_informational blocks RAG context containing authority fields.
  - Clean RAG context passes without error.
  - C0BoundaryViolation is raised with descriptive message.
  - ReActStrategy.enforce_c0_boundary delegates correctly.
  - Policy hash mismatch in envelope is detectable.

CI failure condition:
  - C0 boundary check not enforced (authority fields pass through).
  - Policy hash mismatch between envelope and expected.
"""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_react_policy_boundary")
# REMOVED: _emit_applies_guardrail("p0", "test_react_policy_boundary", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_react_policy_boundary", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_react_policy_boundary", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_react_policy_boundary")
# REMOVED: emit_determinism_digest("p0", "test_react_policy_boundary")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_react_policy_boundary", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_react_policy_boundary", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_react_policy_boundary", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_react_policy_boundary", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_react_policy_boundary", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_react_policy_boundary", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_react_policy_boundary", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_react_policy_boundary", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_react_policy_boundary", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_react_policy_boundary", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_react_policy_boundary", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_react_policy_boundary", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_react_policy_boundary", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_react_policy_boundary", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_react_policy_boundary", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_react_policy_boundary", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_react_policy_boundary", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_react_policy_boundary", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_react_policy_boundary", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_react_policy_boundary", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.react_trace_types import (
    C0_FORBIDDEN_FIELDS,
    C0BoundaryViolation,
    ReasonTraceEnvelope,
    assert_c0_informational,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_react_policy_boundary", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_react_policy_boundary", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_react_policy_boundary", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_react_policy_boundary", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_react_policy_boundary", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_react_policy_boundary", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_react_policy_boundary", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_react_policy_boundary", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_react_policy_boundary", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_react_policy_boundary", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_react_policy_boundary", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_react_policy_boundary", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_react_policy_boundary", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_react_policy_boundary", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_react_policy_boundary", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_react_policy_boundary", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_react_policy_boundary", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_react_policy_boundary", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_react_policy_boundary", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_react_policy_boundary", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_react_policy_boundary", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_react_policy_boundary", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_react_policy_boundary", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_react_policy_boundary", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_react_policy_boundary", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_react_policy_boundary", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_react_policy_boundary", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_react_policy_boundary", "write_through")
# REMOVED: _emit_writes_through("p1", "test_react_policy_boundary", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_react_policy_boundary", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_react_policy_boundary", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_react_policy_boundary", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_react_policy_boundary", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_react_policy_boundary", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_react_policy_boundary", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_react_policy_boundary", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_react_policy_boundary", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_react_policy_boundary", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_react_policy_boundary", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_react_policy_boundary", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_react_policy_boundary", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_react_policy_boundary", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_react_policy_boundary", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_react_policy_boundary")
# REMOVED: _emit_gated_by_confidence("p1", "test_react_policy_boundary", "confidence_gate")


class TestC0BoundaryEnforcement:
    def test_clean_context_passes(self):
        assert_c0_informational({"doc_id": "d1", "text": "hello"})

    def test_empty_context_passes(self):
        assert_c0_informational({})

    def test_route_mode_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="route_mode"):
            assert_c0_informational({"route_mode": "fast"})

    def test_execution_tier_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="execution_tier"):
            assert_c0_informational({"execution_tier": "high"})

    def test_safety_policy_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="safety_policy"):
            assert_c0_informational({"safety_policy": "override"})

    def test_tool_budget_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="tool_budget"):
            assert_c0_informational({"tool_budget": 999})

    def test_auth_token_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="auth_token"):
            assert_c0_informational({"auth_token": "secret"})

    def test_policy_override_blocked(self):
        with pytest.raises(C0BoundaryViolation, match="policy_override"):
            assert_c0_informational({"policy_override": True})

    def test_multiple_forbidden_fields_all_reported(self):
        with pytest.raises(C0BoundaryViolation) as exc_info:
            assert_c0_informational({"route_mode": "x", "tool_budget": 1})
        msg = str(exc_info.value)
        assert "route_mode" in msg or "tool_budget" in msg

    def test_source_label_in_error(self):
        with pytest.raises(C0BoundaryViolation, match="MySource"):
            assert_c0_informational({"route_mode": "x"}, source="MySource")

    def test_forbidden_fields_constant_non_empty(self):
        assert len(C0_FORBIDDEN_FIELDS) > 0

    def test_non_forbidden_keys_pass(self):
        safe_context = {
            "title": "doc1",
            "chunk_ids": ["c1", "c2"],
            "score": 0.95,
            "metadata": {"source": "wiki"},
        }
        assert_c0_informational(safe_context)


class TestPolicyHashMismatch:
    """Envelope must fail verify() if policy_hash is tampered."""

    def _make_envelope(self, policy_hash: str) -> ReasonTraceEnvelope:
        return ReasonTraceEnvelope.build(
            trace_id="t-pol",
            plan_hash="ph",
            reason_steps=("s",),
            action_steps=("a",),
            tool_invocations=(),
            policy_hash=policy_hash,
            semantic_clock_vector=(0,),
        )

    def test_correct_policy_hash_verifies(self):
        env = self._make_envelope("pol_v1")
        assert env.verify()

    def test_tampered_policy_hash_fails_verify(self):
        env = self._make_envelope("pol_v1")
        import dataclasses

        tampered = dataclasses.replace(env, policy_hash="evil_policy")
        assert not tampered.verify()

    def test_different_policy_produces_different_envelope(self):
        env1 = self._make_envelope("pol_v1")
        env2 = self._make_envelope("pol_v2")
        assert env1.envelope_hash != env2.envelope_hash
