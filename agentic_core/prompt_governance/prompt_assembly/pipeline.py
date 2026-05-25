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

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

_logger = logging.getLogger(__name__)
_L5_CERT_REF_FAIL_CLOSED = os.getenv("L5_CERT_REF_FAIL_CLOSED", "0") == "1"


def _check_l5_cert_ref_pa(ref: str) -> None:
    """Fail-soft L5 cert ref verify at PA entry per AG-W0-3=A_consume_entry."""
    try:
        from agentic_core.L5_safety.contracts.registry import verify_certification_ref
        valid = verify_certification_ref(ref)
    except Exception as exc:  # guardian: allow-log-and-swallow -- L5 registry must not crash PA pipeline; treat as unverified  # guardian: allow-broad-exception -- P1 ADG burndown
        _logger.warning("L5CertRefViolation stage=PA_entry registry_error=%s", exc)
        return
    if not valid:
        msg = "L5CertRefViolation stage=PA_entry ref=%r — missing or invalid l5_certification_ref"
        if _L5_CERT_REF_FAIL_CLOSED:
            raise ValueError(msg % (ref,))
        _logger.warning(msg, ref)


from .assembly_statuses import (
    PAStatus,
    status_for_pa0,
    status_for_pa3,
    status_for_pa5,
)
from .doctrine_receipts import (
    aggregate_doctrine_status,
    pa0_doctrine_receipt,
    pa3_doctrine_receipt,
    pa5_doctrine_receipt,
    pa7_doctrine_receipt,
)
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
    """Bundle returned by :func:`run_prompt_assembly_pipeline`.

    The ``doctrine_status`` and ``doctrine_receipts`` fields surface the
    canonical PA_* status vocabulary mandated by the Prompt Assembly
    doctrine. They are derived deterministically from the rich internal
    result objects (boundary, classifier, budget, dispatch) so the
    pipeline emits both representations without duplication.
    """

    boundary: BoundaryCheckResult
    classifier: C0ClassifierResult | None
    budget: BudgetReport | None
    dispatch: DispatchOutcome
    events: tuple[PromptAssemblyEvent, ...]
    kept_budget_entries: tuple[SlotBudgetEntry, ...] = field(default_factory=tuple)
    doctrine_status: PAStatus = PAStatus.PA_READY
    doctrine_receipts: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

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
    # PA entry: verify upstream (route/plan) l5_certification_ref (AG-W0-3)
    _check_l5_cert_ref_pa(
        str((route_contract or {}).get("l5_certification_ref", ""))
    )

    buf = EventBuffer()
    plan = plan_contract or {}
    route = route_contract or {}

    plan_id = str(plan.get("plan_id", ""))
    route_id = str(route.get("route_id", ""))
    policy_hash = str((execution_metadata or {}).get("policy_hash", "") or plan.get("policy_hash", ""))
    provider_lane = str(route.get("provider_lane", ""))
    request_id = str((execution_metadata or {}).get("request_id", ""))
    run_id = str((execution_metadata or {}).get("run_id", ""))
    trace_id = str((execution_metadata or {}).get("trace_id", ""))
    replay_key = str((execution_metadata or {}).get("replay_key", ""))
    doctrine_receipts: list[Mapping[str, Any]] = []

    def _doctrine_status() -> PAStatus:
        return aggregate_doctrine_status(doctrine_receipts) if doctrine_receipts else PAStatus.PA_READY

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
    pa0_receipt = pa0_doctrine_receipt(
        boundary,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        route_id=route_id,
        plan_id=plan_id,
        policy_hash=policy_hash,
        replay_key=replay_key,
    )
    doctrine_receipts.append(pa0_receipt)
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
            doctrine_status=_doctrine_status(),
            doctrine_receipts=tuple(doctrine_receipts),
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
            doctrine_status=_doctrine_status(),
            doctrine_receipts=tuple(doctrine_receipts),
        )

    # PA.1 BOM resolution is delegated to the existing PromptBOMBuilder.
    # We emit an event marker here so the spec's observability list is
    # complete without re-implementing BOM resolution.
    requested = tuple(sorted(set(route.get("required_slots") or ())))
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
        doctrine_receipts.append(
            pa3_doctrine_receipt(
                classifier=classifier,
                request_id=request_id,
                policy_hash=policy_hash,
                replay_key=replay_key,
            )
        )
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
                doctrine_status=_doctrine_status(),
                doctrine_receipts=tuple(doctrine_receipts),
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
        doctrine_receipts.append(
            pa5_doctrine_receipt(
                budget_report,
                request_id=request_id,
                policy_hash=policy_hash,
                replay_key=replay_key,
            )
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
                doctrine_status=_doctrine_status(),
                doctrine_receipts=tuple(doctrine_receipts),
            )

    # ----- PA.7 Final emit (PASS) -----
    outcome = build_dispatch_outcome(
        disposition=DispatchDisposition.PASS,
        detail="prompt_assembly_pipeline_pass",
    )
    artifact_id = str((execution_metadata or {}).get("artifact_id", ""))
    manifest_hash = str((execution_metadata or {}).get("manifest_hash", "")) or "pipeline_pass"
    hmac_sig = str((execution_metadata or {}).get("hmac_sig", "")) or ""
    doctrine_receipts.append(
        pa7_doctrine_receipt(
            artifact_id=artifact_id,
            manifest_hash=manifest_hash,
            hmac_sig=hmac_sig,
            signed=bool(hmac_sig),
            handoff_ready=bool(hmac_sig),
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            route_id=route_id,
            plan_id=plan_id,
            policy_hash=policy_hash,
            replay_key=replay_key,
        )
    )
    buf.emit(
        PromptAssemblyDispatched(
            artifact_id=artifact_id,
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
        doctrine_status=_doctrine_status(),
        doctrine_receipts=tuple(doctrine_receipts),
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
    "PAStatus",
    "PromptAssemblyPipelineResult",
    "run_prompt_assembly_pipeline",
]
