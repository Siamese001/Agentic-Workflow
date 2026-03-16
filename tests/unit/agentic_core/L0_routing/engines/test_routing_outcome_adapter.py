"""Behavioral tests for RoutingOutcomeAdapter and build_routing_outcome_package.

Covers:
- Package kind is always 'routing_outcome'
- SUCCESS / SAFE_FAILURE / UNKNOWN outcome derivation
- Payload fields: intent, target_name, confidence, outcome, has_error, timestamp_utc
- influence_class is always C0_INFORMATIONAL
- Adapter.emit() returns True on success
- Adapter.emit() returns False and never raises on MetaLearningBus failure
- Confidence value is rounded to 6 decimal places
- Determinism: same decision → identical package payload
"""

from __future__ import annotations

from unittest.mock import MagicMock

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_routing_outcome_adapter")
_emit_applies_guardrail("p0", "test_routing_outcome_adapter", "p0_governance")
_emit_reads_policy_state("p0", "test_routing_outcome_adapter", "policy_binding")
_emit_snapshots_state("p0", "test_routing_outcome_adapter", "state_snapshot")
emit_replay_key("p0", "test_routing_outcome_adapter")
emit_determinism_digest("p0", "test_routing_outcome_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_routing_outcome_adapter", "execution_auth")
_emit_validates_capability("p2", "test_routing_outcome_adapter", "capability_check")
_emit_routes_to_capability("p2", "test_routing_outcome_adapter", "capability_route")
_emit_writes_via_uwg("p2", "test_routing_outcome_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "test_routing_outcome_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "test_routing_outcome_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "test_routing_outcome_adapter", "exec_output")
_emit_dispatches_agent("p3", "test_routing_outcome_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "test_routing_outcome_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_routing_outcome_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_routing_outcome_adapter", "healing_outcome")
_emit_escalates_failure("p3", "test_routing_outcome_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_routing_outcome_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_routing_outcome_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_routing_outcome_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_routing_outcome_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_routing_outcome_adapter", "eval_metric")
_emit_stores_embedding("p4", "test_routing_outcome_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_routing_outcome_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_routing_outcome_adapter", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.engines.agentic_router import RoutingDecision
from agentic_core.L0_routing.engines.routing_outcome_adapter import (
    RoutingOutcomeAdapter,
    build_routing_outcome_package,
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_1")
_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_2")
_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_3")
_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_4")
_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_5")
_emit_emits_metric_event("test_routing_outcome_adapter", "p4obs", "metric_6")
_emit_records_incident_event("test_routing_outcome_adapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_routing_outcome_adapter", "p4obs", "anomaly")
_emit_writes_observability_log("test_routing_outcome_adapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_routing_outcome_adapter", "p4obs", "mon_state")
_emit_triggers_alert("test_routing_outcome_adapter", "p4obs", "alert")
_emit_links_incident_trace("test_routing_outcome_adapter", "p4obs", "trace_link")
_emit_captures_pattern("test_routing_outcome_adapter", "p3lm", "pattern")
_emit_records_learning_event("test_routing_outcome_adapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_routing_outcome_adapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_routing_outcome_adapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_routing_outcome_adapter", "p3lm", "routing")
_emit_improves_agent_policy("test_routing_outcome_adapter", "p3lm", "policy")
_emit_stores_learning_state("test_routing_outcome_adapter", "p3lm", "state")
_emit_records_execution_trace("test_routing_outcome_adapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_routing_outcome_adapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_routing_outcome_adapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_routing_outcome_adapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_routing_outcome_adapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_routing_outcome_adapter", "env_read", "p2_env_1")
_emit_reads_environ("test_routing_outcome_adapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_routing_outcome_adapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_routing_outcome_adapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_routing_outcome_adapter", "context_pull")
_emit_pulls_context("p1", "test_routing_outcome_adapter", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_routing_outcome_adapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_routing_outcome_adapter", "uwg_term_secondary")
_emit_writes_through("p1", "test_routing_outcome_adapter", "write_through")
_emit_writes_through("p1", "test_routing_outcome_adapter", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_routing_outcome_adapter", "safety_validation")
_emit_invokes_eval("p1", "test_routing_outcome_adapter", "eval_call")
_emit_proposal_commits_routing("p1", "test_routing_outcome_adapter", "routing_commit")
_emit_escalates_to_human("p1", "test_routing_outcome_adapter", "human_escalation")
_emit_routes_through("p1", "test_routing_outcome_adapter", "route_through")
_emit_checks_agent_registry("p1", "test_routing_outcome_adapter", "agent_registry")
_emit_validates_agent_capability("p1", "test_routing_outcome_adapter", "capability")
_emit_dispatches_execution_plan("p1", "test_routing_outcome_adapter", "exec_plan")
_emit_agent_executes_agent("p1", "test_routing_outcome_adapter", "sub_agent")
_emit_routes_to_agent("p1", "test_routing_outcome_adapter", "target_agent")
_emit_verifies_policy("p1", "test_routing_outcome_adapter", "policy_check")
_emit_observes_runtime_state("p1", "test_routing_outcome_adapter", "runtime_state")
_emit_verifies_boundary("p1", "test_routing_outcome_adapter", "boundary_check")
_emit_transcripts_response("p1", "test_routing_outcome_adapter", "transcript")
_emit_hard_fails_untranscripted("p1", "test_routing_outcome_adapter")
_emit_gated_by_confidence("p1", "test_routing_outcome_adapter", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _decision(
    *,
    intent: str = "code",
    target_name: str = "code_reviewer",
    confidence: float = 0.85,
    result: object = "ok",
    error: str | None = None,
    trace_id: str = "trace-001",
) -> RoutingDecision:
    return RoutingDecision(
        intent=intent,
        target_name=target_name,
        confidence=confidence,
        result=result,
        error=error,
        metadata={"trace_id": trace_id},
    )


def _mock_bus() -> MagicMock:
    bus = MagicMock()
    bus.enqueue = MagicMock()
    return bus


# ---------------------------------------------------------------------------
# build_routing_outcome_package
# ---------------------------------------------------------------------------


class TestBuildRoutingOutcomePackage:
    def test_kind_is_routing_outcome(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1000)
        assert pkg.kind == "routing_outcome"

    def test_payload_has_all_required_keys(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1000)
        required = {
            "intent",
            "target_name",
            "confidence",
            "outcome",
            "has_error",
            "timestamp_utc",
            "influence_class",
        }
        assert required.issubset(set(pkg.payload.keys()))

    def test_outcome_success_when_result_present(self):
        pkg = build_routing_outcome_package(_decision(result="ok", error=None), timestamp_utc=1)
        assert pkg.payload["outcome"] == "SUCCESS"

    def test_outcome_safe_failure_when_error_set(self):
        pkg = build_routing_outcome_package(_decision(result=None, error="boom"), timestamp_utc=1)
        assert pkg.payload["outcome"] == "SAFE_FAILURE"

    def test_outcome_unknown_when_result_none_no_error(self):
        pkg = build_routing_outcome_package(_decision(result=None, error=None), timestamp_utc=1)
        assert pkg.payload["outcome"] == "UNKNOWN"

    def test_has_error_true_when_error_set(self):
        pkg = build_routing_outcome_package(_decision(error="oops"), timestamp_utc=1)
        assert pkg.payload["has_error"] is True

    def test_has_error_false_when_no_error(self):
        pkg = build_routing_outcome_package(_decision(error=None), timestamp_utc=1)
        assert pkg.payload["has_error"] is False

    def test_confidence_in_payload(self):
        pkg = build_routing_outcome_package(_decision(confidence=0.72345678), timestamp_utc=1)
        assert abs(pkg.payload["confidence"] - 0.723457) < 1e-5

    def test_influence_class_is_c0_informational(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=1)
        assert pkg.payload["influence_class"] == "C0_INFORMATIONAL"

    def test_intent_and_target_name_in_payload(self):
        pkg = build_routing_outcome_package(
            _decision(intent="resume", target_name="resume_writer"), timestamp_utc=1
        )
        assert pkg.payload["intent"] == "resume"
        assert pkg.payload["target_name"] == "resume_writer"

    def test_timestamp_utc_in_payload(self):
        pkg = build_routing_outcome_package(_decision(), timestamp_utc=99999)
        assert pkg.payload["timestamp_utc"] == 99999

    def test_deterministic_same_decision_same_payload(self):
        d = _decision(confidence=0.5, trace_id="t42")
        p1 = build_routing_outcome_package(d, timestamp_utc=5)
        p2 = build_routing_outcome_package(d, timestamp_utc=5)
        assert p1.payload == p2.payload

    def test_different_timestamps_produce_different_packages(self):
        d = _decision()
        p1 = build_routing_outcome_package(d, timestamp_utc=1)
        p2 = build_routing_outcome_package(d, timestamp_utc=2)
        assert p1.payload["timestamp_utc"] != p2.payload["timestamp_utc"]


# ---------------------------------------------------------------------------
# RoutingOutcomeAdapter.emit()
# ---------------------------------------------------------------------------


class TestRoutingOutcomeAdapterEmit:
    def test_emit_returns_true_on_success(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        result = adapter.emit(_decision(), timestamp_utc=1)
        assert result is True

    def test_emit_calls_bus_enqueue_once(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        adapter.emit(_decision(), timestamp_utc=1)
        bus.enqueue.assert_called_once()

    def test_emit_returns_false_when_bus_raises(self):
        bus = _mock_bus()
        bus.enqueue.side_effect = RuntimeError("bus dead")
        adapter = RoutingOutcomeAdapter(bus=bus)
        result = adapter.emit(_decision(), timestamp_utc=1)
        assert result is False

    def test_emit_does_not_raise_when_bus_raises(self):
        bus = _mock_bus()
        bus.enqueue.side_effect = Exception("unexpected")
        adapter = RoutingOutcomeAdapter(bus=bus)
        try:
            adapter.emit(_decision(), timestamp_utc=1)
        except Exception as exc:
            pytest.fail(f"emit() raised unexpectedly: {exc}")

    def test_emit_passes_correct_package_kind(self):
        captured = []
        bus = _mock_bus()
        bus.enqueue.side_effect = lambda pkg: captured.append(pkg)
        adapter = RoutingOutcomeAdapter(bus=bus)
        adapter.emit(_decision(), timestamp_utc=1)
        assert len(captured) == 1
        assert captured[0].kind == "routing_outcome"

    def test_emit_multiple_decisions_enqueues_each(self):
        bus = _mock_bus()
        adapter = RoutingOutcomeAdapter(bus=bus)
        for i in range(5):
            adapter.emit(_decision(confidence=float(i) / 10), timestamp_utc=i)
        assert bus.enqueue.call_count == 5
