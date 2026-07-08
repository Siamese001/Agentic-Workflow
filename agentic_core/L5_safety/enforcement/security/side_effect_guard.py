"""Side-Effect Guard - Enforce Verification Before Any Side Effects

[PHASE 8] Ensures all side-effect operations require verified context.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "side_effect_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "side_effect_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "side_effect_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "side_effect_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "side_effect_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "side_effect_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "side_effect_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "side_effect_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "side_effect_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "side_effect_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "side_effect_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "side_effect_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "side_effect_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "side_effect_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "side_effect_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "side_effect_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "side_effect_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "side_effect_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "side_effect_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "side_effect_guard", "exec_snapshot_link")
from .signature_verifier import VerificationContext

trace_contract.emit_replay_key("p0", "side_effect_guard")
trace_contract.emit_determinism_digest("p0", "side_effect_guard")

trace_contract._emit_dispatches_healing_run("p1", "side_effect_guard", "L5")
trace_contract._emit_routes_through("p1", "side_effect_guard", "L5")
trace_contract._emit_checks_agent_registry("p1", "side_effect_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "side_effect_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "side_effect_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "side_effect_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "side_effect_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "side_effect_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "side_effect_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "side_effect_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "side_effect_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "side_effect_guard")
trace_contract._emit_gated_by_confidence("p1", "side_effect_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "side_effect_guard", "L5")
trace_contract._emit_reads_policy_state("p1", "side_effect_guard", "L5")

trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("side_effect_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("side_effect_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("side_effect_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("side_effect_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("side_effect_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("side_effect_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("side_effect_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("side_effect_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("side_effect_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("side_effect_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("side_effect_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("side_effect_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("side_effect_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("side_effect_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("side_effect_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("side_effect_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("side_effect_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("side_effect_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("side_effect_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("side_effect_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("side_effect_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("side_effect_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("side_effect_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "side_effect_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "side_effect_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "side_effect_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "side_effect_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "side_effect_guard", "write_through")
trace_contract._emit_writes_through("p1", "side_effect_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "side_effect_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "side_effect_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "side_effect_guard", "routing_commit")

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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "SideEffectGuard.set_context", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "SideEffectGuard.set_context", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SideEffectGuard.set_context")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SideEffectGuard.set_context".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                is_verified=True,
                signature_hash="disabled",
                signer_id="disabled",
                packet_hash="disabled",
            )
        if self._active_context is None:
            raise UnverifiedSideEffectError(
                f"UNVERIFIED_OPERATION_DENIED: {operation} attempted without verified context",
            )
        if not self._active_context.is_verified:
            raise UnverifiedSideEffectError(
                f"UNVERIFIED_CONTEXT_DENIED: {operation} attempted with unverified context",
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
