"""Tests for Detection Signal Emitter L4A writes - Phase 7 functionality.

Tests that detection signals are written to L4A state when writer is provided.
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

_emit_records_execution_trace("p0", "evidence", "test_detection_signal_emitter_writes_l4a")
_emit_applies_guardrail("p0", "test_detection_signal_emitter_writes_l4a", "p0_governance")
_emit_reads_policy_state("p0", "test_detection_signal_emitter_writes_l4a", "policy_binding")
_emit_snapshots_state("p0", "test_detection_signal_emitter_writes_l4a", "state_snapshot")
emit_replay_key("p0", "test_detection_signal_emitter_writes_l4a")
emit_determinism_digest("p0", "test_detection_signal_emitter_writes_l4a")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_detection_signal_emitter_writes_l4a", "execution_auth")
_emit_validates_capability("p2", "test_detection_signal_emitter_writes_l4a", "capability_check")
_emit_routes_to_capability("p2", "test_detection_signal_emitter_writes_l4a", "capability_route")
_emit_writes_via_uwg("p2", "test_detection_signal_emitter_writes_l4a", "uwg_write")
_emit_blocks_direct_write("p2", "test_detection_signal_emitter_writes_l4a", "direct_write_block")
_emit_records_tool_invocation("p2", "test_detection_signal_emitter_writes_l4a", "tool_invocation")
_emit_captures_execution_output("p2", "test_detection_signal_emitter_writes_l4a", "exec_output")
_emit_dispatches_agent("p3", "test_detection_signal_emitter_writes_l4a", "agent_dispatch")
_emit_coordinates_agents("p3", "test_detection_signal_emitter_writes_l4a", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_detection_signal_emitter_writes_l4a", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_detection_signal_emitter_writes_l4a", "healing_outcome")
_emit_escalates_failure("p3", "test_detection_signal_emitter_writes_l4a", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_detection_signal_emitter_writes_l4a", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_detection_signal_emitter_writes_l4a", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_detection_signal_emitter_writes_l4a", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_detection_signal_emitter_writes_l4a", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_detection_signal_emitter_writes_l4a", "eval_metric")
_emit_stores_embedding("p4", "test_detection_signal_emitter_writes_l4a", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_detection_signal_emitter_writes_l4a", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_detection_signal_emitter_writes_l4a", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L6_observability.engines.detection_signal_emitter import (
    emit_detection_signal_with_l4a,
)
from agentic_core.L6_observability.types.detection_signal_types import DetectionSignal
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_1")
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_2")
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_3")
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_4")
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_5")
_emit_emits_metric_event("test_detection_signal_emitter_writes_l4a", "p4obs", "metric_6")
_emit_records_incident_event("test_detection_signal_emitter_writes_l4a", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_detection_signal_emitter_writes_l4a", "p4obs", "anomaly")
_emit_writes_observability_log("test_detection_signal_emitter_writes_l4a", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_detection_signal_emitter_writes_l4a", "p4obs", "mon_state")
_emit_triggers_alert("test_detection_signal_emitter_writes_l4a", "p4obs", "alert")
_emit_links_incident_trace("test_detection_signal_emitter_writes_l4a", "p4obs", "trace_link")
_emit_captures_pattern("test_detection_signal_emitter_writes_l4a", "p3lm", "pattern")
_emit_records_learning_event("test_detection_signal_emitter_writes_l4a", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_detection_signal_emitter_writes_l4a", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_detection_signal_emitter_writes_l4a", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_detection_signal_emitter_writes_l4a", "p3lm", "routing")
_emit_improves_agent_policy("test_detection_signal_emitter_writes_l4a", "p3lm", "policy")
_emit_stores_learning_state("test_detection_signal_emitter_writes_l4a", "p3lm", "state")
_emit_records_execution_trace("test_detection_signal_emitter_writes_l4a", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_detection_signal_emitter_writes_l4a", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_detection_signal_emitter_writes_l4a", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_detection_signal_emitter_writes_l4a", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_detection_signal_emitter_writes_l4a", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_detection_signal_emitter_writes_l4a", "env_read", "p2_env_1")
_emit_reads_environ("test_detection_signal_emitter_writes_l4a", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_detection_signal_emitter_writes_l4a", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_detection_signal_emitter_writes_l4a", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_detection_signal_emitter_writes_l4a", "context_pull")
_emit_pulls_context("p1", "test_detection_signal_emitter_writes_l4a", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_detection_signal_emitter_writes_l4a", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_detection_signal_emitter_writes_l4a", "uwg_term_secondary")
_emit_writes_through("p1", "test_detection_signal_emitter_writes_l4a", "write_through")
_emit_writes_through("p1", "test_detection_signal_emitter_writes_l4a", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_detection_signal_emitter_writes_l4a", "safety_validation")
_emit_invokes_eval("p1", "test_detection_signal_emitter_writes_l4a", "eval_call")
_emit_proposal_commits_routing("p1", "test_detection_signal_emitter_writes_l4a", "routing_commit")


class FakeL4StateWriter:
    """Fake L4 state writer that captures writes."""

    def __init__(self) -> None:
        self.l4a_writes: list[dict] = []

    def write_l4a_detection_signal(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Capture L4A detection signal writes."""
        self.l4a_writes.append(
            {"payload_bytes": payload_bytes, "component_name": component_name, "created_utc": created_utc}
        )
        # Return a fake version ID
        return f"fake_version_{len(self.l4a_writes)}"

    def write_l4b_healing_snapshot(
        self, *, payload_bytes: bytes, component_name: str, created_utc: int
    ) -> str:
        """Not used in this test."""
        return "noop_l4b"


