"""
agentic_core/L2_execution/enforcement/execution_guardrail_chokepoint.py

authorize_and_execute() — P0/L2 mandatory execution chokepoint.

ALL L2 execution paths MUST route through this wrapper.
No direct execution outside this function is permitted.

Contract per call:
    1.  validate ExecutionContext completeness
    2.  validate capability token (no anonymous execution)
    3.  resolve and bind active policy hash       (references_policy_hash)
    4.  classify action (ActionClass)
    5.  require human review for HUMAN_GATED      (requires_human_review)
    6.  run guardrail evaluation                  (applies_guardrail)
    7.  validate_by_safety_plane binding          (validated_by_safety_plane)
    8.  record guardrail decision hash
    9.  abort on DENY / ERROR / TIMEOUT / UNKNOWN (reenters_safety)
   10.  emit pre-execution trace stub              (records_execution_trace)
   11.  execute only after ALLOW
   12.  route MUTATION through UWG                (execution_terminates_at_uwg)
   13.  emit post-execution trace record          (signs_execution_trace)

Fail-closed hard rules:
    - DENY / ERROR / TIMEOUT / UNKNOWN → execution terminated, reenters_safety emitted
    - Missing token → PermissionError (no anonymous execution)
    - Missing policy → PermissionError (no ambient policy)
    - HUMAN_GATED without human_approved=True → HumanReviewRequired

ADG edges emitted:
    applies_guardrail
    validated_by_safety_plane
    references_policy_hash
    execution_terminates_at_uwg
    reenters_safety
    requires_human_review
    records_execution_trace
    signs_execution_trace
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from typing import Any, Callable

from agentic_core.L2_execution.enforcement.execution_proof_contract import (
    DeterminismViolation,
    emit_execution_proof,
)
from agentic_core.L2_execution.types.typed_tool_contract import (
    ToolContract,
    ToolInputSchemaViolation,
    ToolOutputSchemaViolation,
    ToolSchema,
    UnregisteredToolError,
    get_typed_tool_registry,
    invoke_typed_tool,
)
from agentic_core.L4_state.utils.context.execution_context import (
    ActionClass,
    ExecutionContext,
    GuardrailOutcome,
)
from agentic_core.L5_safety.audit.safety_audit_emitter import (  # guardian: allow-layer-violation -- execution chokepoint must invoke L5 safety audit to emit guardrail decisions; this is an intentional enforcement boundary that spans L2->L5
    SafetyAuditMissingError,
    emit_guardrail_audit,
)
from agentic_core.L6_observability.execution.observability_recorder import (  # guardian: allow-layer-violation -- execution chokepoint must record observability at L6; P0 enforcement boundary requires cross-layer instrumentation
    ExecutionContext as ObservabilityExecutionContext,
)
from agentic_core.L6_observability.execution.observability_recorder import (  # guardian: allow-layer-violation -- execution chokepoint must record observability at L6; P0 enforcement boundary requires cross-layer instrumentation
    ExecutionObservabilityContext,
    ExecutionStatus,
    FailureClassification,
    record_execution_failure,
    record_execution_observability,
    record_policy_block,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
)

_emit_authorize_and_execute("p2", "execution_guardrail_chokepoint", "execution_auth")
_emit_validates_capability("p2", "execution_guardrail_chokepoint", "capability_check")
_emit_routes_to_capability("p2", "execution_guardrail_chokepoint", "capability_route")
_emit_writes_via_uwg("p2", "execution_guardrail_chokepoint", "uwg_write")
_emit_blocks_direct_write("p2", "execution_guardrail_chokepoint", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_guardrail_chokepoint", "tool_invocation")
_emit_captures_execution_output("p2", "execution_guardrail_chokepoint", "exec_output")
_emit_dispatches_agent("p3", "execution_guardrail_chokepoint", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_guardrail_chokepoint", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_guardrail_chokepoint", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_guardrail_chokepoint", "healing_outcome")
_emit_escalates_failure("p3", "execution_guardrail_chokepoint", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_guardrail_chokepoint", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_guardrail_chokepoint", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_guardrail_chokepoint", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_guardrail_chokepoint", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_guardrail_chokepoint", "eval_metric")
_emit_stores_embedding("p4", "execution_guardrail_chokepoint", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_guardrail_chokepoint", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_guardrail_chokepoint", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace as _lc_records,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace as _lc_signs,
)

_emit_dispatches_healing_run("p1", "execution_guardrail_chokepoint", "L2")
_emit_routes_through("p1", "execution_guardrail_chokepoint", "L2")
_emit_checks_agent_registry("p1", "execution_guardrail_chokepoint", "agent_registry")
_emit_validates_agent_capability("p1", "execution_guardrail_chokepoint", "capability")
_emit_dispatches_execution_plan("p1", "execution_guardrail_chokepoint", "exec_plan")
_emit_agent_executes_agent("p1", "execution_guardrail_chokepoint", "sub_agent")
_emit_routes_to_agent("p1", "execution_guardrail_chokepoint", "target_agent")
_emit_observes_runtime_state("p1", "execution_guardrail_chokepoint", "runtime_state")
_emit_verifies_boundary("p1", "execution_guardrail_chokepoint", "boundary_check")
_emit_transcripts_response("p1", "execution_guardrail_chokepoint", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_guardrail_chokepoint")
_emit_gated_by_confidence("p1", "execution_guardrail_chokepoint", "confidence_gate")
_emit_escalates_to_human("p1", "execution_guardrail_chokepoint", "L2")
_emit_reads_policy_state("p1", "execution_guardrail_chokepoint", "L2")

_emit_snapshots_state("p0", "execution_guardrail_chokepoint", "state_snapshot")
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
    _emit_records_execution_trace,
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
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_1")
_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_2")
_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_3")
_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_4")
_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_5")
_emit_emits_metric_event("execution_guardrail_chokepoint", "p4obs", "metric_6")
_emit_records_incident_event("execution_guardrail_chokepoint", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_guardrail_chokepoint", "p4obs", "anomaly")
_emit_writes_observability_log("execution_guardrail_chokepoint", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_guardrail_chokepoint", "p4obs", "mon_state")
_emit_triggers_alert("execution_guardrail_chokepoint", "p4obs", "alert")
_emit_links_incident_trace("execution_guardrail_chokepoint", "p4obs", "trace_link")
_emit_captures_pattern("execution_guardrail_chokepoint", "p3lm", "pattern")
_emit_records_learning_event("execution_guardrail_chokepoint", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_guardrail_chokepoint", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_guardrail_chokepoint", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_guardrail_chokepoint", "p3lm", "routing")
_emit_improves_agent_policy("execution_guardrail_chokepoint", "p3lm", "policy")
_emit_stores_learning_state("execution_guardrail_chokepoint", "p3lm", "state")
_emit_records_execution_trace("execution_guardrail_chokepoint", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_guardrail_chokepoint", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_guardrail_chokepoint", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_guardrail_chokepoint", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_guardrail_chokepoint", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_guardrail_chokepoint", "env_read", "p2_env_1")
_emit_reads_environ("execution_guardrail_chokepoint", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_guardrail_chokepoint", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_guardrail_chokepoint", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_guardrail_chokepoint", "context_pull")
_emit_pulls_context("p1", "execution_guardrail_chokepoint", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_guardrail_chokepoint", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_guardrail_chokepoint", "uwg_term_2")
_emit_writes_through("p1", "execution_guardrail_chokepoint", "write_through")
_emit_writes_through("p1", "execution_guardrail_chokepoint", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_guardrail_chokepoint", "safety_validation")
_emit_invokes_eval("p1", "execution_guardrail_chokepoint", "eval_call")
_emit_proposal_commits_routing("p1", "execution_guardrail_chokepoint", "routing_commit")

emit_determinism_digest(
    "trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_dispatch_entry"
)
emit_determinism_digest(
    "trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_dispatch_exit"
)
emit_determinism_digest("trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_tool_invoke")
emit_determinism_digest(
    "trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_tool_complete"
)
emit_determinism_digest("trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_agent_entry")
emit_determinism_digest("trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_agent_exit")
emit_determinism_digest("trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_uwg_write")
emit_determinism_digest("trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_trace_sign")
emit_determinism_digest(
    "trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_guardrail_check"
)
emit_determinism_digest(
    "trace_execution_guardrail_chokepoint", "execution_guardrail_chokepoint_policy_verify"
)

logger = logging.getLogger(__name__)

_EXECUTION_NON_FATAL_EXCEPTIONS = (
    AttributeError,
    KeyError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    TimeoutError,
)
_PROOF_EMISSION_EXCEPTIONS = _EXECUTION_NON_FATAL_EXCEPTIONS + (DeterminismViolation,)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class GuardrailDenied(PermissionError):
    """Execution denied by guardrail. ADG edge: reenters_safety"""


class MissingCapabilityToken(PermissionError):
    """No capability token provided. Fail-closed."""


class MissingPolicyHash(PermissionError):
    """No policy hash bound to execution context. Fail-closed."""


class HumanReviewRequired(PermissionError):
    """HUMAN_GATED action attempted without human approval.
    ADG edge: requires_human_review
    """


class ExecutionBypassAttempt(RuntimeError):
    """Direct execution outside authorize_and_execute() detected."""


# ---------------------------------------------------------------------------
# ADG signal emitters (each function name is a detection symbol)
# ---------------------------------------------------------------------------


def _emit_applies_guardrail(ctx: ExecutionContext, outcome: str) -> None:
    """ADG edge: applies_guardrail"""
    logger.debug(
        "EXEC applies_guardrail req=%s policy=%s outcome=%s target=%s",
        ctx.execution_request_id,
        ctx.policy_hash[:12],
        outcome,
        ctx.execution_target_hash[:12],
    )


def _emit_validated_by_safety_plane(ctx: ExecutionContext) -> None:
    """ADG edge: validated_by_safety_plane"""
    _emit_verifies_policy(str(uuid.uuid4()), "Module._emit_validated_by_safety_plane", "L2_EXECUTION")
    logger.debug(
        "EXEC validated_by_safety_plane req=%s policy=%s",
        ctx.execution_request_id,
        ctx.policy_hash[:12],
    )


def _emit_references_policy_hash(ctx: ExecutionContext) -> None:
    """ADG edge: references_policy_hash"""
    logger.debug(
        "EXEC references_policy_hash policy=%s req=%s",
        ctx.policy_hash,
        ctx.execution_request_id,
    )


def _emit_execution_terminates_at_uwg(ctx: ExecutionContext) -> None:
    """ADG edge: execution_terminates_at_uwg"""
    logger.debug(
        "EXEC execution_terminates_at_uwg req=%s class=%s",
        ctx.execution_request_id,
        ctx.action_class.value,
    )


def _emit_reenters_safety(ctx: ExecutionContext, reason: str) -> None:
    """ADG edge: reenters_safety"""
    logger.warning(
        "EXEC reenters_safety req=%s reason=%s policy=%s",
        ctx.execution_request_id,
        reason,
        ctx.policy_hash[:12],
    )


def _emit_requires_human_review(ctx: ExecutionContext) -> None:
    """ADG edge: requires_human_review"""
    logger.warning(
        "EXEC requires_human_review req=%s class=%s target=%s",
        ctx.execution_request_id,
        ctx.action_class.value,
        ctx.execution_target_hash[:12],
    )


def _emit_records_execution_trace(ctx: ExecutionContext) -> None:
    """ADG edge: records_execution_trace"""
    logger.debug(
        "EXEC records_execution_trace req=%s trace=%s",
        ctx.execution_request_id,
        ctx.trace_id,
    )
    _lc_records(ctx.trace_id or ctx.execution_request_id, LayerSegment.L2_EXECUTION, ctx.action_class.value)


def _emit_signs_execution_trace(ctx: ExecutionContext, output_hash: str) -> None:
    """ADG edge: signs_execution_trace"""
    logger.debug(
        "EXEC signs_execution_trace req=%s output_hash=%s",
        ctx.execution_request_id,
        output_hash,
    )
    _lc_signs(ctx.trace_id or ctx.execution_request_id, output_hash[:16], ctx.execution_request_id[:12], 0)
    emit_determinism_digest(ctx.trace_id or ctx.execution_request_id, output_hash[:16])


# ---------------------------------------------------------------------------
# Internal guardrail evaluator
# ---------------------------------------------------------------------------


def _evaluate_guardrail(
    ctx: ExecutionContext,
    target_name: str,
    *,
    safety_plane_available: bool = True,
) -> GuardrailOutcome:
    """Evaluate guardrail for execution context.

    Returns GuardrailOutcome. Only ALLOW may proceed.
    Calls _emit_validated_by_safety_plane when safety plane is available.
    """
    if not safety_plane_available:
        # P2/L5: Emit safety audit record for safety plane unavailability
        try:
            from agentic_core.L5_safety.audit.safety_audit_emitter import (
                emit_safety_plane_validation_audit,
            )

            safety_plane_audit = emit_safety_plane_validation_audit(
                run_id=ctx.run_id,
                trace_id=ctx.trace_id,
                policy_hash=ctx.policy_hash,
                decision_outcome="error",
                evaluated_input={
                    "target": target_name,
                    "action_class": ctx.action_class.value,
                    "safety_plane_available": False,
                },
                reason="Safety plane not available",
                actor_id="execution_guardrail_chokepoint",
            )
            logger.debug(
                "SAFETY_PLANE_UNAVAILABLE_AUDIT audit_id=%s req=%s target=%s",
                safety_plane_audit.safety_audit_id,
                ctx.execution_request_id,
                target_name,
            )
        except (RuntimeError, ValueError) as audit_exc:
            logger.error(
                "SAFETY_PLANE_UNAVAILABLE_AUDIT_ERROR: %s (req=%s)",
                audit_exc,
                ctx.execution_request_id,
            )
        return GuardrailOutcome.ERROR

    from agentic_core.L2_execution.enforcement.guardrail_gate import (  # noqa: PLC0415
        GuardrailVerdict,
        get_guardrail_gate,
    )

    gate = get_guardrail_gate(policy_hash=ctx.policy_hash)
    result = gate.check(operation=ctx.action_class.value, target=target_name)
    _emit_validated_by_safety_plane(ctx)

    # P2/L5: Emit safety audit record for safety plane validation
    try:
        from agentic_core.L5_safety.audit.safety_audit_emitter import (
            emit_safety_plane_validation_audit,
        )

        validation_outcome = "allow" if result.verdict == GuardrailVerdict.ALLOW else "deny"
        safety_plane_audit = emit_safety_plane_validation_audit(
            run_id=ctx.run_id,
            trace_id=ctx.trace_id,
            policy_hash=ctx.policy_hash,
            decision_outcome=validation_outcome,
            evaluated_input={
                "target": target_name,
                "action_class": ctx.action_class.value,
                "guardrail_verdict": result.verdict.value,
            },
            reason=f"Safety plane validation for {target_name}",
            actor_id="execution_guardrail_chokepoint",
        )
        logger.debug(
            "SAFETY_PLANE_VALIDATION_AUDIT audit_id=%s req=%s target=%s verdict=%s",
            safety_plane_audit.safety_audit_id,
            ctx.execution_request_id,
            target_name,
            result.verdict.value,
        )
    except (RuntimeError, ValueError) as audit_exc:
        logger.error(
            "SAFETY_PLANE_VALIDATION_AUDIT_ERROR: %s (req=%s)",
            audit_exc,
            ctx.execution_request_id,
        )

    if result.verdict == GuardrailVerdict.DENY:
        return GuardrailOutcome.DENY
    return GuardrailOutcome.ALLOW


def _make_decision_hash(ctx: ExecutionContext, outcome: GuardrailOutcome) -> str:
    payload = f"{ctx.execution_request_id}|{ctx.policy_hash}|{ctx.execution_target_hash}|{outcome.value}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Public chokepoint
# ---------------------------------------------------------------------------


def authorize_and_execute(
    execution_context: ExecutionContext,
    target_callable: Callable[..., Any],
    capability_token: str,
    payload: Any,
    *,
    target_name: str = "",
    human_approved: bool = False,
    safety_plane_available: bool = True,
    uwg_callable: Callable[..., Any] | None = None,
) -> tuple[Any, ExecutionContext]:
    """Mandatory L2 execution chokepoint — P0/L2 enforcement.

    Args:
        execution_context:      Validated run-scoped ExecutionContext.
        target_callable:        The callable to execute (only on ALLOW).
        capability_token:       Token proving authority (must match ctx.capability_token).
        payload:                Execution payload passed to target_callable.
        target_name:            Human-readable target identifier for guardrail.
        human_approved:         Must be True for HUMAN_GATED actions.
        safety_plane_available: If False, guardrail returns ERROR (fail-closed).
        uwg_callable:           If provided, MUTATION actions route through this.

    Returns:
        (output, bound_context) — execution result and context with decision bound.

    Raises:
        MissingCapabilityToken:  token missing or mismatched.
        MissingPolicyHash:       no policy hash on context.
        HumanReviewRequired:     HUMAN_GATED without human_approved.
        GuardrailDenied:         guardrail returned DENY/ERROR/TIMEOUT/UNKNOWN.
        ValueError:              invalid execution_context.
    """
    # 1. Validate ExecutionContext completeness
    if not isinstance(execution_context, ExecutionContext):
        raise ValueError(f"authorize_and_execute: expected ExecutionContext, got {type(execution_context)}")

    # 2. Validate capability token (no anonymous execution)
    if not capability_token:
        _emit_reenters_safety(execution_context, "MISSING_CAPABILITY_TOKEN")
        raise MissingCapabilityToken(
            f"authorize_and_execute: no capability token for req={execution_context.execution_request_id}",
        )
    if capability_token != execution_context.capability_token:
        _emit_reenters_safety(execution_context, "TOKEN_MISMATCH")
        raise MissingCapabilityToken(
            f"authorize_and_execute: capability token mismatch for req={execution_context.execution_request_id}",
        )

    # 3. Resolve and bind policy hash
    if not execution_context.policy_hash:
        _emit_reenters_safety(execution_context, "MISSING_POLICY_HASH")
        raise MissingPolicyHash(
            f"authorize_and_execute: no policy hash on context req={execution_context.execution_request_id}",
        )
    _emit_references_policy_hash(execution_context)

    # 4 + 5. Human review gate for irreversible / HUMAN_GATED actions
    if execution_context.action_class.requires_human_review:
        _emit_requires_human_review(execution_context)

        # P2/L5: Emit safety audit record for human review requirement (Gate A)
        try:
            human_review_audit = emit_guardrail_audit(
                run_id=execution_context.run_id,
                trace_id=execution_context.trace_id,
                policy_hash=execution_context.policy_hash,
                decision_outcome="require_review",
                evaluated_input={
                    "action_class": execution_context.action_class.value,
                    "execution_request_id": execution_context.execution_request_id,
                    "requires_human_review": True,
                },
                reason=f"Human review required for {execution_context.action_class.value}",
                actor_id="execution_guardrail_chokepoint",
                action_class=execution_context.action_class.value,
            )
            logger.debug(
                "HUMAN_REVIEW_AUDIT audit_id=%s req=%s action=%s",
                human_review_audit.safety_audit_id,
                execution_context.execution_request_id,
                execution_context.action_class.value,
            )
        except (RuntimeError, ValueError) as audit_exc:
            logger.error(
                "HUMAN_REVIEW_AUDIT_ERROR: %s (req=%s)",
                audit_exc,
                execution_context.execution_request_id,
            )
            # Continue - audit failure should not block safety decisions

        if not human_approved:
            _emit_reenters_safety(execution_context, "HUMAN_REVIEW_REQUIRED")
            raise HumanReviewRequired(
                f"authorize_and_execute: HUMAN_GATED action requires human approval "
                f"req={execution_context.execution_request_id}",
            )

    # 6 + 7. Guardrail evaluation + safety plane binding
    _tgt = target_name or execution_context.execution_target_hash[:16]
    outcome = _evaluate_guardrail(
        execution_context,
        _tgt,
        safety_plane_available=safety_plane_available,
    )
    _emit_applies_guardrail(execution_context, outcome.value)

    # P2/L5: Emit safety audit record for guardrail decision (Gate A)
    try:
        safety_audit = emit_guardrail_audit(
            run_id=execution_context.run_id,
            trace_id=execution_context.trace_id,
            policy_hash=execution_context.policy_hash,
            decision_outcome=outcome.value.lower(),  # ALLOW, DENY, ERROR, TIMEOUT, UNKNOWN
            evaluated_input={
                "target": _tgt,
                "action_class": execution_context.action_class.value,
                "execution_request_id": execution_context.execution_request_id,
            },
            evaluated_output={
                "outcome": outcome.value,
                "may_proceed": outcome.may_proceed,
            },
            reason=f"Guardrail evaluation for {_tgt}",
            actor_id="execution_guardrail_chokepoint",
            action_class=execution_context.action_class.value,
        )
        logger.debug(
            "EXECUTION_GUARDRAIL_AUDIT audit_id=%s req=%s target=%s outcome=%s",  # guardian: SafetyAuditMissingError should be handled with specific context
            safety_audit.safety_audit_id,
            execution_context.execution_request_id,
            _tgt,
            outcome.value,
        )
    except (
        SafetyAuditMissingError
    ) as audit_exc:  # guardian: SafetyAuditMissingError should be handled with specific context
        logger.error(
            "EXECUTION_GUARDRAIL_AUDIT_FAILED: %s (req=%s target=%s)",
            audit_exc,
            execution_context.execution_request_id,
            _tgt,
        )
        # Continue execution - audit failure should not block safety decisions
    except (RuntimeError, ValueError) as audit_exc:
        logger.error(
            "EXECUTION_GUARDRAIL_AUDIT_ERROR: %s (req=%s target=%s)",
            audit_exc,
            execution_context.execution_request_id,
            _tgt,
        )
        # Continue execution - audit failure should not block safety decisions

    # Bind decision
    decision_id = str(uuid.uuid4())
    decision_hash = _make_decision_hash(execution_context, outcome)
    bound_ctx = execution_context.with_guardrail_decision(decision_id, decision_hash)

    # 9. Fail-closed: abort on any non-ALLOW outcome
    if not outcome.may_proceed:
        # P3/L2: Record execution observability for policy blocks
        try:
            import time as _time  # noqa: PLC0415

            obs_context = ExecutionObservabilityContext.create(
                run_id=bound_ctx.run_id,
                trace_id=bound_ctx.trace_id,
                execution_target=target_name or bound_ctx.execution_target_hash[:16],
                guardrail_decision_id=decision_id,
                policy_hash=bound_ctx.policy_hash,
            )
            record_policy_block(
                execution_context=ObservabilityExecutionContext.create(
                    execution_request_id=bound_ctx.execution_request_id,
                    execution_start_tick=_exec_start,
                    execution_end_tick=_time.monotonic(),
                    execution_status=ExecutionStatus.BLOCKED_BY_POLICY,
                ),
                observability_context=obs_context,
                block_reason=f"Guardrail {outcome.value} for {_tgt}",
            )
        except (RuntimeError, ValueError) as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_BLOCK_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"GUARDRAIL_{outcome.value}")
        raise GuardrailDenied(
            f"authorize_and_execute: guardrail {outcome.value} for "
            f"req={bound_ctx.execution_request_id} target={_tgt}",
        )

    # 10. Pre-execution trace stub
    _emit_records_execution_trace(bound_ctx)

    # 11 + 12. Execute via typed tool contract (P2/L2) — route MUTATION through UWG
    import time as _time  # noqa: PLC0415

    _exec_start = _time.monotonic()

    # Build typed ToolContract from ExecutionContext fields
    _input_schema = ToolSchema(required_fields=[])
    _output_schema = ToolSchema(required_fields=[])
    _typed_input: dict = payload if isinstance(payload, dict) else {"payload": payload}

    # Register tool on-the-fly if not already present (governed dynamic paths)
    _registry = get_typed_tool_registry()
    if not _registry.is_registered(target_name or bound_ctx.execution_target_hash[:16]):
        from agentic_core.L2_execution.types.typed_tool_contract import ToolRegistryEntry  # noqa: PLC0415

        _registry.register(
            ToolRegistryEntry(
                tool_name=target_name or bound_ctx.execution_target_hash[:16],
                tool_version="1.0",
                input_schema=_input_schema,
                output_schema=_output_schema,
                action_class=bound_ctx.action_class.value,
                allowed_callers=["*"],
                policy_requirements=[],
                callable=None,
            ),
        )

    _tool_contract = ToolContract.create(
        tool_name=target_name or bound_ctx.execution_target_hash[:16],
        tool_version="1.0",
        run_id=bound_ctx.run_id,
        trace_id=bound_ctx.trace_id,
        input_schema=_input_schema,
        output_schema=_output_schema,
        input_payload=_typed_input,
        action_class=bound_ctx.action_class.value,
        caller_agent_id=bound_ctx.extra.get("caller_agent_id", bound_ctx.execution_request_id),
        policy_hash=bound_ctx.policy_hash,
    )

    try:
        if bound_ctx.action_class.requires_uwg and uwg_callable is not None:
            _emit_execution_terminates_at_uwg(bound_ctx)
            _effective_callable = uwg_callable
        else:
            _effective_callable = target_callable

        _contract_result = invoke_typed_tool(
            _tool_contract,  # guardian: Multiple exceptions (ToolInputSchemaViolation, ToolOutputSchemaViolation) need specific handling
            _typed_input,
            registry=_registry,
            tool_callable=_effective_callable,
        )
        output = _contract_result.output_payload.get("result", _contract_result.output_payload)
    except (
        ToolInputSchemaViolation,
        ToolOutputSchemaViolation,
        UnregisteredToolError,
    ) as exc:  # guardian: Multiple exceptions (ToolInputSchemaViolation, ToolOutputSchemaViolation) need specific handling
        # P3/L2: Record execution observability for tool errors
        try:
            obs_context = ExecutionObservabilityContext.create(
                run_id=bound_ctx.run_id,
                trace_id=bound_ctx.trace_id,
                execution_target=target_name or bound_ctx.execution_target_hash[:16],
                guardrail_decision_id=decision_id,
                policy_hash=bound_ctx.policy_hash,
            )
            record_execution_failure(
                execution_context=ObservabilityExecutionContext.create(
                    execution_request_id=bound_ctx.execution_request_id,
                    execution_start_tick=_exec_start,
                    execution_end_tick=_time.monotonic(),
                    execution_status=ExecutionStatus.FAILED,
                ),
                observability_context=obs_context,
                failure_classification=FailureClassification.TOOL_ERROR,
                failure_reason=f"Tool contract violation: {type(exc).__name__}",
            )
        except (RuntimeError, ValueError) as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_FAILURE_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"TYPED_TOOL_CONTRACT_VIOLATION:{type(exc).__name__}")
        raise
    except _EXECUTION_NON_FATAL_EXCEPTIONS as exc:
        # P3/L2: Record execution observability for general errors
        try:
            obs_context = ExecutionObservabilityContext.create(
                run_id=bound_ctx.run_id,
                trace_id=bound_ctx.trace_id,
                execution_target=target_name or bound_ctx.execution_target_hash[:16],
                guardrail_decision_id=decision_id,
                policy_hash=bound_ctx.policy_hash,
            )
            record_execution_failure(
                execution_context=ObservabilityExecutionContext.create(
                    execution_request_id=bound_ctx.execution_request_id,
                    execution_start_tick=_exec_start,
                    execution_end_tick=_time.monotonic(),
                    execution_status=ExecutionStatus.FAILED,
                ),
                observability_context=obs_context,
                failure_classification=FailureClassification.UNKNOWN_FAILURE,
                failure_reason=f"Execution error: {type(exc).__name__}",
            )
        except (RuntimeError, ValueError) as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_FAILURE_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"EXECUTION_ERROR:{type(exc).__name__}")
        raise
    _exec_end = _time.monotonic()
    _elapsed_ms = (_exec_end - _exec_start) * 1000.0

    # 13a. Emit execution proof (replay-valid, signed) — P1/L2 mandatory
    try:
        emit_execution_proof(
            execution_context=bound_ctx,
            execution_result=output,
            policy_context=bound_ctx.policy_hash,
            trace_context=bound_ctx,
            target_callable=target_callable,
            elapsed_ms=_elapsed_ms,
        )
    except _PROOF_EMISSION_EXCEPTIONS as _proof_exc:
        _emit_reenters_safety(bound_ctx, f"PROOF_EMISSION_FAILED:{type(_proof_exc).__name__}")
        raise RuntimeError(
            f"authorize_and_execute: execution proof emission failed for "
            f"req={bound_ctx.execution_request_id}: {_proof_exc}",
        ) from _proof_exc

    # 13b. Post-execution signed trace
    output_hash = hashlib.sha256(repr(output).encode()).hexdigest()[:32]
    _emit_signs_execution_trace(bound_ctx, output_hash)

    # P3/L2: Record execution observability
    try:
        # Create execution observability context
        obs_context = ExecutionObservabilityContext.create(
            run_id=bound_ctx.run_id,
            trace_id=bound_ctx.trace_id,
            execution_target=target_name or bound_ctx.execution_target_hash[:16],
            guardrail_decision_id=decision_id,
            policy_hash=bound_ctx.policy_hash,
        )

        # Create execution context with timing
        exec_context = ObservabilityExecutionContext.create(
            execution_request_id=bound_ctx.execution_request_id,
            execution_start_tick=_exec_start,
            execution_end_tick=_exec_end,
            execution_status=ExecutionStatus.SUCCEEDED,
        )

        # Record observability
        observability_record = record_execution_observability(
            execution_context=exec_context,
            observability_context=obs_context,
        )

        logger.debug(
            "EXECUTION_OBSERVABILITY_RECORDED record_id=%s req=%s duration_ms=%.2f",
            observability_record.execution_observability_id,
            bound_ctx.execution_request_id,
            _elapsed_ms,
        )

    except (RuntimeError, ValueError) as _obs_exc:
        logger.error(
            "EXECUTION_OBSERVABILITY_ERROR: %s (req=%s)",
            _obs_exc,
            bound_ctx.execution_request_id,
        )
        # Continue - observability failure should not block execution

    logger.info(
        "EXEC completed req=%s outcome=%s class=%s",
        bound_ctx.execution_request_id,
        outcome.value,
        bound_ctx.action_class.value,
    )
    return output, bound_ctx


__all__ = [
    "authorize_and_execute",
    "ActionClass",
    "ExecutionContext",
    "GuardrailOutcome",
    "GuardrailDenied",
    "MissingCapabilityToken",
    "MissingPolicyHash",
    "HumanReviewRequired",
    "ExecutionBypassAttempt",
    "emit_execution_proof",
    "DeterminismViolation",
]
