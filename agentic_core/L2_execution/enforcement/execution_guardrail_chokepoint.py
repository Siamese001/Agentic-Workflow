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

from agentic_core.L2_execution.context.execution_context import (
    ActionClass,
    ExecutionContext,
    GuardrailOutcome,
)
from agentic_core.L2_execution.contracts.typed_tool_contract import (
    ToolContract,
    ToolInputSchemaViolation,
    ToolOutputSchemaViolation,
    ToolSchema,
    UnregisteredToolError,
    get_typed_tool_registry,
    invoke_typed_tool,
)
from agentic_core.L2_execution.enforcement.execution_proof_contract import (
    DeterminismViolation,
    emit_execution_proof,
)
from agentic_core.L2_execution.observability.observability_recorder import (
    ExecutionContext,
    ExecutionObservabilityContext,
    ExecutionStatus,
    FailureClassification,
    record_execution_failure,
    record_execution_observability,
    record_policy_block,
)
from agentic_core.L5_safety.audit.safety_audit_emitter import (
    SafetyAuditMissingError,
    emit_guardrail_audit,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    emit_determinism_digest,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_records_execution_trace as _lc_records,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_signs_execution_trace as _lc_signs,
)

logger = logging.getLogger(__name__)


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
        except Exception as audit_exc:
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
    except Exception as audit_exc:
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
            f"authorize_and_execute: no capability token for req={execution_context.execution_request_id}"
        )
    if capability_token != execution_context.capability_token:
        _emit_reenters_safety(execution_context, "TOKEN_MISMATCH")
        raise MissingCapabilityToken(
            f"authorize_and_execute: capability token mismatch for req={execution_context.execution_request_id}"
        )

    # 3. Resolve and bind policy hash
    if not execution_context.policy_hash:
        _emit_reenters_safety(execution_context, "MISSING_POLICY_HASH")
        raise MissingPolicyHash(
            f"authorize_and_execute: no policy hash on context req={execution_context.execution_request_id}"
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
        except Exception as audit_exc:
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
                f"req={execution_context.execution_request_id}"
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
            "EXECUTION_GUARDRAIL_AUDIT audit_id=%s req=%s target=%s outcome=%s",
            safety_audit.safety_audit_id,
            execution_context.execution_request_id,
            _tgt,
            outcome.value,
        )
    except SafetyAuditMissingError as audit_exc:
        logger.error(
            "EXECUTION_GUARDRAIL_AUDIT_FAILED: %s (req=%s target=%s)",
            audit_exc,
            execution_context.execution_request_id,
            _tgt,
        )
        # Continue execution - audit failure should not block safety decisions
    except Exception as audit_exc:
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
            exec_context = ExecutionContext.create(
                execution_request_id=bound_ctx.execution_request_id,
                execution_start_tick=_time.monotonic(),  # Use current time as start
                execution_end_tick=_time.monotonic(),  # Immediate end for blocked
                execution_status=ExecutionStatus.BLOCKED_BY_POLICY,
            )
            record_policy_block(
                execution_context=exec_context,
                observability_context=obs_context,
                block_reason=f"Guardrail {outcome.value} for {_tgt}",
            )
        except Exception as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_BLOCK_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"GUARDRAIL_{outcome.value}")
        raise GuardrailDenied(
            f"authorize_and_execute: guardrail {outcome.value} for "
            f"req={bound_ctx.execution_request_id} target={_tgt}"
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
        from agentic_core.L2_execution.contracts.typed_tool_contract import ToolRegistryEntry  # noqa: PLC0415

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
            )
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
            _tool_contract,
            _typed_input,
            registry=_registry,
            tool_callable=_effective_callable,
        )
        output = _contract_result.output_payload.get("result", _contract_result.output_payload)
    except (ToolInputSchemaViolation, ToolOutputSchemaViolation, UnregisteredToolError) as exc:
        # P3/L2: Record execution observability for tool errors
        try:
            obs_context = ExecutionObservabilityContext.create(
                run_id=bound_ctx.run_id,
                trace_id=bound_ctx.trace_id,
                execution_target=target_name or bound_ctx.execution_target_hash[:16],
                guardrail_decision_id=decision_id,
                policy_hash=bound_ctx.policy_hash,
            )
            exec_context = ExecutionContext.create(
                execution_request_id=bound_ctx.execution_request_id,
                execution_start_tick=_exec_start,
                execution_end_tick=_time.monotonic(),
                execution_status=ExecutionStatus.FAILED,
                failure_classification=FailureClassification.TOOL_ERROR,
                failure_reason=f"Tool contract violation: {type(exc).__name__}",
            )
            record_execution_failure(
                execution_context=exec_context,
                observability_context=obs_context,
                failure_classification=FailureClassification.TOOL_ERROR,
                failure_reason=f"Tool contract violation: {type(exc).__name__}",
            )
        except Exception as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_FAILURE_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"TYPED_TOOL_CONTRACT_VIOLATION:{type(exc).__name__}")
        raise
    except Exception as exc:
        # P3/L2: Record execution observability for general errors
        try:
            obs_context = ExecutionObservabilityContext.create(
                run_id=bound_ctx.run_id,
                trace_id=bound_ctx.trace_id,
                execution_target=target_name or bound_ctx.execution_target_hash[:16],
                guardrail_decision_id=decision_id,
                policy_hash=bound_ctx.policy_hash,
            )
            exec_context = ExecutionContext.create(
                execution_request_id=bound_ctx.execution_request_id,
                execution_start_tick=_exec_start,
                execution_end_tick=_time.monotonic(),
                execution_status=ExecutionStatus.FAILED,
                failure_classification=FailureClassification.UNKNOWN_FAILURE,
                failure_reason=f"Execution error: {type(exc).__name__}",
            )
            record_execution_failure(
                execution_context=exec_context,
                observability_context=obs_context,
                failure_classification=FailureClassification.UNKNOWN_FAILURE,
                failure_reason=f"Execution error: {type(exc).__name__}",
            )
        except Exception as _obs_exc:
            logger.error("EXECUTION_OBSERVABILITY_FAILURE_ERROR: %s", _obs_exc)

        _emit_reenters_safety(bound_ctx, f"EXECUTION_ERROR:{type(exc).__name__}")
        raise
    _elapsed_ms = (_time.monotonic() - _exec_start) * 1000.0

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
    except Exception as _proof_exc:  # guardian: allow-silent-swallow
        _emit_reenters_safety(bound_ctx, f"PROOF_EMISSION_FAILED:{type(_proof_exc).__name__}")
        raise RuntimeError(
            f"authorize_and_execute: execution proof emission failed for "
            f"req={bound_ctx.execution_request_id}: {_proof_exc}"
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
        exec_context = ExecutionContext.create(
            execution_request_id=bound_ctx.execution_request_id,
            execution_start_tick=_exec_start,
            execution_end_tick=_exec_start + (_elapsed_ms / 1000.0),
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

    except Exception as _obs_exc:
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
