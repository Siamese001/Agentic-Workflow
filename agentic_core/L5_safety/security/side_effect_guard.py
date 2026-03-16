"""Side-Effect Guard - Enforce Verification Before Any Side Effects

[PHASE 8] Ensures all side-effect operations require verified context.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "side_effect_guard", "execution_auth")
_emit_validates_capability("p2", "side_effect_guard", "capability_check")
_emit_routes_to_capability("p2", "side_effect_guard", "capability_route")
_emit_writes_via_uwg("p2", "side_effect_guard", "uwg_write")
_emit_blocks_direct_write("p2", "side_effect_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "side_effect_guard", "tool_invocation")
_emit_captures_execution_output("p2", "side_effect_guard", "exec_output")
_emit_dispatches_agent("p3", "side_effect_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "side_effect_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "side_effect_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "side_effect_guard", "healing_outcome")
_emit_escalates_failure("p3", "side_effect_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "side_effect_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "side_effect_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "side_effect_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "side_effect_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "side_effect_guard", "eval_metric")
_emit_stores_embedding("p4", "side_effect_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "side_effect_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "side_effect_guard", "exec_snapshot_link")
from .signature_verifier import VerificationContext

emit_replay_key("p0", "side_effect_guard")
emit_determinism_digest("p0", "side_effect_guard")

_emit_dispatches_healing_run("p1", "side_effect_guard", "L5")
_emit_routes_through("p1", "side_effect_guard", "L5")
_emit_escalates_to_human("p1", "side_effect_guard", "L5")
_emit_reads_policy_state("p1", "side_effect_guard", "L5")

logger = logging.getLogger(__name__)


class UnverifiedSideEffectError(RuntimeError):
    """Raised when side-effect is attempted without verification."""

    pass


class SideEffectGuard:
    """Guard that enforces verification before side effects."""

    def __init__(self):
        self._active_context: VerificationContext | None = None
        self._guard_enabled = True

    def set_context(self, context: VerificationContext) -> None:
        """Set the active verification context."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SideEffectGuard.set_context", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SideEffectGuard.set_context", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SideEffectGuard.set_context")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SideEffectGuard.set_context".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not context.is_verified:
            raise UnverifiedSideEffectError("ATTEMPT_TO_SET_UNVERIFIED_CONTEXT: Context must be verified")
        self._active_context = context
        logger.debug(f"SideEffectGuard: Set verified context for signer {context.signer_id}")

    def clear_context(self) -> None:
        """Clear the active verification context."""
        self._active_context = None
        logger.debug("SideEffectGuard: Cleared verification context")

    def require_verified(self, operation: str = "side-effect") -> VerificationContext:
        """
        Require verified context before proceeding.

        Raises UnverifiedSideEffectError if no verified context is active.
        """
        if not self._guard_enabled:
            logger.warning(f"SideEffectGuard: Guard disabled, allowing {operation}")
            from .signature_verifier import VerificationContext

            return VerificationContext(
                is_verified=True, signature_hash="disabled", signer_id="disabled", packet_hash="disabled"
            )
        if self._active_context is None:
            raise UnverifiedSideEffectError(
                f"UNVERIFIED_OPERATION_DENIED: {operation} attempted without verified context"
            )
        if not self._active_context.is_verified:
            raise UnverifiedSideEffectError(
                f"UNVERIFIED_CONTEXT_DENIED: {operation} attempted with unverified context"
            )
        logger.debug(f"SideEffectGuard: Allowed {operation} for signer {self._active_context.signer_id}")
        return self._active_context

    def disable(self) -> None:
        """Disable the guard (for testing only)."""
        self._guard_enabled = False
        logger.warning("SideEffectGuard: DISABLED - side effects allowed without verification")

    def enable(self) -> None:
        """Enable the guard."""
        self._guard_enabled = True
        logger.info("SideEffectGuard: ENABLED - verification required for side effects")

    @property
    def has_context(self) -> bool:
        """Check if a verified context is currently active."""
        return self._active_context is not None and self._active_context.is_verified


_global_guard: SideEffectGuard | None = None


def get_side_effect_guard() -> SideEffectGuard:
    """Get the global side-effect guard instance."""
    global _global_guard
    if _global_guard is None:
        _global_guard = SideEffectGuard()
    return _global_guard


def require_verified(operation: str = "side-effect") -> VerificationContext:
    """
    Require verified context before proceeding with side effect.

    Convenience function that raises UnverifiedSideEffectError if
    no verified context is active.
    """
    return get_side_effect_guard().require_verified(operation)


def set_verification_context(context: VerificationContext) -> None:
    """Set the global verification context."""
    get_side_effect_guard().set_context(context)


def clear_verification_context() -> None:
    """Clear the global verification context."""
    get_side_effect_guard().clear_context()


def requires_verification(operation_name: str | None = None):
    """Decorator to require verification before function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            require_verified(op_name)
            return func(*args, **kwargs)

        return wrapper

    return decorator


logger.info("SideEffectGuard: Initialized with verification enforcement")