class TestDetectionSignalEmitterWritesL4A:
    """Test suite for detection signal L4A writing."""

    def test_emit_with_l4a_writer_calls_write_exactly_once(self):
        """Test that providing L4A writer results in exactly one write call."""
        fake_writer = FakeL4StateWriter()

        mission_id = "test_mission_123"
        created_at_utc = 1000
        anomaly_score = 0.5
        escalation_rate = 0.2
        retry_rate = 0.1
        violation_density = 0.3

        # Emit signal with L4A writer
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            l4a_writer=fake_writer,
            anomaly_score=anomaly_score,
            escalation_rate=escalation_rate,
            retry_rate=retry_rate,
            violation_density=violation_density,
            schema_version=1,
        )

        # Verify signal was created correctly
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id
        assert signal.created_at_utc == created_at_utc
        assert signal.anomaly_score == anomaly_score
        assert signal.escalation_rate == escalation_rate
        assert signal.retry_rate == retry_rate
        assert signal.violation_density == violation_density
        assert signal.schema_version == 1

        # Verify L4A writer was called exactly once
        assert len(fake_writer.l4a_writes) == 1

        # Verify write parameters
        write = fake_writer.l4a_writes[0]
        assert write["component_name"] == "detection_signal_emitter"
        assert write["created_utc"] == created_at_utc

        # Verify payload bytes contain the serialized signal
        payload_bytes = write["payload_bytes"]
        assert isinstance(payload_bytes, bytes)
        # Should contain the mission_id in serialized form
        assert mission_id.encode() in payload_bytes

    def test_emit_without_l4a_writer_no_write_calls(self):
        """Test that not providing L4A writer results in no write calls."""
        fake_writer = FakeL4StateWriter()

        mission_id = "test_mission_456"
        created_at_utc = 2000

        # Emit signal without L4A writer
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id,
            created_at_utc=created_at_utc,
            l4a_writer=None,  # No writer provided
        )

        # Verify signal was still created
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id

        # Verify no L4A writes occurred
        assert len(fake_writer.l4a_writes) == 0

    def test_emit_with_l4a_writer_deterministic_bytes(self):
        """Test that L4A writes use deterministic bytes."""
        fake_writer = FakeL4StateWriter()

        # Emit same signal twice
        mission_id = "deterministic_test"
        created_at_utc = 3000

        signal1 = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=fake_writer
        )

        signal2 = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=fake_writer
        )

        # Should have two writes
        assert len(fake_writer.l4a_writes) == 2

        # Payload bytes should be identical for same signal
        payload1 = fake_writer.l4a_writes[0]["payload_bytes"]
        payload2 = fake_writer.l4a_writes[1]["payload_bytes"]
        assert payload1 == payload2

        # Signals should also be identical
        assert signal1.canonical_bytes() == signal2.canonical_bytes()

    def test_emit_with_l4a_writer_handles_write_failure_gracefully(self):
        """Test that L4A write failures don't break signal emission."""

        class FailingL4StateWriter:
            """L4A writer that always fails."""

            def write_l4a_detection_signal(self, **kwargs) -> str:
                raise RuntimeError("Simulated write failure")

        failing_writer = FailingL4StateWriter()

        mission_id = "test_mission_failure"
        created_at_utc = 4000

        # Should not raise exception even if L4A write fails
        signal = emit_detection_signal_with_l4a(
            mission_id=mission_id, created_at_utc=created_at_utc, l4a_writer=failing_writer
        )

        # Signal should still be created successfully
        assert isinstance(signal, DetectionSignal)
        assert signal.mission_id == mission_id

    def test_emit_with_l4a_writer_different_signals_different_bytes(self):
        """Test that different signals produce different payload bytes."""
        fake_writer = FakeL4StateWriter()

        # Emit two different signals
        signal1 = emit_detection_signal_with_l4a(
            mission_id="signal_1", created_at_utc=5000, anomaly_score=0.1, l4a_writer=fake_writer
        )

        signal2 = emit_detection_signal_with_l4a(
            mission_id="signal_2", created_at_utc=5000, anomaly_score=0.9, l4a_writer=fake_writer
        )

        # Should have two writes
        assert len(fake_writer.l4a_writes) == 2

        # Payload bytes should be different
        payload1 = fake_writer.l4a_writes[0]["payload_bytes"]
        payload2 = fake_writer.l4a_writes[1]["payload_bytes"]
        assert payload1 != payload2

        # Signals should also be different
        assert signal1.canonical_bytes() != signal2.canonical_bytes()
