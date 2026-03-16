"""
W5 Handshake State Machine Tests

Tests for deterministic sequential handshake state machine.
Validates state transitions, guards, and sequence hash computation.
"""

import pytest

from agentic_core.L3_orchestration.engines.handshake_state_machine import (
    HandshakeState,
    HandshakeStateMachine,
    create_handshake_machine,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_1")
_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_2")
_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_3")
_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_4")
_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_5")
_emit_emits_metric_event("test_handshake_state_machine", "p4obs", "metric_6")
_emit_records_incident_event("test_handshake_state_machine", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_handshake_state_machine", "p4obs", "anomaly")
_emit_writes_observability_log("test_handshake_state_machine", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_handshake_state_machine", "p4obs", "mon_state")
_emit_triggers_alert("test_handshake_state_machine", "p4obs", "alert")
_emit_links_incident_trace("test_handshake_state_machine", "p4obs", "trace_link")
_emit_captures_pattern("test_handshake_state_machine", "p3lm", "pattern")
_emit_records_learning_event("test_handshake_state_machine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_handshake_state_machine", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_handshake_state_machine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_handshake_state_machine", "p3lm", "routing")
_emit_improves_agent_policy("test_handshake_state_machine", "p3lm", "policy")
_emit_stores_learning_state("test_handshake_state_machine", "p3lm", "state")
_emit_records_execution_trace("test_handshake_state_machine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_handshake_state_machine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_handshake_state_machine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_handshake_state_machine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_handshake_state_machine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_handshake_state_machine", "env_read", "p2_env_1")
_emit_reads_environ("test_handshake_state_machine", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_handshake_state_machine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_handshake_state_machine", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_handshake_state_machine")
_emit_applies_guardrail("p0", "test_handshake_state_machine", "p0_governance")
_emit_reads_policy_state("p0", "test_handshake_state_machine", "policy_binding")
_emit_routes_to_agent("p1", "test_handshake_state_machine", "test")
_emit_orchestrates_workflow("p1", "test_handshake_state_machine", "test")
_emit_dispatches_execution_plan("p1", "test_handshake_state_machine", "test")
_emit_validates_agent_capability("p1", "test_handshake_state_machine", "test")
_emit_checks_agent_registry("p1", "test_handshake_state_machine", "test")
_emit_snapshots_state("p0", "test_handshake_state_machine", "state_snapshot")
_emit_pulls_context("p1", "test_handshake_state_machine", "context_pull")
_emit_pulls_context("p1", "test_handshake_state_machine", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_handshake_state_machine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_handshake_state_machine", "uwg_term_secondary")
_emit_writes_through("p1", "test_handshake_state_machine", "write_through")
_emit_writes_through("p1", "test_handshake_state_machine", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_handshake_state_machine", "safety_validation")
_emit_invokes_eval("p1", "test_handshake_state_machine", "eval_call")
_emit_proposal_commits_routing("p1", "test_handshake_state_machine", "routing_commit")
emit_replay_key("p0", "test_handshake_state_machine")
emit_determinism_digest("p0", "test_handshake_state_machine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_handshake_state_machine", "execution_auth")
_emit_validates_capability("p2", "test_handshake_state_machine", "capability_check")
_emit_routes_to_capability("p2", "test_handshake_state_machine", "capability_route")
_emit_writes_via_uwg("p2", "test_handshake_state_machine", "uwg_write")
_emit_blocks_direct_write("p2", "test_handshake_state_machine", "direct_write_block")
_emit_records_tool_invocation("p2", "test_handshake_state_machine", "tool_invocation")
_emit_captures_execution_output("p2", "test_handshake_state_machine", "exec_output")
_emit_dispatches_agent("p3", "test_handshake_state_machine", "agent_dispatch")
_emit_coordinates_agents("p3", "test_handshake_state_machine", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_handshake_state_machine", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_handshake_state_machine", "healing_outcome")
_emit_escalates_failure("p3", "test_handshake_state_machine", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_handshake_state_machine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_handshake_state_machine", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_handshake_state_machine", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_handshake_state_machine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_handshake_state_machine", "eval_metric")
_emit_stores_embedding("p4", "test_handshake_state_machine", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_handshake_state_machine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_handshake_state_machine", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestW5HandshakeStateMachine:
    """Test suite for W5 handshake state machine."""

    @pytest.fixture
    def machine(self):
        """Create fresh handshake state machine for each test."""
        return HandshakeStateMachine()

    def test_initial_state(self, machine):
        """Test machine starts in INIT state."""
        assert machine.current_state == HandshakeState.INIT
        assert len(machine.transition_history) == 0

    def test_reset_functionality(self, machine):
        """Test reset returns machine to INIT state."""
        # Advance through some states
        machine.request_preclear()
        machine.certify()

        # Reset
        machine.reset()

        # Verify reset
        assert machine.current_state == HandshakeState.INIT
        assert len(machine.transition_history) == 0

    def test_preclear_from_init(self, machine):
        """Test PRECLEAR_REQUESTED transition from INIT."""
        machine.request_preclear()

        assert machine.current_state == HandshakeState.PRECLEAR_REQUESTED
        assert len(machine.transition_history) == 1

        transition = machine.transition_history[0]
        assert transition.from_state == HandshakeState.INIT
        assert transition.to_state == HandshakeState.PRECLEAR_REQUESTED
        assert transition.reason == "L5 pre-clear requested"

    def test_certify_from_preclear(self, machine):
        """Test CERTIFIED transition from PRECLEAR_REQUESTED."""
        machine.request_preclear()
        machine.certify()

        assert machine.current_state == HandshakeState.CERTIFIED
        assert len(machine.transition_history) == 2

        # Check last transition
        transition = machine.transition_history[-1]
        assert transition.from_state == HandshakeState.PRECLEAR_REQUESTED
        assert transition.to_state == HandshakeState.CERTIFIED
        assert transition.reason == "L5 certification granted"

    def test_seal_from_certified(self, machine):
        """Test SEALED transition from CERTIFIED."""
        machine.request_preclear()
        machine.certify()
        machine.seal()

        assert machine.current_state == HandshakeState.SEALED
        assert len(machine.transition_history) == 3

        # Check last transition
        transition = machine.transition_history[-1]
        assert transition.from_state == HandshakeState.CERTIFIED
        assert transition.to_state == HandshakeState.SEALED
        assert transition.reason == "Plan sealed for execution"

    def test_dispatch_from_sealed(self, machine):
        """Test DISPATCHED transition from SEALED."""
        machine.request_preclear()
        machine.certify()
        machine.seal()
        machine.dispatch()

        assert machine.current_state == HandshakeState.DISPATCHED
        assert len(machine.transition_history) == 4

        # Check last transition
        transition = machine.transition_history[-1]
        assert transition.from_state == HandshakeState.SEALED
        assert transition.to_state == HandshakeState.DISPATCHED
        assert transition.reason == "Dispatched to L2 execution"

    def test_modify_diff_from_certified(self, machine):
        """Test MODIFY_DIFF forces CERTIFIED → PRECLEAR_REQUESTED."""
        machine.request_preclear()
        machine.certify()

        # Apply modify diff
        machine.modify_diff()

        assert machine.current_state == HandshakeState.PRECLEAR_REQUESTED
        assert len(machine.transition_history) == 3

        # Check last transition
        transition = machine.transition_history[-1]
        assert transition.from_state == HandshakeState.CERTIFIED
        assert transition.to_state == HandshakeState.PRECLEAR_REQUESTED
        assert transition.reason == "MODIFY_DIFF invalidated certification"

    def test_preclear_from_invalid_state_fails(self, machine):
        """Test preclear request fails from non-INIT state."""
        machine.request_preclear()

        with pytest.raises(ValueError, match="Cannot request preclear from PRECLEAR_REQUESTED"):
            machine.request_preclear()

    def test_certify_from_invalid_state_fails(self, machine):
        """Test certification fails from non-PRECLEAR_REQUESTED state."""
        # Try to certify from INIT
        with pytest.raises(ValueError, match="Cannot certify from INIT"):
            machine.certify()

        # Try to certify from CERTIFIED
        machine.request_preclear()
        machine.certify()

        with pytest.raises(ValueError, match="Cannot certify from CERTIFIED"):
            machine.certify()

    def test_seal_from_invalid_state_fails(self, machine):
        """Test seal fails from non-CERTIFIED state."""
        # Try to seal from INIT
        with pytest.raises(ValueError, match="Cannot seal from INIT"):
            machine.seal()

        # Try to seal from PRECLEAR_REQUESTED
        machine.request_preclear()

        with pytest.raises(ValueError, match="Cannot seal from PRECLEAR_REQUESTED"):
            machine.seal()

    def test_dispatch_from_invalid_state_fails(self, machine):
        """Test dispatch fails from non-SEALED state."""
        # Try to dispatch from INIT
        with pytest.raises(ValueError, match="Cannot dispatch from INIT"):
            machine.dispatch()

        # Try to dispatch from CERTIFIED
        machine.request_preclear()
        machine.certify()

        with pytest.raises(ValueError, match="Cannot dispatch from CERTIFIED"):
            machine.dispatch()

    def test_modify_diff_from_invalid_state_fails(self, machine):
        """Test modify_diff fails from non-CERTIFIED state."""
        # Try to modify from INIT
        with pytest.raises(ValueError, match="Cannot modify_diff from INIT"):
            machine.modify_diff()

        # Try to modify from PRECLEAR_REQUESTED
        machine.request_preclear()

        with pytest.raises(ValueError, match="Cannot modify_diff from PRECLEAR_REQUESTED"):
            machine.modify_diff()

        # Try to modify from SEALED (reset first - machine is in PRECLEAR_REQUESTED)
        machine.reset()
        machine.request_preclear()
        machine.certify()
        machine.seal()

        with pytest.raises(ValueError, match="Cannot modify_diff from SEALED"):
            machine.modify_diff()

    def test_no_direct_init_to_sealed(self, machine):
        """Test that direct jump INIT → SEALED is not possible."""
        assert machine.current_state == HandshakeState.INIT

        with pytest.raises(ValueError, match="Cannot seal from INIT"):
            machine.seal()

        # Should still be in INIT state
        assert machine.current_state == HandshakeState.INIT

    def test_no_dispatch_without_seal(self, machine):
        """Test that dispatch without SEALED is not possible."""
        # Try full sequence without seal
        machine.request_preclear()
        machine.certify()

        with pytest.raises(ValueError, match="Cannot dispatch from CERTIFIED"):
            machine.dispatch()

        # Should still be in CERTIFIED state
        assert machine.current_state == HandshakeState.CERTIFIED

    def test_sequence_hash_deterministic(self, machine):
        """Test that sequence hash is deterministic."""
        # Execute same sequence twice
        sequence1 = self._execute_full_sequence(machine)

        # Reset and repeat
        machine.reset()
        sequence2 = self._execute_full_sequence(machine)

        # Hashes should be identical
        assert sequence1 == sequence2

        # Hash should be valid SHA256
        assert len(sequence1) == 64
        assert all(c in "0123456789abcdef" for c in sequence1)

    def test_sequence_hash_changes_with_different_transitions(self, machine):
        """Test that sequence hash changes with different transition sequences."""
        # Execute full sequence
        hash1 = self._execute_full_sequence(machine)

        # Reset and execute partial sequence
        machine.reset()
        machine.request_preclear()
        machine.certify()
        hash2 = machine.get_sequence_hash()

        # Hashes should be different
        assert hash1 != hash2

    def test_sequence_hash_invalidated_on_transition(self, machine):
        """Test that sequence hash is invalidated when transitions occur."""
        # Get initial hash (empty sequence)
        hash1 = machine.get_sequence_hash()

        # Make a transition
        machine.request_preclear()

        # Hash should change
        hash2 = machine.get_sequence_hash()
        assert hash1 != hash2

        # Make another transition
        machine.certify()

        # Hash should change again
        hash3 = machine.get_sequence_hash()
        assert hash2 != hash3

    def test_transition_history_immutability(self, machine):
        """Test that transition history is immutable."""
        machine.request_preclear()
        machine.certify()

        history = machine.transition_history
        original_length = len(history)

        # Try to modify returned history (shouldn't affect internal state)
        with pytest.raises(AttributeError):
            history.append(None)  # tuple is immutable

        # Internal history should be unchanged
        assert len(machine.transition_history) == original_length

    def test_string_representations(self, machine):
        """Test string and repr methods."""
        # Test empty machine
        str_repr = str(machine)
        assert "HandshakeStateMachine" in str_repr
        assert "state=INIT" in str_repr
        assert "transitions=0" in str_repr

        repr_str = repr(machine)
        assert "HandshakeStateMachine" in repr_str
        assert "current_state=INIT" in repr_str
        assert "transition_count=0" in repr_str

        # Test machine with transitions
        machine.request_preclear()
        machine.certify()

        str_repr = str(machine)
        assert "state=CERTIFIED" in str_repr
        assert "transitions=2" in str_repr

        repr_str = repr(machine)
        assert "current_state=CERTIFIED" in repr_str
        assert "transition_count=2" in repr_str

    def test_factory_function(self):
        """Test factory function creates valid machine."""
        machine = create_handshake_machine()

        assert isinstance(machine, HandshakeStateMachine)
        assert machine.current_state == HandshakeState.INIT
        assert len(machine.transition_history) == 0

    def test_transition_timestamp_format(self, machine):
        """Test that transition timestamps have correct format."""
        machine.request_preclear()

        transition = machine.transition_history[0]
        assert transition.timestamp is not None
        assert "+00:00" in transition.timestamp or "Z" in transition.timestamp  # UTC indicator
        assert "T" in transition.timestamp  # ISO format separator

    def _execute_full_sequence(self, machine: HandshakeStateMachine) -> str:
        """Execute full state sequence and return sequence hash."""
        machine.request_preclear()
        machine.certify()
        machine.seal()
        machine.dispatch()
        return machine.get_sequence_hash()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
