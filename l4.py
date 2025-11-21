# FILE: 10_10/l4.py
"""
Unified L4 State Adapter (v10_10 · Phase 3)
==========================================

Responsibilities:
    • L4 is the ONLY layer allowed to mutate persisted workflow state.
    • Apply typed StateTransitionEvent objects to build final state patches.
    • Generate checkpoint and rollback snapshots for correction loops.
    • Record all mutations to observability telemetry streams.
    • No LLM, no retrieval, no planning, no safety logic.

Non-Responsibilities:
    • No generation of transitions (L2/L3 create transitions).
    • No DAG orchestration (L3).
    • No safety enforcement (L5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from models import (
    WorkflowState,
    StateTransitionEvent,
    StatePatch,
    CorrectionSignal,
    ExecutionContext,
)
from observability import (
    start_span,
    end_span,
    emit_state_transition,
    emit_telemetry_event,
    log_exception,
)


# =============================================================================
# Helpers
# =============================================================================


def _apply_transition(base: Dict[str, Any], event: StateTransitionEvent) -> Dict[str, Any]:
    """
    Apply a single StateTransitionEvent to a dict representing WorkflowState.
    """
    new_state = dict(base)

    # Each event is a typed mutation request
    if event.operation == "update_field":
        new_state[event.field] = event.value

    elif event.operation == "remove_field":
        if event.field in new_state:
            del new_state[event.field]

    elif event.operation == "merge_dict":
        existing = new_state.get(event.field, {})
        if not isinstance(existing, dict):
            existing = {}
        merged = {**existing, **event.value}
        new_state[event.field] = merged

    elif event.operation == "append_list":
        existing = new_state.get(event.field, [])
        if not isinstance(existing, list):
            existing = []
        new_state[event.field] = existing + list(event.value)

    else:
        raise ValueError(f"Unknown transition op: {event.operation}")

    return new_state


def _apply_patch_series(
    base_state: WorkflowState,
    events: List[StateTransitionEvent],
) -> WorkflowState:
    """
    Apply a series of StateTransitionEvent objects to a WorkflowState.
    """
    state_dict: Dict[str, Any] = base_state.model_dump()

    for ev in events:
        state_dict = _apply_transition(state_dict, ev)

    return WorkflowState(**state_dict)


def _build_l2_output_transition(l2_results: Any) -> List[StateTransitionEvent]:
    """
    Persist relevant L2 artifacts into state.
    """
    return [
        StateTransitionEvent(
            operation="update_field",
            field="draft_output",
            value=[s.model_dump() for s in getattr(l2_results.drafting, "sections", [])],
        ),
        StateTransitionEvent(
            operation="update_field",
            field="qa_findings",
            value=[f.model_dump() for f in getattr(l2_results.qa, "findings", [])],
        ),
        StateTransitionEvent(
            operation="update_field",
            field="safety_findings",
            value=[f.model_dump() for f in getattr(l2_results.safety, "findings", [])],
        ),
    ]


def _build_correction_transitions(
    corrections: List[CorrectionSignal],
) -> List[StateTransitionEvent]:
    """
    Convert CorrectionSignal objects into StateTransitionEvents.
    Phase 3 version: structured log entries.
    """
    transitions: List[StateTransitionEvent] = []

    for c in corrections:
        transitions.append(
            StateTransitionEvent(
                operation="append_list",
                field="correction_log",
                value=[
                    {
                        "surface": c.surface,
                        "severity": c.severity,
                        "reason": c.reason,
                        "action": c.recommended_action,
                    }
                ],
            )
        )

    return transitions


def _build_safety_transitions(safety_passed: bool) -> List[StateTransitionEvent]:
    """
    Persist safety pass/fail signal.
    """
    return [
        StateTransitionEvent(
            operation="update_field",
            field="safety_passed",
            value=bool(safety_passed),
        )
    ]


# =============================================================================
# Checkpoints & Rollback
# =============================================================================


@dataclass
class CheckpointSnapshot:
    """
    Immutable snapshot of WorkflowState for rollback.

    L4 is responsible for creating and applying checkpoints.
    """

    workflow_id: str
    state_dict: Dict[str, Any]


def create_checkpoint(state: WorkflowState) -> CheckpointSnapshot:
    """
    Create a checkpoint snapshot from a WorkflowState.
    """
    return CheckpointSnapshot(
        workflow_id=state.workflow_id,
        state_dict=state.model_dump(),
    )


def rollback_to(checkpoint: CheckpointSnapshot) -> WorkflowState:
    """
    Roll back to a previously-created checkpoint.
    """
    return WorkflowState(**checkpoint.state_dict)


# =============================================================================
# Public API: apply_l2_results_to_state
# =============================================================================


def apply_l2_results_to_state(
    ctx: ExecutionContext,
    state: WorkflowState,
    l2_results: Any,
    corrections: List[CorrectionSignal],
    safety_passed: bool,
) -> Dict[str, Any]:
    """
    Apply L2 results and correction signals to the workflow state.

    L4 is the only layer allowed to perform this mutation.

    Returns:
        A dict representing the state patch (delta) applied.
    """
    span = start_span("l4.apply_state", ctx=ctx.span_context())
    try:
        prev_state = state

        # Build transitions from L2 outputs, corrections, and safety.
        transitions: List[StateTransitionEvent] = []
        transitions.extend(_build_l2_output_transition(l2_results))
        transitions.extend(_build_correction_transitions(corrections))
        transitions.extend(_build_safety_transitions(safety_passed))

        # Emit transition-level telemetry.
        for ev in transitions:
            emit_state_transition(ev)

        # Apply patch series.
        new_state = _apply_patch_series(prev_state, transitions)

        emit_telemetry_event(
            "state_mutation",
            {
                "workflow_id": state.workflow_id,
                "num_transitions": len(transitions),
            },
        )

        # Compute diff patch dict.
        patch = StatePatch.from_states(prev_state, new_state)

        # L4 is the ONLY layer allowed to mutate ctx.state.
        ctx.state = new_state  # type: ignore[attr-defined]

        return patch.to_dict()

    except Exception as exc:
        log_exception("l4.state_patch_error", exc)
        raise
    finally:
        end_span(span)
