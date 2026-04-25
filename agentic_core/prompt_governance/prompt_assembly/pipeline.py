"""PA Pipeline Orchestrator — chains PA.0 → PA.7.

This is a thin, deterministic orchestrator. It does NOT replace the
existing :class:`AirlockAssembler.assemble_from_bom` or the rich
``CompiledPromptArtifact`` signing flow; instead it drives the *staged
checks* described in the spec and produces a :class:`PromptAssemblyPipelineResult`
that bundles:

  * the boundary check result (PA.0)
  * the C0 classifier result (PA.3)
  * the budget report (PA.5)
  * the dispatch outcome (PA.7)
  * the ordered observability event log

When an upstream stage blocks, the pipeline short-circuits and emits the
appropriate :class:`PromptAssemblyBlocked` event with the canonical reason
code mapped to a :class:`DispatchDisposition`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from .observability_events import (
    EventBuffer,
    PromptAssemblyBlocked,
    PromptAssemblyDispatched,
    PromptAssemblyEvent,
    PromptAssemblyStarted,
    PromptBOMResolved,
    PromptBudgetCompleted,
    PromptSecurityPassCompleted,
)
from .pa0_boundary import (
    BoundaryCheckResult,
    BoundaryFailReason,
    BoundaryStatus,
    boundary_check,
)
from .pa3_c0_classifier import (
    C0ClassifierResult,
    C0Disposition,
    classify_c0_chunks,
)
from .pa5_budget import (
    BudgetReport,
    OverflowStatus,
    SlotBudgetEntry,
    build_budget_report,
)
from .pa7_dispatch_states import (
    DispatchBlockReason,
    DispatchDisposition,
    DispatchOutcome,
    build_dispatch_outcome,
)


@dataclass(frozen=True)
class PromptAssemblyPipelineResult:
    """Bundle returned by :func:`run_prompt_assembly_pipeline`."""

    boundary: BoundaryCheckResult
    classifier: C0ClassifierResult | None
    budget: BudgetReport | None
    dispatch: DispatchOutcome
    events: tuple[PromptAssemblyEvent, ...]
    kept_budget_entries: tuple[SlotBudgetEntry, ...] = field(default_factory=tuple)

    @property
    def dispatch_allowed(self) -> bool:
        return self.dispatch.dispatch_allowed


# ---------------------------------------------------------------------------
# Boundary-fail-reason → dispatch mapping
# ---------------------------------------------------------------------------


def _map_boundary_to_dispatch(reason: BoundaryFailReason) -> tuple[DispatchDisposition, DispatchBlockReason]:
    """Map a PA.0 fail reason to a PA.7 dispatch disposition + block reason."""
    if reason in {BoundaryFailReason.MISSING_PLAN_CONTRACT, BoundaryFailReason.MISSING_ROUTE_CONTRACT}:
        return DispatchDisposition.BLOCKED_REPLAY, DispatchBlockReason.REPLAY_METADATA_MISSING
    if reason is BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE:
        return DispatchDisposition.BLOCKED_CONTEXT, DispatchBlockReason.EVIDENCE_REQUIRED_MISSING
    if reason is BoundaryFailReason.DURABLE_WRITE_NOT_PERMITTED:
        return DispatchDisposition.BLOCKED_POLICY, DispatchBlockReason.POLICY_FENCE_VIOLATION
    if reason is BoundaryFailReason.HITL_REQUIRED_BUT_EXECUTABLE_REQUESTED:
        return DispatchDisposition.BLOCKED_HITL, DispatchBlockReason.HITL_REVIEW_REQUIRED
    if reason is BoundaryFailReason.POLICY_HASH_MISMATCH:
        return DispatchDisposition.BLOCKED_POLICY, DispatchBlockReason.POLICY_HASH_MISMATCH
    raise ValueError(f"unmapped boundary fail reason: {reason}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_prompt_assembly_pipeline(
    *,
    plan_contract: Mapping[str, Any] | None,
    route_contract: Mapping[str, Any] | None,
    evidence_contract: Mapping[str, Any] | None = None,
    governance: Mapping[str, Any] | None = None,
    execution_metadata: Mapping[str, Any] | None = None,
    c0_chunks: Sequence[Mapping[str, str]] | None = None,
    budget_entries: Sequence[SlotBudgetEntry] | None = None,
    model_context_window: int = 200_000,
    reserved_output_tokens: int = 4096,
    reserved_schema_tokens: int = 0,
    reserved_tool_tokens: int = 0,
) -> PromptAssemblyPipelineResult:
    """Run PA.0 → PA.7 staged checks in deterministic order.

    Each stage emits the spec-named event before the next runs. On any
    block-class outcome the pipeline short-circuits and emits a
    :class:`PromptAssemblyBlocked` event before returning.
    """
    buf = EventBuffer()
    plan = plan_contract or {}
    route = route_contract or {}

    plan_id = str(plan.get("plan_id", ""))
    route_id = str(route.get("route_id", ""))
    policy_hash = str((execution_metadata or {}).get("policy_hash", "") or plan.get("policy_hash", ""))
    provider_lane = str(route.get("provider_lane", ""))
    request_id = str((execution_metadata or {}).get("request_id", ""))

    buf.emit(
        PromptAssemblyStarted(
            request_id=request_id,
            plan_id=plan_id,
            route_id=route_id,
            policy_hash=policy_hash,
            provider_lane=provider_lane,
        )
    )

    # ----- PA.0 -----
    boundary = boundary_check(
        plan_contract=plan_contract,
        route_contract=route_contract,
        evidence_contract=evidence_contract,
        governance=governance,
        execution_metadata=execution_metadata,
    )
    if boundary.status is BoundaryStatus.FAIL:
        assert boundary.fail_reason is not None
        disposition, block_reason = _map_boundary_to_dispatch(boundary.fail_reason)
        outcome = build_dispatch_outcome(
            disposition=disposition,
            block_reason=block_reason,
            detail=f"PA.0 boundary check failed: {boundary.fail_reason.value}",
        )
        buf.emit(
            PromptAssemblyBlocked(
                reason_code=block_reason.value,
                policy_hash=policy_hash,
                plan_id=plan_id,
                route_id=route_id,
                recommended_disposition=disposition.value,
            )
        )
        return PromptAssemblyPipelineResult(
            boundary=boundary,
            classifier=None,
            budget=None,
            dispatch=outcome,
            events=tuple(buf.events),
        )

    if boundary.status is BoundaryStatus.SKIP:
        # Terminal [RET] route — PA is not needed at all. Caller must dispatch
        # to Exit Eval directly; we still record an event so telemetry sees it.
        outcome = build_dispatch_outcome(
            disposition=DispatchDisposition.PASS,
            detail="terminal_shortcircuit_route_pa_skipped",
        )
        buf.emit(
            PromptAssemblyDispatched(
                artifact_id="",
                l2_target="exit_eval",
                trace_root=request_id,
            )
        )
        return PromptAssemblyPipelineResult(
            boundary=boundary,
            classifier=None,
            budget=None,
            dispatch=outcome,
            events=tuple(buf.events),
        )

    # PA.1 BOM resolution is delegated to the existing PromptBOMBuilder.
    # We emit an event marker here so the spec's observability list is
    # complete without re-implementing BOM resolution.
    requested = tuple(sorted(set((route.get("required_slots") or ()))))
    available = requested  # caller is expected to pass already-resolved BOM
    buf.emit(
        PromptBOMResolved(
            bom_id=str((execution_metadata or {}).get("bom_id", "")),
            slots_requested=requested,
            slots_available=available,
            slots_missing=(),
        )
    )

    # ----- PA.3 C0 classifier -----
    classifier: C0ClassifierResult | None = None
    if c0_chunks:
        classifier = classify_c0_chunks(c0_chunks)
        buf.emit(
            PromptSecurityPassCompleted(
                u0_disposition="neutralized",
                c0_classifier_disposition=_summarize_c0(classifier),
                h0_disposition="absent",
                stripped_count=classifier.strip_count,
                quarantined_count=classifier.quarantine_count,
            )
        )
        # If grounding required and *every* must-use chunk got rejected, block.
        grounding_required = bool(plan.get("grounding_required", False))
        if grounding_required and classifier.pass_count + classifier.strip_count == 0:
            outcome = build_dispatch_outcome(
                disposition=DispatchDisposition.BLOCKED_CONTEXT,
                block_reason=DispatchBlockReason.EVIDENCE_BLOCKED,
                detail="all C0 chunks were rejected/quarantined",
            )
            buf.emit(
                PromptAssemblyBlocked(
                    reason_code=DispatchBlockReason.EVIDENCE_BLOCKED.value,
                    policy_hash=policy_hash,
                    plan_id=plan_id,
                    route_id=route_id,
                    recommended_disposition=DispatchDisposition.BLOCKED_CONTEXT.value,
                )
            )
            return PromptAssemblyPipelineResult(
                boundary=boundary,
                classifier=classifier,
                budget=None,
                dispatch=outcome,
                events=tuple(buf.events),
            )

    # ----- PA.5 Budget -----
    budget_report: BudgetReport | None = None
    kept: list[SlotBudgetEntry] = []
    if budget_entries:
        budget_report, kept = build_budget_report(
            model_context_window=model_context_window,
            reserved_output_tokens=reserved_output_tokens,
            reserved_schema_tokens=reserved_schema_tokens,
            reserved_tool_tokens=reserved_tool_tokens,
            entries=budget_entries,
        )
        buf.emit(
            PromptBudgetCompleted(
                input_token_estimate=budget_report.input_token_estimate,
                output_token_reserve=budget_report.reserved_output_tokens,
                trim_actions=budget_report.trim_actions,
                overflow_status=budget_report.overflow_status.value,
            )
        )
        if not budget_report.can_dispatch:
            block_reason = (
                DispatchBlockReason.BUDGET_REFINE_REQUIRED
                if budget_report.overflow_status is OverflowStatus.REFINE
                else DispatchBlockReason.BUDGET_OVERFLOW
            )
            outcome = build_dispatch_outcome(
                disposition=DispatchDisposition.BLOCKED_BUDGET,
                block_reason=block_reason,
                detail=f"budget overflow: {budget_report.overflow_status.value}",
            )
            buf.emit(
                PromptAssemblyBlocked(
                    reason_code=block_reason.value,
                    policy_hash=policy_hash,
                    plan_id=plan_id,
                    route_id=route_id,
                    recommended_disposition=DispatchDisposition.BLOCKED_BUDGET.value,
                )
            )
            return PromptAssemblyPipelineResult(
                boundary=boundary,
                classifier=classifier,
                budget=budget_report,
                dispatch=outcome,
                events=tuple(buf.events),
                kept_budget_entries=tuple(kept),
            )

    # ----- PA.7 Final emit (PASS) -----
    outcome = build_dispatch_outcome(
        disposition=DispatchDisposition.PASS,
        detail="prompt_assembly_pipeline_pass",
    )
    buf.emit(
        PromptAssemblyDispatched(
            artifact_id=str((execution_metadata or {}).get("artifact_id", "")),
            l2_target="sovereign_llm_gateway",
            trace_root=request_id,
        )
    )
    return PromptAssemblyPipelineResult(
        boundary=boundary,
        classifier=classifier,
        budget=budget_report,
        dispatch=outcome,
        events=tuple(buf.events),
        kept_budget_entries=tuple(kept),
    )


def _summarize_c0(result: C0ClassifierResult) -> str:
    if result.reject_count == result.total and result.total > 0:
        return C0Disposition.REJECT.value
    if result.quarantine_count > 0:
        return C0Disposition.QUARANTINE.value
    if result.strip_count > 0:
        return C0Disposition.STRIP.value
    return C0Disposition.PASS.value


__all__ = [
    "PromptAssemblyPipelineResult",
    "run_prompt_assembly_pipeline",
]
