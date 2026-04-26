"""C0 FAILURE MODES — 14 detectors.

Spec: C0 Context Engine.md lines 925-946. Each detector is a pure predicate
on the run's stage outputs. The dispatcher folds them into the final
contract's `extras["failure_modes_detected"]` for telemetry + replay.

These detectors are READ-ONLY. They do NOT block on their own; the gates
(G0–G10) are responsible for blocking. Failure modes are early-warning
signals for L6 observability and weekly drift reports.
"""

from __future__ import annotations

from dataclasses import dataclass

from .candidate_pool import CandidateEvidencePool
from .contradiction_gap import ConflictGapReport
from .evidence_contract import EvidenceContract
from .graph_traverse import GraphExpandedEvidencePool
from .hydration import HydratedEvidencePool
from .injection import detect_injection_markers
from .plan import RetrievalPlan
from .route_contract import RouteContract
from .shape import ShapedEvidenceSet
from .verdicts import (
    EXACTNESS_REQUIRED,
    ContradictionType,
    FailureMode,
    FreshnessClass,
    RetrievalLane,
    SourceClass,
    SupportStatus,
)


@dataclass(frozen=True)
class FailureModeReport:
    """Per-run failure-mode evidence."""

    plan_id: str
    detected: tuple[FailureMode, ...]
    notes: tuple[tuple[FailureMode, str], ...] = ()

    def has(self, mode: FailureMode) -> bool:
        return mode in self.detected

    def reasons(self, mode: FailureMode) -> tuple[str, ...]:
        return tuple(n for m, n in self.notes if m == mode)


# ----- detectors -----


def _dense_only_hallucination(
    *, hydrated: HydratedEvidencePool, plan: RetrievalPlan,
) -> str | None:
    """Failure: dense-only support for an exactness-required target."""
    if plan.support_target not in EXACTNESS_REQUIRED:
        return None
    has_exact = any(
        RetrievalLane.SPARSE in h.candidate.found_by_lanes
        or RetrievalLane.METADATA in h.candidate.found_by_lanes
        or RetrievalLane.CODE in h.candidate.found_by_lanes
        for h in hydrated.hydrated
    )
    dense_count = sum(
        1 for h in hydrated.hydrated
        if RetrievalLane.DENSE in h.candidate.found_by_lanes
    )
    if not has_exact and dense_count > 0:
        return f"target={plan.support_target.value} backed only by {dense_count} dense hits"
    return None


def _wrong_tenant_evidence(
    *, hydrated: HydratedEvidencePool, route: RouteContract,
) -> str | None:
    bad: list[str] = []
    for h in hydrated.hydrated:
        m = h.candidate.manifest
        if route.tenant_scope and m.tenant and m.tenant != route.tenant_scope:
            bad.append(h.candidate.chunk_id)
    if bad:
        return f"{len(bad)} chunk(s) from tenant != {route.tenant_scope!r}"
    return None


def _stale_policy_answer(
    *, hydrated: HydratedEvidencePool, route: RouteContract, plan: RetrievalPlan,
) -> str | None:
    if route.freshness_class in (FreshnessClass.STATIC, FreshnessClass.SLOW):
        return None
    is_policy = SourceClass.POLICY in plan.source_classes
    if not is_policy:
        return None
    stale = sum(
        1 for h in hydrated.hydrated
        if h.candidate.source_class == SourceClass.POLICY
        and not h.quality.source_version_current
    )
    if stale > 0:
        return f"{stale} policy chunk(s) lack current version under freshness={route.freshness_class.value}"
    return None


def _quote_distortion(
    *, hydrated: HydratedEvidencePool,
) -> str | None:
    risky = [
        h.candidate.chunk_id for h in hydrated.hydrated
        if h.quality.chunk_boundary_risk.value == "high"
    ]
    if risky:
        return f"{len(risky)} chunk(s) end mid-thought (high boundary risk)"
    return None


def _hidden_contradiction(
    *, contract: EvidenceContract, conflict: ConflictGapReport,
) -> str | None:
    """If contract status is PASS but contradictions are recorded, that's hidden."""
    if contract.status == SupportStatus.PASS and conflict.contradictions:
        return (
            f"PASS contract suppresses {len(conflict.contradictions)} contradiction(s)"
        )
    return None


def _graph_scope_creep(
    *, expanded: GraphExpandedEvidencePool, plan: RetrievalPlan,
) -> str | None:
    over = [
        h for h in expanded.traverse.hops
        if h.hop_depth > plan.graph_bounds.max_hops
    ]
    if over:
        return f"{len(over)} hop(s) exceed max_hops={plan.graph_bounds.max_hops}"
    return None


def _cache_poisoning(
    *, hydrated: HydratedEvidencePool, plan: RetrievalPlan,
) -> str | None:
    if not plan.cache_policy.allow_cache:
        return None
    cache_only = [
        h for h in hydrated.hydrated
        if h.candidate.found_by_lanes == (RetrievalLane.CACHE,)
        and not h.candidate.manifest.version
    ]
    if cache_only:
        return f"{len(cache_only)} cache-only chunk(s) with no version lineage"
    return None


