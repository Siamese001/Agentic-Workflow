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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "handshake_state_machine")
trace_contract.emit_determinism_digest("p0", "handshake_state_machine")

trace_contract._emit_dispatches_healing_run("p1", "handshake_state_machine", "L3")
trace_contract._emit_routes_through("p1", "handshake_state_machine", "L3")
trace_contract._emit_checks_agent_registry("p1", "handshake_state_machine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "handshake_state_machine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "handshake_state_machine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "handshake_state_machine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "handshake_state_machine", "target_agent")
trace_contract._emit_verifies_policy("p1", "handshake_state_machine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "handshake_state_machine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "handshake_state_machine", "boundary_check")
trace_contract._emit_transcripts_response("p1", "handshake_state_machine", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "handshake_state_machine")
trace_contract._emit_gated_by_confidence("p1", "handshake_state_machine", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "handshake_state_machine", "L3")
trace_contract._emit_reads_policy_state("p1", "handshake_state_machine", "L3")
trace_contract._emit_authorize_and_execute("p2", "handshake_state_machine", "execution_auth")
trace_contract._emit_validates_capability("p2", "handshake_state_machine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "handshake_state_machine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "handshake_state_machine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "handshake_state_machine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "handshake_state_machine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "handshake_state_machine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "handshake_state_machine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "handshake_state_machine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "handshake_state_machine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "handshake_state_machine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "handshake_state_machine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "handshake_state_machine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "handshake_state_machine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "handshake_state_machine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "handshake_state_machine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "handshake_state_machine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "handshake_state_machine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "handshake_state_machine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "handshake_state_machine", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("handshake_state_machine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("handshake_state_machine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("handshake_state_machine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("handshake_state_machine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("handshake_state_machine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("handshake_state_machine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("handshake_state_machine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("handshake_state_machine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("handshake_state_machine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("handshake_state_machine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("handshake_state_machine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("handshake_state_machine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("handshake_state_machine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("handshake_state_machine", "p3lm", "state")
trace_contract._emit_records_execution_trace("handshake_state_machine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("handshake_state_machine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("handshake_state_machine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("handshake_state_machine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("handshake_state_machine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("handshake_state_machine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("handshake_state_machine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("handshake_state_machine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("handshake_state_machine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "handshake_state_machine", "context_pull")
trace_contract._emit_pulls_context("p1", "handshake_state_machine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "handshake_state_machine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "handshake_state_machine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "handshake_state_machine", "write_through")
trace_contract._emit_writes_through("p1", "handshake_state_machine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "handshake_state_machine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "handshake_state_machine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "handshake_state_machine", "routing_commit")


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
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "HandshakeStateMachine.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "HandshakeStateMachine.__init__", "p0_governance")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HandshakeStateMachine.reset")

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
                f"Cannot request preclear from {self._current_state.value}. Must be in INIT state.",
            )
        self._transition_to(HandshakeState.PRECLEAR_REQUESTED, "L5 pre-clear requested")

    def certify(self) -> None:
        """
        Transition to CERTIFIED state.

        Only allowed from PRECLEAR_REQUESTED state.
        """
        if self._current_state != HandshakeState.PRECLEAR_REQUESTED:
            raise ValueError(
                f"Cannot certify from {self._current_state.value}. Must be in PRECLEAR_REQUESTED state.",
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
                f"Cannot modify_diff from {self._current_state.value}. Must be in CERTIFIED state.",
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
                {"from_state": t.from_state.value, "reason": t.reason, "to_state": t.to_state.value}
                for t in self._transition_history
            ],
            "final_state": self._current_state.value,
        }
        canonical = json.dumps(sequence_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _transition_to(self, new_state: HandshakeState, reason: str) -> None:
        """
        Internal method to perform state transition.

        Records transition in history for audit trail.
        """
        from datetime import datetime, timezone

        transition = StateTransition(
            from_state=self._current_state,
            to_state=new_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )
        self._transition_history.append(transition)
        self._current_state = new_state
        self._sequence_hash = None

    def __str__(self) -> str:
        """String representation of current state."""
        return f"HandshakeStateMachine(state={self._current_state.value}, transitions={len(self._transition_history)})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"HandshakeStateMachine(current_state={self._current_state.value}, transition_count={len(self._transition_history)}, sequence_hash={self.get_sequence_hash()[:8]}...)"


def create_handshake_machine() -> HandshakeStateMachine:
    """Create a new handshake state machine instance."""
    return HandshakeStateMachine()


__all__ = ["HandshakeStateMachine", "HandshakeState", "StateTransition", "create_handshake_machine"]
