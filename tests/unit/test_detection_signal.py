"""
Phase 3 — Wave 1 Tests: DetectionSignal model + emission hook.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal,
    emit_signal_from_gateway_result,
)
from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
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

# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_detection_signal", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_detection_signal", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_detection_signal", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_detection_signal", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_detection_signal", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_detection_signal", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_detection_signal", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_detection_signal", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_detection_signal", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_detection_signal", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_detection_signal", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_detection_signal", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_detection_signal", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_detection_signal", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_detection_signal", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_detection_signal", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_detection_signal", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_detection_signal", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_detection_signal", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_detection_signal", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_detection_signal", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_detection_signal", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_detection_signal", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_detection_signal")
# REMOVED: _emit_applies_guardrail("p0", "test_detection_signal", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_detection_signal", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_detection_signal", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_detection_signal", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_detection_signal", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_detection_signal", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_detection_signal", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_detection_signal", "write_through")
# REMOVED: _emit_writes_through("p1", "test_detection_signal", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_detection_signal", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_detection_signal", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_detection_signal", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_detection_signal", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_detection_signal", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_detection_signal", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_detection_signal", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_detection_signal", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_detection_signal", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_detection_signal", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_detection_signal", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_detection_signal", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_detection_signal", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_detection_signal", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_detection_signal")
# REMOVED: _emit_gated_by_confidence("p1", "test_detection_signal", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_detection_signal")
# REMOVED: emit_determinism_digest("p0", "test_detection_signal")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_detection_signal", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_detection_signal", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_detection_signal", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_detection_signal", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_detection_signal", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_detection_signal", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_detection_signal", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_detection_signal", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_detection_signal", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_detection_signal", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_detection_signal", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_detection_signal", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_detection_signal", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_detection_signal", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_detection_signal", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_detection_signal", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_detection_signal", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_detection_signal", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_detection_signal", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_detection_signal", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestDetectionSignalModel:
    def test_build_produces_valid_signal(self):
        sig = DetectionSignal.build(
            mission_id="m-001",
            created_at_utc=1_700_000_000,
            anomaly_score=0.3,
            escalation_rate=0.1,
            retry_rate=0.2,
            violation_density=0.05,
        )
        assert sig.schema_version == 1
        assert sig.mission_id == "m-001"
        assert sig.anomaly_score == 0.3
        assert len(sig.signal_hash) == 64

    def test_detection_signal_hash_stable(self):
        """Same inputs must produce identical signal_hash across calls."""
        kwargs = {
            "mission_id": "m-stable",
            "created_at_utc": 1_700_000_001,
            "anomaly_score": 0.5,
            "escalation_rate": 0.2,
            "retry_rate": 0.1,
            "violation_density": 0.0,
        }
        sig1 = DetectionSignal.build(**kwargs)
        sig2 = DetectionSignal.build(**kwargs)
        assert sig1.signal_hash == sig2.signal_hash

    def test_different_inputs_produce_different_hash(self):
        sig1 = DetectionSignal.build(
            mission_id="m-a",
            created_at_utc=100,
            anomaly_score=0.1,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        sig2 = DetectionSignal.build(
            mission_id="m-b",
            created_at_utc=100,
            anomaly_score=0.1,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig1.signal_hash != sig2.signal_hash

    def test_canonical_bytes_is_deterministic(self):
        sig = DetectionSignal.build(
            mission_id="m-canon",
            created_at_utc=200,
            anomaly_score=0.0,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig.canonical_bytes() == sig.canonical_bytes()

    def test_canonical_bytes_excludes_signal_hash(self):
        """signal_hash must not appear in canonical_bytes (no circular dependency)."""
        sig = DetectionSignal.build(
            mission_id="m-excl",
            created_at_utc=300,
            anomaly_score=0.2,
            escalation_rate=0.0,
            retry_rate=0.0,
            violation_density=0.0,
        )
        assert sig.signal_hash.encode() not in sig.canonical_bytes()
        assert b"signal_hash" not in sig.canonical_bytes()


class TestDetectionSignalValidation:
    def test_detection_signal_rejects_out_of_range_anomaly_score(self):
        with pytest.raises(ValueError, match="anomaly_score"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=1.5,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_negative_escalation_rate(self):
        with pytest.raises(ValueError, match="escalation_rate"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=-0.1,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_out_of_range_values(self):
        for field_name, kwargs in [
            ("retry_rate", {"retry_rate": 2.0}),
            ("violation_density", {"violation_density": -1.0}),
        ]:
            base = {
                "mission_id": "m",
                "created_at_utc": 1,
                "anomaly_score": 0.0,
                "escalation_rate": 0.0,
                "retry_rate": 0.0,
                "violation_density": 0.0,
            }
            base.update(kwargs)
            with pytest.raises(ValueError, match=field_name):
                DetectionSignal.build(**base)

    def test_detection_signal_rejects_empty_mission_id(self):
        with pytest.raises(ValueError, match="mission_id"):
            DetectionSignal.build(
                mission_id="",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
            )

    def test_detection_signal_rejects_bad_schema_version(self):
        with pytest.raises(ValueError, match="schema_version"):
            DetectionSignal.build(
                mission_id="m",
                created_at_utc=1,
                anomaly_score=0.0,
                escalation_rate=0.0,
                retry_rate=0.0,
                violation_density=0.0,
                schema_version=0,
            )


class TestEmissionHook:
    def test_emit_detection_signal_returns_valid_signal(self):
        sig = emit_detection_signal(
            mission_id="emit-001",
            created_at_utc=1_700_000_100,
            anomaly_score=0.4,
        )
        assert isinstance(sig, DetectionSignal)
        assert sig.mission_id == "emit-001"
        assert sig.anomaly_score == 0.4

    def test_emission_is_side_effect_free_on_result(self):
        """
        Emitting a signal from a GatewayResult must not modify the result.
        The returned signal is a new object; gateway_result is unchanged.
        """

        class FakeResult:
            success = True
            error = None
            healing_output = {"errors": 0}

        result = FakeResult()
        original_success = result.success
        original_error = result.error

        sig = emit_signal_from_gateway_result(
            mission_id="side-effect-test",
            created_at_utc=1_700_000_200,
            gateway_result=result,
        )

        assert isinstance(sig, DetectionSignal)
        assert result.success == original_success
        assert result.error == original_error

    def test_emit_from_failed_result_raises_anomaly_score(self):
        class FakeFailedResult:
            success = False
            error = "heal failed"

        sig = emit_signal_from_gateway_result(
            mission_id="fail-test",
            created_at_utc=1_700_000_300,
            gateway_result=FakeFailedResult(),
        )
        assert sig.anomaly_score > 0.0

    def test_emit_from_success_result_has_zero_anomaly(self):
        class FakeSuccessResult:
            success = True
            error = None

        sig = emit_signal_from_gateway_result(
            mission_id="success-test",
            created_at_utc=1_700_000_400,
            gateway_result=FakeSuccessResult(),
        )
        assert sig.anomaly_score == 0.0
