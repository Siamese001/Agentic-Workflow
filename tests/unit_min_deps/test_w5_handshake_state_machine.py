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
