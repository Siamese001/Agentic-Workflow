"""ADG-driven tests for L2 enforcement modules — fan_in=1.

Covers: healer_pipe_order, tool_policy_enforcer.
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

_emit_records_execution_trace("p0", "evidence", "test_l2_enforcement_adg")
_emit_applies_guardrail("p0", "test_l2_enforcement_adg", "p0_governance")
_emit_snapshots_state("p0", "test_l2_enforcement_adg", "state_snapshot")
emit_replay_key("p0", "test_l2_enforcement_adg")
emit_determinism_digest("p0", "test_l2_enforcement_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l2_enforcement_adg", "execution_auth")
_emit_validates_capability("p2", "test_l2_enforcement_adg", "capability_check")
_emit_routes_to_capability("p2", "test_l2_enforcement_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_l2_enforcement_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_l2_enforcement_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l2_enforcement_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_l2_enforcement_adg", "exec_output")
_emit_dispatches_agent("p3", "test_l2_enforcement_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l2_enforcement_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l2_enforcement_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l2_enforcement_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_l2_enforcement_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l2_enforcement_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l2_enforcement_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l2_enforcement_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l2_enforcement_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l2_enforcement_adg", "eval_metric")
_emit_stores_embedding("p4", "test_l2_enforcement_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l2_enforcement_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l2_enforcement_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# healer_pipe_order
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.enforcement.healer_pipe_order import (
    enforce_healer_pipe_order,
)

_CANONICAL_10 = (
    "pre_audit",
    "discovery",
    "reconciliation",
    "alignment",
    "arch_validation",
    "healing",
    "certification",
    "post_audit",
    "cleanup",
    "report",
)


class TestHealerPipeOrder:
    def test_enforce_callable(self):
        assert callable(enforce_healer_pipe_order)

    def test_passes_on_exact_match(self):
        enforce_healer_pipe_order(
            expected_steps=_CANONICAL_10,
            observed_steps=list(_CANONICAL_10),
        )

    def test_raises_on_wrong_length(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=list(_CANONICAL_10)[:-1],
            )

    def test_raises_on_extra_step(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=list(_CANONICAL_10) + ["extra"],
            )

    def test_raises_on_wrong_order(self):
        reordered = list(_CANONICAL_10)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(
                expected_steps=_CANONICAL_10,
                observed_steps=reordered,
            )

    def test_requires_exactly_10_expected_steps(self):
        with pytest.raises(AssertionError):
            enforce_healer_pipe_order(
                expected_steps=("only_one",),
                observed_steps=["only_one"],
            )

    def test_trace_id_accepted(self):
        enforce_healer_pipe_order(
            expected_steps=_CANONICAL_10,
            observed_steps=list(_CANONICAL_10),
            trace_id="test-trace-001",
        )


# ---------------------------------------------------------------------------
# tool_policy_enforcer
# ---------------------------------------------------------------------------
from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
    ToolPolicyEnforcer,
    _stable_args_hash,
)
from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
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

_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_l2_enforcement_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_l2_enforcement_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_l2_enforcement_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_l2_enforcement_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_l2_enforcement_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_l2_enforcement_adg", "p4obs", "alert")
_emit_links_incident_trace("test_l2_enforcement_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_l2_enforcement_adg", "p3lm", "pattern")
_emit_records_learning_event("test_l2_enforcement_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_l2_enforcement_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_l2_enforcement_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_l2_enforcement_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_l2_enforcement_adg", "p3lm", "policy")
_emit_stores_learning_state("test_l2_enforcement_adg", "p3lm", "state")
_emit_records_execution_trace("test_l2_enforcement_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_l2_enforcement_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_l2_enforcement_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_l2_enforcement_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_l2_enforcement_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_l2_enforcement_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_l2_enforcement_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_l2_enforcement_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_l2_enforcement_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_l2_enforcement_adg", "context_pull")
_emit_pulls_context("p1", "test_l2_enforcement_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_l2_enforcement_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_l2_enforcement_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_l2_enforcement_adg", "write_through")
_emit_writes_through("p1", "test_l2_enforcement_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_l2_enforcement_adg", "safety_validation")
_emit_invokes_eval("p1", "test_l2_enforcement_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_l2_enforcement_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_l2_enforcement_adg", "human_escalation")
_emit_routes_through("p1", "test_l2_enforcement_adg", "route_through")
_emit_checks_agent_registry("p1", "test_l2_enforcement_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_l2_enforcement_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_l2_enforcement_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_l2_enforcement_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_l2_enforcement_adg", "target_agent")
_emit_verifies_policy("p1", "test_l2_enforcement_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_l2_enforcement_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_l2_enforcement_adg", "boundary_check")
_emit_transcripts_response("p1", "test_l2_enforcement_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_l2_enforcement_adg")
_emit_gated_by_confidence("p1", "test_l2_enforcement_adg", "confidence_gate")


class TestStableArgsHash:
    def test_returns_string(self):
        h = _stable_args_hash({"key": "value"})
        assert isinstance(h, str)

    def test_deterministic(self):
        a = _stable_args_hash({"b": 2, "a": 1})
        b = _stable_args_hash({"a": 1, "b": 2})
        assert a == b

    def test_different_args_different_hash(self):
        a = _stable_args_hash({"key": "a"})
        b = _stable_args_hash({"key": "b"})
        assert a != b


class TestToolPolicyEnforcerInit:
    def test_creates(self):
        enforcer = ToolPolicyEnforcer()
        assert enforcer is not None

    def test_policy_rules_start_empty(self):
        enforcer = ToolPolicyEnforcer()
        assert enforcer._policy_rules == {}

    def test_has_register_rule(self):
        assert hasattr(ToolPolicyEnforcer, "register_rule")

    def test_has_enforce(self):
        assert hasattr(ToolPolicyEnforcer, "enforce")


class TestToolPolicyEnforcerEnforce:
    def setup_method(self):
        self.enforcer = ToolPolicyEnforcer()

    def test_enforce_unknown_tool_returns_tuple(self):
        result = self.enforcer.enforce(
            tool_name="read_file",
            args={"path": "foo.py"},
        )
        assert isinstance(result, tuple)
        assert len(result) >= 2

    def test_enforce_default_outcome_pass(self):
        outcome, *_ = self.enforcer.enforce(
            tool_name="write_file",
            args={"path": "foo.py", "content": "hello"},
        )
        assert outcome == LawSlotOutcome.PASS

    def test_register_block_rule_enforces(self):
        self.enforcer.register_rule(
            "dangerous_tool",
            outcome=LawSlotOutcome.BLOCK,
            rationale="unsafe",
        )
        outcome, *_ = self.enforcer.enforce(
            tool_name="dangerous_tool",
            args={},
        )
        assert outcome == LawSlotOutcome.BLOCK
