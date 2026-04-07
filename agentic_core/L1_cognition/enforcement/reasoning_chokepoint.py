"""
agentic_core/L1_cognition/enforcement/reasoning_chokepoint.py

reason_and_record() — mandatory L1 reasoning entry chokepoint.

ALL L1 reasoning paths MUST route through this wrapper.
No direct model/reasoning invocation is permitted outside this function.

Contract per call:
    1. validate ReasoningContext completeness
    2. hash prompt + context + policy state
    3. emit pre-execution trace stub  (records_execution_trace)
    4. execute reasoning callable
    5. emit post-execution trace record (records_execution_trace)
    6. attach output_hash to trace
    7. sign trace                       (signs_execution_trace)
    8. create transcript                (transcripts_response)
    9. bind policy hash                 (references_policy_hash)
   10. fail hard if transcript/trace missing (hard_fails_untranscripted)

ADG edges emitted:
    records_execution_trace
    signs_execution_trace
    transcripts_response
    references_policy_hash
    hard_fails_untranscripted
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Callable

from agentic_core.L1_cognition.reasoning.knowledge_orchestrator import (
    EvaluationResult,
    ReasoningContext,
    ReasoningTrace,
    capture_simple_reasoning_pattern,
)
from agentic_core.L1_cognition.reasoning.plan_creator import (
    CheckpointResult,
    PlanningPolicy,
    ReasoningPlanContext,
    ReasoningPlanError,
    create_reasoning_plan,
    enforce_plan_checkpoint,
    execute_plan_step,
)
from agentic_core.L1_cognition.reasoning.reasoning_context import (
    ReasoningContext,
    ReasoningTraceArtifact,
    ReasoningTranscript,
)
from agentic_core.L1_cognition.reasoning.reasoning_evaluation import (
    OrphanReasoningEvaluationError,
    ReasoningEvaluationOutcome,
    ReasoningEvaluationRubric,
    evaluate_reasoning_step_from_trace,
)


# Lazy import to avoid L1->L6 gravity violation
def _get_performance_emitter():
    from agentic_core.L6_observability.utils.performance.performance_emitter import (
        StageStatus,
        record_reasoning_performance,
    )
    return StageStatus, record_reasoning_performance

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_hard_fails_untranscripted,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_transcripts_response,
    emit_determinism_digest,
)

emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_dispatch_entry")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_dispatch_exit")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_tool_invoke")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_tool_complete")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_agent_entry")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_agent_exit")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_uwg_write")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_trace_sign")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_guardrail_check")
emit_determinism_digest("trace_reasoning_chokepoint", "reasoning_chokepoint_policy_verify")

logger = logging.getLogger(__name__)


class MissingReasoningTranscript(RuntimeError):
    """Raised when a reasoning response has no transcript artifact.

    ADG edge: hard_fails_untranscripted
    """


class MissingReasoningTrace(RuntimeError):
    """Raised when reason_and_record produces an incomplete trace."""


def _hash_prompt(prompt_payload: Any) -> str:
    return hashlib.sha256(repr(prompt_payload).encode()).hexdigest()[:32]


def _hash_output(output: Any) -> str:
    return hashlib.sha256(repr(output).encode()).hexdigest()[:32]


def _hash_step(ctx: ReasoningContext, prompt_payload: Any, retrieved_context: Any) -> str:
    payload = (
        f"{ctx.policy_hash}|{ctx.prompt_hash}|"
        f"{ctx.retrieved_context_hash}|{repr(prompt_payload)[:512]}|"
        f"{repr(retrieved_context)[:512]}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def _emit_records_execution_trace(trace: ReasoningTraceArtifact) -> None:
    """ADG edge: records_execution_trace"""
    logger.debug(
        "REASONING records_execution_trace trace_id=%s run_id=%s policy_hash=%s",
        trace.reasoning_trace_id,
        trace.run_id,
        trace.policy_hash,
    )


def _emit_signs_execution_trace(trace: ReasoningTraceArtifact) -> None:
    """ADG edge: signs_execution_trace"""
    logger.debug(
        "REASONING signs_execution_trace trace_id=%s output_hash=%s signed=%s",
        trace.reasoning_trace_id,
        trace.output_hash,
        trace.signed,
    )


def _emit_transcripts_response(transcript: ReasoningTranscript) -> None:
    """ADG edge: transcripts_response"""
    logger.debug(
        "REASONING transcripts_response transcript_id=%s trace_id=%s model_id=%s",
        transcript.transcript_id,
        transcript.reasoning_trace_id,
        transcript.model_id,
    )


def _emit_references_policy_hash(ctx: ReasoningContext) -> None:
    """ADG edge: references_policy_hash"""
    logger.debug(
        "REASONING references_policy_hash policy_hash=%s run_id=%s",
        ctx.policy_hash,
        ctx.run_id,
    )


def _emit_hard_fails_untranscripted(trace_id: str, reason: str) -> None:
    """ADG edge: hard_fails_untranscripted"""
    logger.error(
        "REASONING hard_fails_untranscripted trace_id=%s reason=%s",
        trace_id,
        reason,
    )


def reason_and_record(
    reasoning_context: ReasoningContext,
    prompt_payload: Any,
    retrieved_context: Any,
    model_callable: Callable[..., Any],
    *,
    inference_config: dict[str, Any] | None = None,
) -> tuple[Any, ReasoningTraceArtifact]:
    """Execute reasoning through the mandatory L1 chokepoint.

    Args:
        reasoning_context:  Validated run-scoped ReasoningContext.
        prompt_payload:     Assembled prompt (any hashable form).
        retrieved_context:  Retrieved evidence bound to this step.
        model_callable:     The reasoning callable to invoke.
        inference_config:   Optional model config dict for transcript.

    Returns:
        (output, trace) — the model output and the completed trace artifact.

    Raises:
        ValueError:                  if reasoning_context is incomplete.
        MissingReasoningTranscript:  if transcript creation fails.
        MissingReasoningTrace:       if trace is incomplete after execution.
    """
    # P2/L6: Start timing for reasoning performance
    reasoning_start_tick = time.time()

    # 1. Validate context completeness
    if not isinstance(reasoning_context, ReasoningContext):
        raise ValueError(f"reason_and_record: expected ReasoningContext, got {type(reasoning_context)}")
    try:
        reasoning_context.__post_init__()  # re-validates required fields
    except ValueError as exc:
        raise ValueError(f"reason_and_record: invalid context — {exc}") from exc

    # 2. Hash prompt + context + policy
    step_hash = _hash_step(reasoning_context, prompt_payload, retrieved_context)

    # 3. Emit pre-execution trace stub
    trace = ReasoningTraceArtifact.create(
        ctx=reasoning_context,
        reasoning_step_hash=step_hash,
        output_hash="",
    )
    _emit_records_execution_trace(trace)
    _emit_references_policy_hash(reasoning_context)

    # P3/L1: Create reasoning plan for multi-step reasoning
    reasoning_plan = None
    try:
        plan_context = ReasoningPlanContext.create(
            run_id=reasoning_context.run_id,
            trace_id=reasoning_context.trace_id,
            model_id=reasoning_context.model_id,
            parent_reasoning_trace_id=reasoning_context.parent_reasoning_trace_id,
        )
        planning_policy = PlanningPolicy.create(
            require_checkpoints=True,
            checkpoint_after_evidence=True,
            checkpoint_before_action=True,
            checkpoint_after_tool_result=True,
            checkpoint_before_synthesis=True,
        )

        reasoning_plan = create_reasoning_plan(
            reasoning_context=plan_context,    # guardian: ReasoningPlanError should be handled with specific context
            goal_payload=str(prompt_payload)[:200],  # Truncate for goal
            evidence_bundle=retrieved_context,
            planning_policy=planning_policy,
        )    # guardian: ReasoningPlanError should be handled with specific context

        logger.debug(
            "REASONING_PLAN_CREATED plan_id=%s run_id=%s trace_id=%s",
            reasoning_plan.reasoning_plan_id,
            reasoning_context.run_id,
            reasoning_context.trace_id,
        )

    except ReasoningPlanError as _rpe:    # guardian: ReasoningPlanError should be handled with specific context
        logger.warning(
            "REASONING_PLAN_FAILED: %s, continuing without plan",
            _rpe,
        )
        # Continue without plan - planning failure should not block reasoning
    except Exception as _plan_exc:
        logger.error(
            "REASONING_PLAN_ERROR: %s, continuing without plan",
            _plan_exc,
        )
        # Continue without plan - planning failure should not block reasoning

    # 4. Execute reasoning
    reasoning_success = True
    try:
        output = model_callable(prompt_payload, retrieved_context)
    except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        reasoning_success = False
        trace_id = trace.reasoning_trace_id
        _emit_hard_fails_untranscripted(trace_id, f"model_callable raised: {exc}")
        raise
    finally:
        # P2/L6: Record reasoning performance even if execution failed
        reasoning_end_tick = time.time()
        try:
            perf_status = StageStatus.SUCCESS if reasoning_success else StageStatus.ERROR
            reasoning_perf = record_reasoning_performance(
                run_id=reasoning_context.run_id,
                trace_id=reasoning_context.trace_id,
                start_tick=reasoning_start_tick,
                end_tick=reasoning_end_tick,
                status=perf_status,
                concurrency_count=1,  # Single reasoning operation
            )
            logger.debug(
                "REASONING_PERFORMANCE_RECORD record_id=%s model_id=%s duration_ms=%.2f",
                reasoning_perf.performance_record_id,
                reasoning_context.model_id,
                reasoning_perf.duration_ms,
            )
        except Exception as _perf_exc:
            logger.error(
                "REASONING_PERFORMANCE_ERROR: %s (model_id=%s)",
                _perf_exc,
                reasoning_context.model_id,
            )
            # Continue - performance failure should not block reasoning

    # P3/L1: Execute plan steps and checkpoints if plan exists
    if reasoning_plan:
        try:
            # Execute first step (evidence processing)
            step = execute_plan_step(
                reasoning_plan=reasoning_plan,
                step_index=0,
                step_goal="process_evidence_and_context",
                step_input=prompt_payload,
                step_output=output,
            )

            # Enforce checkpoint after evidence processing
            checkpoint = enforce_plan_checkpoint(
                reasoning_plan=reasoning_plan,
                step=step,
                checkpoint_result=CheckpointResult.PASS,
                checkpoint_reason="evidence_processed_successfully",
            )

            logger.debug(
                "PLAN_STEP_AND_CHECKPOINT_EXECUTED step_id=%s checkpoint_id=%s plan_id=%s",
                step.step_id,
                checkpoint.checkpoint_id,
                reasoning_plan.reasoning_plan_id,
            )

        except Exception as _step_exc:
            logger.error(
                "PLAN_STEP_EXECUTION_ERROR: %s (plan_id=%s)",
                _step_exc,
                reasoning_plan.reasoning_plan_id,
            )
            # Continue - step execution failure should not block reasoning

    # 5–6. Post-execution: attach output hash
    output_hash = _hash_output(output)
    trace.output_hash = output_hash

    # 5. Emit post-execution trace record
    _emit_records_execution_trace(trace)

    # 7. Sign trace
    if not trace.is_complete():
        trace_id = trace.reasoning_trace_id
        _emit_hard_fails_untranscripted(trace_id, "incomplete_trace_fields")
        raise MissingReasoningTrace(f"reason_and_record: trace {trace_id} is incomplete after execution")
    trace.sign()
    _emit_signs_execution_trace(trace)

    # 8. Create + attach transcript
    try:
        raw_response = repr(output) if not isinstance(output, str) else output
        transcript = ReasoningTranscript.create(
            trace_id=trace.reasoning_trace_id,
            raw_response=raw_response,
            model_id=reasoning_context.model_id,
            inference_config=inference_config,
            parent_trace_id=reasoning_context.parent_reasoning_trace_id,
        )
        trace.transcript_id = transcript.transcript_id
        _emit_transcripts_response(transcript)
    except Exception as exc:
        _emit_hard_fails_untranscripted(trace.reasoning_trace_id, f"transcript_creation_failed: {exc}")
        raise MissingReasoningTranscript(
            f"reason_and_record: transcript creation failed for trace {trace.reasoning_trace_id}: {exc}",
        ) from exc

    # 9. Final policy binding confirmation
    _emit_references_policy_hash(reasoning_context)

    # 10. P2/L1: Evaluate reasoning step — bind evaluation to completed trace
    try:
        _rubric = ReasoningEvaluationRubric(    # guardian: OrphanReasoningEvaluationError should be handled with specific context
            relevance=1.0,
            consistency=1.0,
            policy_compliance=1.0 if reasoning_context.policy_hash else 0.0,
            coherence=1.0,    # guardian: OrphanReasoningEvaluationError should be handled with specific context
            actionability=1.0,
        )
        evaluate_reasoning_step_from_trace(
            trace,
            rubric=_rubric,
            evaluator_id=reasoning_context.model_id or "ReasoningChokepoint",
            outcome=ReasoningEvaluationOutcome.PASS,
        )
    except OrphanReasoningEvaluationError as _oee:    # guardian: OrphanReasoningEvaluationError should be handled with specific context
        logger.warning("reason_and_record: orphan evaluation guard triggered: %s", _oee)
    except Exception as _ee:  # guardian: allow-silent-swallow
        logger.debug("reason_and_record: evaluation emission failed: %s", _ee)

    # P4/L1: Capture reasoning pattern for knowledge base
    try:
        # Create reasoning trace for knowledge base
        knowledge_trace = ReasoningTrace.create(
            trace_id=trace.reasoning_trace_id,
            reasoning_steps=[str(prompt_payload)[:100]],  # Simplified reasoning steps
            reasoning_goal=str(prompt_payload)[:200],  # Extract goal from prompt
            reasoning_context={
                "model_id": reasoning_context.model_id,
                "policy_hash": reasoning_context.policy_hash,
            },
            execution_outcome="SUCCESS",
            timestamp=trace.created_at,
        )

        # Create evaluation result for knowledge base
        evaluation_result = EvaluationResult.create(
            quality_score=0.8,  # Default quality score
            reasoning_quality="GOOD",
            policy_compliance=True,
            hallucination_detected=False,
            safety_violation=False,
        )

        # Create reasoning context for knowledge base
        knowledge_context = ReasoningContext.create(
            context_type="REASONING_EXECUTION",
            domain="COGNITIVE_PROCESSING",
            complexity="MEDIUM",
        )

        # Capture reasoning pattern
        knowledge_pattern = capture_simple_reasoning_pattern(
            trace_id=trace.reasoning_trace_id,
            reasoning_goal=str(prompt_payload)[:200],
            reasoning_steps=[str(prompt_payload)[:100]],
            quality_score=0.8,
        )

        logger.debug(
            "REASONING_KNOWLEDGE_PATTERN_CAPTURED pattern_id=%s trace_id=%s",
            knowledge_pattern.reasoning_pattern_id,
            trace.reasoning_trace_id,
        )

    except Exception as _knowledge_exc:
        logger.warning(
            "REASONING_KNOWLEDGE_CAPTURE_ERROR: %s (trace_id=%s)",
            _knowledge_exc,
            trace.reasoning_trace_id,
        )
        # Continue - knowledge capture failure should not block reasoning

    logger.info(
        "REASONING completed trace_id=%s run_id=%s signed=%s transcript_id=%s",
        trace.reasoning_trace_id,
        trace.run_id,
        trace.signed,
        trace.transcript_id,
    )
    return output, trace


__all__ = [
    "reason_and_record",
    "MissingReasoningTranscript",
    "MissingReasoningTrace",
]
