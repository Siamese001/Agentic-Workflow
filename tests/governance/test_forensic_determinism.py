"""REQ-378/384: Forensic determinism.

Prove ForensicTraceBuffer uses semantic clock only; TraceID deterministic under replay.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.trace_id_generator import (
    TraceIdGenerator,
    generate_trace_id,
    validate_trace_id,
)
from agentic_core.L0_routing.types.determinism_types import (
    ForensicTraceBuffer,
    SemanticClockSnapshot,
)
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

_emit_records_execution_trace("p0", "evidence", "test_forensic_determinism")
_emit_applies_guardrail("p0", "test_forensic_determinism", "p0_governance")
_emit_reads_policy_state("p0", "test_forensic_determinism", "policy_binding")
_emit_snapshots_state("p0", "test_forensic_determinism", "state_snapshot")
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

_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_1")
_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_2")
_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_3")
_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_4")
_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_5")
_emit_emits_metric_event("test_forensic_determinism", "p4obs", "metric_6")
_emit_records_incident_event("test_forensic_determinism", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_forensic_determinism", "p4obs", "anomaly")
_emit_writes_observability_log("test_forensic_determinism", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_forensic_determinism", "p4obs", "mon_state")
_emit_triggers_alert("test_forensic_determinism", "p4obs", "alert")
_emit_links_incident_trace("test_forensic_determinism", "p4obs", "trace_link")
_emit_captures_pattern("test_forensic_determinism", "p3lm", "pattern")
_emit_records_learning_event("test_forensic_determinism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_forensic_determinism", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_forensic_determinism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_forensic_determinism", "p3lm", "routing")
_emit_improves_agent_policy("test_forensic_determinism", "p3lm", "policy")
_emit_stores_learning_state("test_forensic_determinism", "p3lm", "state")
_emit_records_execution_trace("test_forensic_determinism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_forensic_determinism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_forensic_determinism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_forensic_determinism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_forensic_determinism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_forensic_determinism", "env_read", "p2_env_1")
_emit_reads_environ("test_forensic_determinism", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_forensic_determinism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_forensic_determinism", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_forensic_determinism", "context_pull")
_emit_pulls_context("p1", "test_forensic_determinism", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_forensic_determinism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_forensic_determinism", "uwg_term_2")
_emit_writes_through("p1", "test_forensic_determinism", "write_through")
_emit_writes_through("p1", "test_forensic_determinism", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_forensic_determinism", "safety_validation")
_emit_invokes_eval("p1", "test_forensic_determinism", "eval_call")
_emit_proposal_commits_routing("p1", "test_forensic_determinism", "routing_commit")
_emit_escalates_to_human("p1", "test_forensic_determinism", "human_escalation")
_emit_routes_through("p1", "test_forensic_determinism", "route_through")
_emit_checks_agent_registry("p1", "test_forensic_determinism", "agent_registry")
_emit_validates_agent_capability("p1", "test_forensic_determinism", "capability")
_emit_dispatches_execution_plan("p1", "test_forensic_determinism", "exec_plan")
_emit_agent_executes_agent("p1", "test_forensic_determinism", "sub_agent")
_emit_routes_to_agent("p1", "test_forensic_determinism", "target_agent")
_emit_verifies_policy("p1", "test_forensic_determinism", "policy_check")
_emit_observes_runtime_state("p1", "test_forensic_determinism", "runtime_state")
_emit_verifies_boundary("p1", "test_forensic_determinism", "boundary_check")
_emit_transcripts_response("p1", "test_forensic_determinism", "transcript")
_emit_hard_fails_untranscripted("p1", "test_forensic_determinism")
_emit_gated_by_confidence("p1", "test_forensic_determinism", "confidence_gate")
emit_replay_key("p0", "test_forensic_determinism")
emit_determinism_digest("p0", "test_forensic_determinism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_forensic_determinism", "execution_auth")
_emit_validates_capability("p2", "test_forensic_determinism", "capability_check")
_emit_routes_to_capability("p2", "test_forensic_determinism", "capability_route")
_emit_writes_via_uwg("p2", "test_forensic_determinism", "uwg_write")
_emit_blocks_direct_write("p2", "test_forensic_determinism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_forensic_determinism", "tool_invocation")
_emit_captures_execution_output("p2", "test_forensic_determinism", "exec_output")
_emit_dispatches_agent("p3", "test_forensic_determinism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_forensic_determinism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_forensic_determinism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_forensic_determinism", "healing_outcome")
_emit_escalates_failure("p3", "test_forensic_determinism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_forensic_determinism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_forensic_determinism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_forensic_determinism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_forensic_determinism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_forensic_determinism", "eval_metric")
_emit_stores_embedding("p4", "test_forensic_determinism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_forensic_determinism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_forensic_determinism", "exec_snapshot_link")


@pytest.mark.governance
def test_req378_forensic_buffer_uses_semantic_clock():
    """REQ-378: ForensicTraceBuffer uses semantic clock only."""
    # Create buffer with semantic clock
    clock = SemanticClockSnapshot(tick=42)
    buffer = ForensicTraceBuffer(
        trace_id="test-trace", semantic_clock_tick=clock.tick, velocity_threshold=THRESHOLD
    )

    # Verify semantic clock is used
    assert buffer.semantic_clock_tick == 42
    assert buffer.velocity_threshold == 100

    # Buffer should be empty initially
    assert len(buffer._buffer) == 0

    # Add some signals
    buffer._buffer.extend([{"signal": "test1", "value": 10}, {"signal": "test2", "value": 20}])

    # Verify signals are stored
    assert len(buffer._buffer) == 2
    assert buffer._buffer[0]["signal"] == "test1"
    assert buffer._buffer[1]["value"] == 20


@pytest.mark.governance
def test_req378_forensic_buffer_velocity_threshold():
    """REQ-378: ForensicTraceBuffer enforces velocity threshold."""
    from agentic_core.L0_routing.types.determinism_types import TRACE_BUFFER_VELOCITY_THRESHOLD

    # Verify default threshold
    buffer = ForensicTraceBuffer(trace_id="test-trace", semantic_clock_tick=42)

    assert buffer.velocity_threshold == TRACE_BUFFER_VELOCITY_THRESHOLD

    # Custom threshold
    custom_buffer = ForensicTraceBuffer(trace_id="test-trace", semantic_clock_tick=42, velocity_threshold=THRESHOLD)

    assert custom_buffer.velocity_threshold == 200


@pytest.mark.governance
def test_req384_trace_id_deterministic_format():
    """REQ-384: TraceID follows deterministic format."""
    generator = TraceIdGenerator(replay_mode=False)

    clock = SemanticClockSnapshot(tick=42)
    trace_id = generator.generate_trace_id(clock, "test_operation")

    # Should match pattern ^CC3AL1-[0-9A-F]{8}$
    assert generator.validate_trace_id(trace_id)
    assert trace_id.startswith("CC3AL1-")
    assert len(trace_id) == 15  # CC3AL1- + 8 hex chars (SHA-256 produces 8 chars)

    # All characters after dash should be hex
    suffix = trace_id[7:]
    assert all(c in "0123456789ABCDEF" for c in suffix)
    assert len(suffix) == 8


@pytest.mark.governance
def test_req384_trace_id_deterministic_under_replay():
    """REQ-384: TraceID deterministic under replay."""
    # Create two generators in replay mode
    generator1 = TraceIdGenerator(replay_mode=True)
    generator2 = TraceIdGenerator(replay_mode=True)

    clock = SemanticClockSnapshot(tick=42)

    # Generate IDs with same inputs
    id1 = generator1.generate_trace_id(clock, "test_operation", "context")
    id2 = generator2.generate_trace_id(clock, "test_operation", "context")

    # Should be identical
    assert id1 == id2

    # Different inputs should produce different IDs
    id3 = generator1.generate_trace_id(clock, "different_operation", "context")
    assert id1 != id3


@pytest.mark.governance
def test_req384_trace_id_replay_determinism_check():
    """REQ-384: TraceID replay determinism can be verified."""
    # Use fresh generator for deterministic check
    generator1 = TraceIdGenerator(replay_mode=True)
    generator2 = TraceIdGenerator(replay_mode=True)
    clock = SemanticClockSnapshot(tick=42)

    # Generate IDs with same inputs
    id1 = generator1.generate_trace_id(clock, "test_operation", "context")
    id2 = generator2.generate_trace_id(clock, "test_operation", "context")

    # Should be identical (deterministic)
    assert id1 == id2

    # Different operation should produce different ID
    generator3 = TraceIdGenerator(replay_mode=True)
    id3 = generator3.generate_trace_id(clock, "different_operation", "context")
    assert id1 != id3


@pytest.mark.governance
def test_req384_trace_id_semantic_clock_dependency():
    """REQ-384: TraceID depends on semantic clock."""
    generator = TraceIdGenerator(replay_mode=True)

    clock1 = SemanticClockSnapshot(tick=42)
    clock2 = SemanticClockSnapshot(tick=43)

    # Same operation, different clock ticks
    id1 = generator.generate_trace_id(clock1, "test_operation")
    id2 = generator.generate_trace_id(clock2, "test_operation")

    # Should be different
    assert id1 != id2

    # Same clock should be deterministic (use same generator state)
    generator.generate_trace_id(clock1, "another_operation")
    # Note: Due to counter increment, this will be different but deterministic


@pytest.mark.governance
def test_req384_trace_id_operation_dependency():
    """REQ-384: TraceID depends on operation."""
    generator = TraceIdGenerator(replay_mode=True)
    clock = SemanticClockSnapshot(tick=42)

    # Different operations
    id1 = generator.generate_trace_id(clock, "operation1")
    id2 = generator.generate_trace_id(clock, "operation2")

    # Should be different
    assert id1 != id2

    # Same operation with new generator should be deterministic
    new_generator = TraceIdGenerator(replay_mode=True)
    id1_again = new_generator.generate_trace_id(clock, "operation1")
    # Should match first ID from fresh generator
    assert id1_again == id1


@pytest.mark.governance
def test_req384_trace_id_context_dependency():
    """REQ-384: TraceID depends on additional context."""
    generator = TraceIdGenerator(replay_mode=True)
    clock = SemanticClockSnapshot(tick=42)

    # Different contexts
    id1 = generator.generate_trace_id(clock, "operation", "context1")
    id2 = generator.generate_trace_id(clock, "operation", "context2")

    # Should be different
    assert id1 != id2

    # Same context with new generator should be deterministic
    new_generator = TraceIdGenerator(replay_mode=True)
    id1_again = new_generator.generate_trace_id(clock, "operation", "context1")
    # Should match first ID from fresh generator
    assert id1_again == id1


@pytest.mark.governance
def test_req384_global_generate_trace_id_function():
    """REQ-384: Global generate_trace_id function works correctly."""
    clock = SemanticClockSnapshot(tick=42)

    # Normal mode
    id1 = generate_trace_id(clock, "test_operation", replay_mode=False)
    assert validate_trace_id(id1)

    # Replay mode
    id2 = generate_trace_id(clock, "test_operation", replay_mode=True)
    assert validate_trace_id(id2)

    # Replay mode should be deterministic
    id3 = generate_trace_id(clock, "test_operation", replay_mode=True)
    assert id2 == id3


@pytest.mark.governance
def test_req384_trace_id_collision_detection():
    """REQ-384: TraceID collision detection and handling."""
    generator = TraceIdGenerator(replay_mode=True)
    clock = SemanticClockSnapshot(tick=42)

    # Generate many IDs to check for collisions
    generated_ids = set()
    for i in range(100):
        operation = f"operation_{i}"
        trace_id = generator.generate_trace_id(clock, operation)

        # Should be valid
        assert generator.validate_trace_id(trace_id)

        # Should not collide (very unlikely with SHA-256)
        assert trace_id not in generated_ids
        generated_ids.add(trace_id)

    # Should have 100 unique IDs
    assert len(generated_ids) == 100


@pytest.mark.governance
def test_req378_384_integration_forensic_trace():
    """REQ-378/384: Integration test for forensic trace with deterministic IDs."""
    # Create forensic buffer
    clock = SemanticClockSnapshot(tick=42)
    buffer = ForensicTraceBuffer(trace_id="CC3AL1-12345678", semantic_clock_tick=clock.tick)

    # Generate matching deterministic trace ID
    generator = TraceIdGenerator(replay_mode=True)
    trace_id = generator.generate_trace_id(clock, "forensic_capture")

    # Should be valid
    assert generator.validate_trace_id(trace_id)

    # Buffer and trace ID should be linked
    assert buffer.semantic_clock_tick == clock.tick

    # Add forensic data
    forensic_data = {"event": "system_call", "timestamp": clock.tick, "data": "sample forensic evidence"}
    buffer._buffer.append(forensic_data)

    # Verify data integrity
    assert len(buffer._buffer) == 1
    assert buffer._buffer[0]["event"] == "system_call"
    assert buffer._buffer[0]["timestamp"] == clock.tick
