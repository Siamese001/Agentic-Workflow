"""
Unit tests for L5 CONF_CALIB Risk Gate - structured risk decision.
"""

import pytest

from agentic_core.L5_safety.enforcement.conf_calib_gate import (
    ConfCalibRiskGate,
    RiskDecision,
    RiskLevel,
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

_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_1")
_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_2")
_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_3")
_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_4")
_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_5")
_emit_emits_metric_event("test_conf_calib_gate", "p4obs", "metric_6")
_emit_records_incident_event("test_conf_calib_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_conf_calib_gate", "p4obs", "anomaly")
_emit_writes_observability_log("test_conf_calib_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_conf_calib_gate", "p4obs", "mon_state")
_emit_triggers_alert("test_conf_calib_gate", "p4obs", "alert")
_emit_links_incident_trace("test_conf_calib_gate", "p4obs", "trace_link")
_emit_captures_pattern("test_conf_calib_gate", "p3lm", "pattern")
_emit_records_learning_event("test_conf_calib_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_conf_calib_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_conf_calib_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_conf_calib_gate", "p3lm", "routing")
_emit_improves_agent_policy("test_conf_calib_gate", "p3lm", "policy")
_emit_stores_learning_state("test_conf_calib_gate", "p3lm", "state")
_emit_records_execution_trace("test_conf_calib_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_conf_calib_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_conf_calib_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_conf_calib_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_conf_calib_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_conf_calib_gate", "env_read", "p2_env_1")
_emit_reads_environ("test_conf_calib_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_conf_calib_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_conf_calib_gate", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_conf_calib_gate")
_emit_applies_guardrail("p0", "test_conf_calib_gate", "p0_governance")
_emit_reads_policy_state("p0", "test_conf_calib_gate", "policy_binding")
_emit_snapshots_state("p0", "test_conf_calib_gate", "state_snapshot")
_emit_pulls_context("p1", "test_conf_calib_gate", "context_pull")
_emit_pulls_context("p1", "test_conf_calib_gate", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_conf_calib_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_conf_calib_gate", "uwg_term_secondary")
_emit_writes_through("p1", "test_conf_calib_gate", "write_through")
_emit_writes_through("p1", "test_conf_calib_gate", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_conf_calib_gate", "safety_validation")
_emit_invokes_eval("p1", "test_conf_calib_gate", "eval_call")
_emit_proposal_commits_routing("p1", "test_conf_calib_gate", "routing_commit")
_emit_escalates_to_human("p1", "test_conf_calib_gate", "human_escalation")
_emit_routes_through("p1", "test_conf_calib_gate", "route_through")
_emit_checks_agent_registry("p1", "test_conf_calib_gate", "agent_registry")
_emit_validates_agent_capability("p1", "test_conf_calib_gate", "capability")
_emit_dispatches_execution_plan("p1", "test_conf_calib_gate", "exec_plan")
_emit_agent_executes_agent("p1", "test_conf_calib_gate", "sub_agent")
_emit_routes_to_agent("p1", "test_conf_calib_gate", "target_agent")
_emit_verifies_policy("p1", "test_conf_calib_gate", "policy_check")
_emit_observes_runtime_state("p1", "test_conf_calib_gate", "runtime_state")
_emit_verifies_boundary("p1", "test_conf_calib_gate", "boundary_check")
_emit_transcripts_response("p1", "test_conf_calib_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "test_conf_calib_gate")
_emit_gated_by_confidence("p1", "test_conf_calib_gate", "confidence_gate")
emit_replay_key("p0", "test_conf_calib_gate")
emit_determinism_digest("p0", "test_conf_calib_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_conf_calib_gate", "execution_auth")
_emit_validates_capability("p2", "test_conf_calib_gate", "capability_check")
_emit_routes_to_capability("p2", "test_conf_calib_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_conf_calib_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_conf_calib_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_conf_calib_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_conf_calib_gate", "exec_output")
_emit_dispatches_agent("p3", "test_conf_calib_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_conf_calib_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_conf_calib_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_conf_calib_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_conf_calib_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_conf_calib_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_conf_calib_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_conf_calib_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_conf_calib_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_conf_calib_gate", "eval_metric")
_emit_stores_embedding("p4", "test_conf_calib_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_conf_calib_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_conf_calib_gate", "exec_snapshot_link")


@pytest.mark.unit
class TestConfCalibRiskGate:
    """Test deterministic ConfCalibRiskGate implementation."""

    def test_risk_level_enum_values(self):
        """Test RiskLevel enum has correct values."""
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MEDIUM.value == "MEDIUM"
        assert RiskLevel.HIGH.value == "HIGH"

    def test_risk_decision_dataclass(self):
        """Test RiskDecision dataclass properties."""
        decision = RiskDecision(allow=True, level=RiskLevel.LOW, reasons=("reason1", "reason2"))

        assert decision.allow is True
        assert decision.level == RiskLevel.LOW
        assert decision.reasons == ("reason1", "reason2")
        assert decision == RiskDecision(allow=True, level=RiskLevel.LOW, reasons=("reason1", "reason2"))

    def test_evaluate_default_low_risk(self):
        """Test default evaluation returns LOW risk with allow=True."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.LOW
        assert result.reasons == ()

    def test_sanitized_input_elevates_to_medium(self):
        """Test sanitized input elevates risk to MEDIUM."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("SANITIZED_INPUT",)

    def test_many_check_ids_triggers_medium(self):
        """Test many check_ids triggers MEDIUM risk."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("MANY_CHECK_IDS",)

    def test_deny_execution_forces_high_and_disallows(self):
        """Test DENY_EXECUTION forces HIGH risk and disallows execution."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[deny] DENY_EXECUTION\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is False
        assert result.level == RiskLevel.HIGH
        assert result.reasons == ("D0_DENY_EXECUTION",)

    def test_determinism_identical_inputs_identical_outputs(self):
        """Test identical inputs produce identical RiskDecision."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result1 = gate.evaluate(payload_like=payload, d0_injections=d0)
        result2 = gate.evaluate(payload_like=payload, d0_injections=d0)
        result3 = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result1 == result2 == result3
        assert result1.reasons == result2.reasons == result3.reasons

    def test_multiple_reasons_sorted_lexicographically(self):
        """Test multiple reasons are sorted lexicographically."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.level == RiskLevel.MEDIUM
        assert result.allow is True
        assert result.reasons == ("MANY_CHECK_IDS", "SANITIZED_INPUT")

    def test_deny_execution_forces_high_and_disallows(self):
        """Test DENY_EXECUTION forces HIGH risk and disallows execution."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[deny] DENY_EXECUTION\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        # DENY_EXECUTION should force HIGH and disallow
        assert result.allow is False
        assert result.level == RiskLevel.HIGH
        # DENY_EXECUTION should be included with other reasons
        expected_reasons = ("D0_DENY_EXECUTION", "MANY_CHECK_IDS", "SANITIZED_INPUT")
        assert result.reasons == expected_reasons

    def test_missing_attributes_default_to_safe(self):
        """Test missing attributes default to safe values."""
        gate = ConfCalibRiskGate()

        # Payload with no sanitized or check_ids attributes
        class MinimalPayload:
            pass

        payload = MinimalPayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.LOW
        assert result.reasons == ()

    def test_payload_like_not_mutated(self):
        """Test payload_like object is not mutated during evaluation."""
        gate = ConfCalibRiskGate()

        class TestPayload:
            def __init__(self):
                self.sanitized = True
                self.check_ids = ("id1", "id2")
                self.extra_field = "unchanged"

        payload = TestPayload()
        original_state = {
            "sanitized": payload.sanitized,
            "check_ids": payload.check_ids,
            "extra_field": payload.extra_field,
        }

        d0 = "<D0>\n[test] Content\n</D0>\n"
        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        # Verify payload was not mutated
        assert payload.sanitized == original_state["sanitized"]
        assert payload.check_ids == original_state["check_ids"]
        assert payload.extra_field == original_state["extra_field"]

        # Verify evaluation worked
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("SANITIZED_INPUT",)