def _prompt_injection(
    *, candidates: CandidateEvidencePool,
) -> str | None:
    flagged = [
        c.chunk_id for c in candidates.candidates
        if detect_injection_markers(c.text)
    ]
    if flagged:
        return f"{len(flagged)} chunk(s) carry instruction-like text"
    return None


def _fake_confidence(
    *, contract: EvidenceContract,
) -> str | None:
    """Aggregate score >= 0.70 but score_breakdown.exactness < 0.40 = inflated."""
    sb = contract.score_breakdown
    if contract.support_score >= 0.70 and sb.exactness_score < 0.30:
        return f"support_score={contract.support_score:.2f} but exactness={sb.exactness_score:.2f}"
    return None


def _lost_lineage(
    *, hydrated: HydratedEvidencePool,
) -> str | None:
    no_lineage = [
        h.candidate.chunk_id for h in hydrated.hydrated
        if not h.candidate.found_by_lanes
    ]
    if no_lineage:
        return f"{len(no_lineage)} chunk(s) missing retrieval lane (C0.I3 violation)"
    return None


def _overstuffed_context(
    *, shaped: ShapedEvidenceSet, plan: RetrievalPlan,
) -> str | None:
    if shaped.token_estimate > plan.budgets.max_token_context:
        return (
            f"shaped token_estimate={shaped.token_estimate} > budget="
            f"{plan.budgets.max_token_context}"
        )
    return None


def _unsupported_synthesis(
    *, contract: EvidenceContract,
) -> str | None:
    if (
        contract.support_score >= 0.50
        and contract.score_breakdown.unsupported_inference_risk >= 0.50
    ):
        return (
            f"unsupported_inference_risk={contract.score_breakdown.unsupported_inference_risk:.2f}"
            f" while support_score={contract.support_score:.2f}"
        )
    return None


def _docs_vs_code_mismatch(
    *, conflict: ConflictGapReport,
) -> str | None:
    """If contradiction_type=CODE found, surface it as a failure mode flag."""
    code = sum(
        1 for cf in conflict.contradictions
        if cf.contradiction_type == ContradictionType.CODE
    )
    if code:
        return f"{code} docs-vs-code contradiction(s)"
    return None


def _runtime_vs_design_mismatch(
    *, conflict: ConflictGapReport,
) -> str | None:
    rt = sum(
        1 for cf in conflict.contradictions
        if cf.contradiction_type == ContradictionType.RUNTIME
    )
    if rt:
        return f"{rt} runtime-vs-design contradiction(s)"
    return None


# ----- aggregate runner -----


def detect_all_failure_modes(
    *,
    plan: RetrievalPlan,
    route: RouteContract,
    candidates: CandidateEvidencePool,
    hydrated: HydratedEvidencePool,
    expanded: GraphExpandedEvidencePool,
    shaped: ShapedEvidenceSet,
    conflict: ConflictGapReport,
    contract: EvidenceContract,
) -> FailureModeReport:
    """Run all 14 detectors. Each that fires contributes one note line."""
    runners: tuple[tuple[FailureMode, str | None], ...] = (
        (FailureMode.DENSE_ONLY_HALLUCINATION,
         _dense_only_hallucination(hydrated=hydrated, plan=plan)),
        (FailureMode.WRONG_TENANT_EVIDENCE,
         _wrong_tenant_evidence(hydrated=hydrated, route=route)),
        (FailureMode.STALE_POLICY_ANSWER,
         _stale_policy_answer(hydrated=hydrated, route=route, plan=plan)),
        (FailureMode.QUOTE_DISTORTION,
         _quote_distortion(hydrated=hydrated)),
        (FailureMode.HIDDEN_CONTRADICTION,
         _hidden_contradiction(contract=contract, conflict=conflict)),
        (FailureMode.GRAPH_SCOPE_CREEP,
         _graph_scope_creep(expanded=expanded, plan=plan)),
        (FailureMode.CACHE_POISONING,
         _cache_poisoning(hydrated=hydrated, plan=plan)),
        (FailureMode.PROMPT_INJECTION,
         _prompt_injection(candidates=candidates)),
        (FailureMode.FAKE_CONFIDENCE,
         _fake_confidence(contract=contract)),
        (FailureMode.LOST_LINEAGE,
         _lost_lineage(hydrated=hydrated)),
        (FailureMode.OVERSTUFFED_CONTEXT,
         _overstuffed_context(shaped=shaped, plan=plan)),
        (FailureMode.UNSUPPORTED_SYNTHESIS,
         _unsupported_synthesis(contract=contract)),
        (FailureMode.DOCS_VS_CODE_MISMATCH,
         _docs_vs_code_mismatch(conflict=conflict)),
        (FailureMode.RUNTIME_VS_DESIGN_MISMATCH,
         _runtime_vs_design_mismatch(conflict=conflict)),
    )
    detected: list[FailureMode] = []
    notes: list[tuple[FailureMode, str]] = []
    for mode, reason in runners:
        if reason is not None:
            detected.append(mode)
            notes.append((mode, reason))
    return FailureModeReport(
        plan_id=plan.plan_id,
        detected=tuple(detected),
        notes=tuple(notes),
    )


__all__ = ["FailureModeReport", "detect_all_failure_modes"]
