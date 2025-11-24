"""Manages workflow state, checkpoints, and rollbacks so each resume run can move forward safely, be traced over time, and be restored cleanly if something goes wrong."""

# FILE: 10_10/l4.py

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
    """Applies a state patch described by an event so workflow progress for a resume is updated in a controlled, reversible way."""
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
    """Creates an immutable snapshot of the workflow state so a resume run can be safely restored to this point later."""
    return Checkpoint(snapshot=state)


def _apply_rollback(
    state: WorkflowState,
    request: RollbackRequest,
) -> RollbackResult:
    """Rolls back to a given checkpoint and reports whether the resume state was successfully restored."""
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
    """Applies a single, well-defined change to workflow state so the system has a reliable, auditable view of where each resume is in the process."""
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
    """Creates a checkpoint of the current workflow state so a resume run can be rolled back to a clean, known-good position if needed."""
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
    """Return to a previously saved checkpoint if something goes wrong.

    Using a :class:`RollbackRequest` that points at a specific checkpoint,
    this function restores the workflow state to that earlier snapshot and
    reports whether the rollback was successful.

    This ability to roll back is important when an error or bad output is
    detected later in the process. It lets operators undo problematic steps
    without corrupting the overall workflow or losing the history of what
    happened.
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
    """Compatibility helper that adapts older patch-style updates.

    Some older parts of the system still expect to provide a loose "patch"
    object instead of a fully-typed event. This function wraps that patch into
    a :class:`StateTransitionEvent` and forwards the work to
    :func:`apply_state_transition`, so all real mutation still flows through
    the same safe path.

    For business purposes, this preserves existing integrations while ensuring
    that state changes remain controlled and traceable.
    """

    event = StateTransitionEvent(event_id="patch", patch=patch)
    return apply_state_transition(state, event, ctx)
