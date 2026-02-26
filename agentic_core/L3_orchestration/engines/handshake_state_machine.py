"""
Sequential Handshake State Machine - W5 Implementation

Deterministic state machine for L3 orchestration handshake protocol.
Enforces strict state transitions with no bypass allowed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum


class HandshakeState(Enum):
    """States in the sequential handshake protocol."""

    INIT = "INIT"
    PRECLEAR_REQUESTED = "PRECLEAR_REQUESTED"
    CERTIFIED = "CERTIFIED"
    SEALED = "SEALED"
    DISPATCHED = "DISPATCHED"


@dataclass
class StateTransition:
    """Record of a state transition for audit trail."""

    from_state: HandshakeState
    to_state: HandshakeState
    timestamp: str
    reason: str


class HandshakeStateMachine:
    """
    Deterministic sequential handshake state machine.

    Enforces strict state transitions:
    - Cannot reach SEALED without CERTIFIED
    - MODIFY_DIFF forces CERTIFIED → PRECLEAR_REQUESTED
    - No direct jump INIT → SEALED
    - No dispatch without SEALED
    """

    def __init__(self):
        self._current_state = HandshakeState.INIT
        self._transition_history: list[StateTransition] = []
        self._sequence_hash: str | None = None

    @property
    def current_state(self) -> HandshakeState:
        """Get current handshake state."""
        return self._current_state

    @property
    def transition_history(self) -> tuple[StateTransition, ...]:
        """Get immutable copy of transition history."""
        return tuple(self._transition_history)

    def reset(self) -> None:
        """Reset state machine to INIT state."""
        self._current_state = HandshakeState.INIT
        self._transition_history.clear()
        self._sequence_hash = None

    def request_preclear(self) -> None:
        """
        Transition to PRECLEAR_REQUESTED state.

        Only allowed from INIT state.
        """
        if self._current_state != HandshakeState.INIT:
            raise ValueError(
                f"Cannot request preclear from {self._current_state.value}. Must be in INIT state."
            )

        self._transition_to(HandshakeState.PRECLEAR_REQUESTED, "L5 pre-clear requested")

    def certify(self) -> None:
        """
        Transition to CERTIFIED state.

        Only allowed from PRECLEAR_REQUESTED state.
        """
        if self._current_state != HandshakeState.PRECLEAR_REQUESTED:
            raise ValueError(
                f"Cannot certify from {self._current_state.value}. Must be in PRECLEAR_REQUESTED state."
            )

        self._transition_to(HandshakeState.CERTIFIED, "L5 certification granted")

    def seal(self) -> None:
        """
        Transition to SEALED state.

        Only allowed from CERTIFIED state.
        """
        if self._current_state != HandshakeState.CERTIFIED:
            raise ValueError(f"Cannot seal from {self._current_state.value}. Must be in CERTIFIED state.")

        self._transition_to(HandshakeState.SEALED, "Plan sealed for execution")

    def dispatch(self) -> None:
        """
        Transition to DISPATCHED state.

        Only allowed from SEALED state.
        """
        if self._current_state != HandshakeState.SEALED:
            raise ValueError(f"Cannot dispatch from {self._current_state.value}. Must be in SEALED state.")

        self._transition_to(HandshakeState.DISPATCHED, "Dispatched to L2 execution")

    def modify_diff(self) -> None:
        """
        Handle MODIFY_DIFF operation.

        Forces CERTIFIED → PRECLEAR_REQUESTED transition.
        Invalidates prior certification.
        """
        if self._current_state != HandshakeState.CERTIFIED:
            raise ValueError(
                f"Cannot modify_diff from {self._current_state.value}. Must be in CERTIFIED state."
            )

        self._transition_to(HandshakeState.PRECLEAR_REQUESTED, "MODIFY_DIFF invalidated certification")

    def get_sequence_hash(self) -> str:
        """
        Compute hash of the complete state transition sequence.

        Used for determinism digest calculation.
        """
        if self._sequence_hash is None:
            self._sequence_hash = self._compute_sequence_hash()
        return self._sequence_hash

    def _compute_sequence_hash(self) -> str:
        """Compute SHA256 hash of transition sequence."""
        sequence_data = {
            "transitions": [
                {
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "timestamp": t.timestamp,
                    "reason": t.reason,
                }
                for t in self._transition_history
            ],
            "final_state": self._current_state.value,
        }

        # Canonical JSON for deterministic hashing
        canonical = json.dumps(sequence_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _transition_to(self, new_state: HandshakeState, reason: str) -> None:
        """
        Internal method to perform state transition.

        Records transition in history for audit trail.
        """
        from datetime import datetime

        transition = StateTransition(
            from_state=self._current_state,
            to_state=new_state,
            timestamp=datetime.utcnow().isoformat() + "Z",
            reason=reason,
        )

        self._transition_history.append(transition)
        self._current_state = new_state
        self._sequence_hash = None  # Invalidate cached hash

    def __str__(self) -> str:
        """String representation of current state."""
        return f"HandshakeStateMachine(state={self._current_state.value}, transitions={len(self._transition_history)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"HandshakeStateMachine("
            f"current_state={self._current_state.value}, "
            f"transition_count={len(self._transition_history)}, "
            f"sequence_hash={self.get_sequence_hash()[:8]}...)"
        )


# Factory function for testing
def create_handshake_machine() -> HandshakeStateMachine:
    """Create a new handshake state machine instance."""
    return HandshakeStateMachine()


__all__ = [
    "HandshakeStateMachine",
    "HandshakeState",
    "StateTransition",
    "create_handshake_machine",
]
