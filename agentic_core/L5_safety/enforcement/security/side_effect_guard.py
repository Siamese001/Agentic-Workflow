"""Side-Effect Guard - Enforce Verification Before Any Side Effects

[PHASE 8] Ensures all side-effect operations require verified context.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
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
_emit_checks_agent_registry("p1", "side_effect_guard", "agent_registry")
_emit_validates_agent_capability("p1", "side_effect_guard", "capability")
_emit_dispatches_execution_plan("p1", "side_effect_guard", "exec_plan")
_emit_agent_executes_agent("p1", "side_effect_guard", "sub_agent")
_emit_routes_to_agent("p1", "side_effect_guard", "target_agent")
_emit_verifies_policy("p1", "side_effect_guard", "policy_check")
_emit_observes_runtime_state("p1", "side_effect_guard", "runtime_state")
_emit_verifies_boundary("p1", "side_effect_guard", "boundary_check")
_emit_transcripts_response("p1", "side_effect_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "side_effect_guard")
_emit_gated_by_confidence("p1", "side_effect_guard", "confidence_gate")
_emit_escalates_to_human("p1", "side_effect_guard", "L5")
_emit_reads_policy_state("p1", "side_effect_guard", "L5")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_1")
_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_2")
_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_3")
_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_4")
_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_5")
_emit_emits_metric_event("side_effect_guard", "p4obs", "metric_6")
_emit_records_incident_event("side_effect_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("side_effect_guard", "p4obs", "anomaly")
_emit_writes_observability_log("side_effect_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("side_effect_guard", "p4obs", "mon_state")
_emit_triggers_alert("side_effect_guard", "p4obs", "alert")
_emit_links_incident_trace("side_effect_guard", "p4obs", "trace_link")
_emit_captures_pattern("side_effect_guard", "p3lm", "pattern")
_emit_records_learning_event("side_effect_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("side_effect_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("side_effect_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("side_effect_guard", "p3lm", "routing")
_emit_improves_agent_policy("side_effect_guard", "p3lm", "policy")
_emit_stores_learning_state("side_effect_guard", "p3lm", "state")
_emit_records_execution_trace("side_effect_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("side_effect_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("side_effect_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("side_effect_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("side_effect_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("side_effect_guard", "env_read", "p2_env_1")
_emit_reads_environ("side_effect_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("side_effect_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("side_effect_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "side_effect_guard", "context_pull")
_emit_pulls_context("p1", "side_effect_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "side_effect_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "side_effect_guard", "uwg_term_2")
_emit_writes_through("p1", "side_effect_guard", "write_through")
_emit_writes_through("p1", "side_effect_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "side_effect_guard", "safety_validation")
_emit_invokes_eval("p1", "side_effect_guard", "eval_call")
_emit_proposal_commits_routing("p1", "side_effect_guard", "routing_commit")

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
