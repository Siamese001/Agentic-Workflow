# FILE: 10_10/l4.py
"""
Unified L4 State Adapter (v10_10 · Phase 1)
==========================================

Responsibilities:
    • L4 is the ONLY layer allowed to mutate persisted workflow state.
    • Apply typed StateTransitionEvent objects to build final state patches.
    • Generate checkpoint and rollback snapshots for L3 correction loops.
    • Record all mutations to observability telemetry streams.
    • No LLM, no retrieval, no planning, no safety logic.

Non-Responsibilities:
    • No generation of transitions (L2/L3 create transitions).
    • No DAG orchestration (L3).
    • No safety enforcement (L5).
    • No business logic (L1/L2).

This module restores the full v10_8 / v10_9 state-engine capability:
    • Typed patches
    • Deterministic state merge
    • Checkpoint/rollback
    • Correction-aware application
    • Telemetry via StateTransitionEvent and patch-level spans
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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

def _apply_transition(
    base: Dict[str, Any],
    event: StateTransitionEvent,
) -> Dict[str, Any]:
    """
    Deterministically merge a typed transition event into state.
    Never mutates input dict in place.
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
    state: WorkflowState,
    transitions: List[StateTransitionEvent],
) -> WorkflowState:
    """
    Apply a series of StateTransitionEvents to the WorkflowState.
    """
    result = state.to_dict()

    for evt in transitions:
        result = _apply_transition(result, evt)

    return WorkflowState.from_dict(result)


# =============================================================================
# Checkpoint / Rollback System
# =============================================================================

@dataclass
class CheckpointSnapshot:
    """
    A copy of the WorkflowState before entering a retry/replan branch.
    """
    state_dict: Dict[str, Any]


def create_checkpoint(state: WorkflowState) -> CheckpointSnapshot:
    return CheckpointSnapshot(state_dict=state.to_dict())


def rollback_to(checkpoint: CheckpointSnapshot) -> WorkflowState:
    return WorkflowState.from_dict(dict(checkpoint.state_dict))


# =============================================================================
# Correction-Aware Patch Construction
# =============================================================================

def _build_correction_transitions(
    corrections: List[CorrectionSignal],
) -> List[StateTransitionEvent]:
    """
    Convert CorrectionSignal objects into StateTransitionEvents.
    Phase 1 version: minimal signals.
    """
    transitions: List[StateTransitionEvent] = []

    for c in corrections:
        transitions.append(
            StateTransitionEvent(
                operation="append_list",
                field="correction_log",
                value=[{
                    "surface": c.surface,
                    "severity": c.severity,
                    "reason": c.reason,
                    "action": c.recommended_action,
                }],
            )
        )

    return transitions


def _build_safety_transitions(safety_passed: bool) -> List[StateTransitionEvent]:
    """
    Encode safety gating into state.
    """
    return [
        StateTransitionEvent(
            operation="update_field",
            field="safety_passed",
            value=bool(safety_passed),
        )
    ]


def _build_l2_output_transition(l2_results: Any) -> List[StateTransitionEvent]:
    """
    Persist relevant L2 artifacts into state.
    """
    return [
        StateTransitionEvent(
            operation="update_field",
            field="draft_output",
            value=l2_results.drafting.output,
        ),
        StateTransitionEvent(
            operation="update_field",
            field="qa_findings",
            value=[f for f in getattr(l2_results.qa, "findings", [])],
        ),
        StateTransitionEvent(
            operation="update_field",
            field="safety_findings",
            value=[f for f in getattr(l2_results.safety, "findings", [])],
        ),
    ]


# =============================================================================
# Public Entrypoint
# =============================================================================

def apply_state_patch(
    l2_results: Any,
    corrections: List[CorrectionSignal],
    ctx: ExecutionContext,
    safety_passed: bool,
) -> Dict[str, Any]:
    """
    Primary L4 entrypoint called by L3.

    Inputs:
        • l2_results: L2ResultBundle
        • corrections: correction signals from L3
        • safety_passed: safety gate result
        • ctx: execution context (provides previous WorkflowState)

    Outputs:
        • final state patch dict

    Behavior:
        • Collect transitions: L2 outputs + corrections + safety gating
        • Apply transitions to existing state
        • Emit telemetry events
        • Return final diff as a patch
    """
    span = start_span("l4.apply_state_patch", ctx=ctx.span_context())
    try:
        prev_state = ctx.state
        transitions: List[StateTransitionEvent] = []

        # L2 output transitions
        transitions.extend(_build_l2_output_transition(l2_results))

        # Correction transitions
        transitions.extend(_build_correction_transitions(corrections))

        # Safety pass/fail
        transitions.extend(_build_safety_transitions(safety_passed))

        # Emit transition telemetry
        for evt in transitions:
            emit_state_transition(evt)

        # Compute new state
        new_state = _apply_patch_series(prev_state, transitions)

        # Emit "final patch" event
        emit_telemetry_event(
            "l4.state_patch_complete",
            attributes={
                "num_transitions": len(transitions),
                "safety_passed": safety_passed,
            },
        )

        # Compute diff patch dict
        patch = StatePatch.from_states(prev_state, new_state)
        ctx.state = new_state  # L4 is the ONLY layer allowed to mutate

        return patch.to_dict()

    except Exception as exc:
        log_exception("l4.state_patch_error", exc)
        raise
    finally:
        end_span(span)
