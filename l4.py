# FILE: 10_10/l4.py
"""
State Adapter · L4 Mutation Layer (v10_10 · Phase 3)
====================================================

Responsibilities:
    • Sole legal mutation surface for WorkflowState.
    • Apply StateTransitionEvent → updated WorkflowState.
    • Implement checkpoint + rollback hooks (G34–G36).
    • Emit state-transition telemetry (G15).
    • Must not:
          – call LLMs,
          – retrieve/rank,
          – plan,
          – enforce safety,
          – orchestrate DAG.

Inputs:
    • WorkflowState
    • StateTransitionEvent  (typed, atomic)
    • ExecutionContext      (read-only for telemetry/span)

Output:
    • New WorkflowState (pure functional update)
"""

from __future__ import annotations

from dataclasses import replace
from typing import Optional

from core.models.models import (
    WorkflowState,
    StateTransitionEvent,
    ExecutionContext,
    Checkpoint,
    RollbackRequest,
    RollbackResult,
)
from runtime.observability import start_span, end_span, log_exception


# =============================================================================
# Internal utilities
# =============================================================================


def _apply_patch(
    state: WorkflowState,
    event: StateTransitionEvent,
) -> WorkflowState:
    """
    Core patch application.

    Requirements:
        • Deterministic, type-safe update.
        • No side effects.
        • No LLM calls.
        • No orchestration.
    """
    # event.patch may be a dict or a typed patch object depending on
    # Phase-0/Phase-1 canonical models. We assume Phase-0 canonical structure.
    patch = getattr(event, "patch", None)
    if patch is None:
        return state

    if isinstance(patch, dict):
        return replace(state, **patch)

    # Typed patch object with .__dict__ or fields.
    if hasattr(patch, "__dict__"):
        return replace(state, **patch.__dict__)

    # Last-chance fallback: no mutation if patch format is unknown.
    return state


def _make_checkpoint(state: WorkflowState) -> Checkpoint:
    """
    Create a new immutable checkpoint snapshot of the WorkflowState.
    """
    return Checkpoint(snapshot=state)


def _apply_rollback(
    state: WorkflowState,
    request: RollbackRequest,
) -> RollbackResult:
    """
    Roll back to the specified checkpoint, returning the new state and localized result.
    """
    checkpoint = getattr(request, "checkpoint", None)
    if checkpoint is None or getattr(checkpoint, "snapshot", None) is None:
        return RollbackResult(
            ok=False,
            reason="invalid_checkpoint",
            state_after=state,
        )

    snapshot: WorkflowState = checkpoint.snapshot
    return RollbackResult(
        ok=True,
        reason="rolled_back",
        state_after=snapshot,
    )


# =============================================================================
# Public API
# =============================================================================


def apply_state_transition(
    state: WorkflowState,
    event: StateTransitionEvent,
    ctx: Optional[ExecutionContext] = None,
) -> WorkflowState:
    """
    Apply a single typed StateTransitionEvent to the WorkflowState.

    Emits L4-layer state-transition telemetry.
    """
    span = start_span("l4.apply_state_transition", ctx=ctx.span_context() if ctx else None)
    try:
        new_state = _apply_patch(state, event)
        return new_state
    except Exception as exc:  # noqa: BLE001
        log_exception("l4.state_transition_error", exc)
        return state
    finally:
        end_span(span)


def commit_checkpoint(
    state: WorkflowState,
    ctx: Optional[ExecutionContext] = None,
) -> Checkpoint:
    """
    Create a deterministic checkpoint (G34).

    Does not mutate state; returns a new Checkpoint object.
    """
    span = start_span("l4.commit_checkpoint", ctx=ctx.span_context() if ctx else None)
    try:
        return _make_checkpoint(state)
    except Exception as exc:  # noqa: BLE001
        log_exception("l4.commit_checkpoint_error", exc)
        return _make_checkpoint(state)
    finally:
        end_span(span)


def rollback_state(
    state: WorkflowState,
    request: RollbackRequest,
    ctx: Optional[ExecutionContext] = None,
) -> RollbackResult:
    """
    Apply rollback based on the provided RollbackRequest (G35–G36).

    The returned RollbackResult includes:
        • ok: bool
        • reason: str
        • state_after: WorkflowState
    """
    span = start_span("l4.rollback_state", ctx=ctx.span_context() if ctx else None)
    try:
        return _apply_rollback(state, request)
    except Exception as exc:  # noqa: BLE001
        log_exception("l4.rollback_error", exc)
        # Return a deterministic fallback.
        return RollbackResult(
            ok=False,
            reason="rollback_exception",
            state_after=state,
        )
    finally:
        end_span(span)


def apply_state_patch(
    state: WorkflowState,
    patch,
    ctx: Optional[ExecutionContext] = None,
) -> WorkflowState:
    """Compatibility shim for older call sites expecting apply_state_patch.

    Wraps the provided patch object into a StateTransitionEvent and
    delegates to apply_state_transition, which owns all mutation logic.
    """

    event = StateTransitionEvent(event_id="patch", patch=patch)
    return apply_state_transition(state, event, ctx)
