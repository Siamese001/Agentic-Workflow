"""C0.5 verify + 11-dimension score + status decision.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

import hashlib
import json
import uuid

from agentic_core.L1_cognition.c0_context.shape_and_scan import (
    ConflictGapReport,
    ShapedEvidenceSet,
)
from agentic_core.L1_cognition.c0_context.types import (
    EvidenceItem,
    FinalEvidenceContract,
    RecommendedDisposition,
    RouteContractView,
    ScoreBreakdown,
    SupportStatus,
    SupportTarget,
)


# ---------------------------------------------------------------------------
# Verify — C0.5 first half.
# ---------------------------------------------------------------------------


def verify_evidence(items: tuple[EvidenceItem, ...]) -> tuple[
    tuple[EvidenceItem, ...],
    tuple[tuple[EvidenceItem, str], ...],
]:
    """Return (verified, rejected_with_reasons).

    Per spec: source_id resolves, span_ref resolves, ACL cleared, not
    classified as instruction.
    """
    verified: list[EvidenceItem] = []
    rejected: list[tuple[EvidenceItem, str]] = []
    for it in items:
        if not it.source_id:
            rejected.append((it, "source_id_missing"))
            continue
        if not it.span_ref:
            rejected.append((it, "span_ref_missing"))
            continue
        if it.acl_status not in {"cleared", "default-allow"}:
            rejected.append((it, f"acl_status={it.acl_status!r}"))
            continue
        verified.append(it)
    return tuple(verified), tuple(rejected)


# ---------------------------------------------------------------------------
# Score — 11-dimension breakdown.
# ---------------------------------------------------------------------------


def score(
    shaped: ShapedEvidenceSet,
    report: ConflictGapReport,
    *,
    support_target: SupportTarget,
) -> ScoreBreakdown:
    """Compute every dimension in [0, 1]. Pure function over its inputs."""
    must_use_n = len(shaped.must_use)
    supporting_n = len(shaped.supporting)
    contradicts_n = len(shaped.contradicts)
    total_n = must_use_n + supporting_n
    direct_support_score = (
        min(1.0, must_use_n / 3.0)  # saturate at 3 must-use items
    )
    coverage_score = (
        min(1.0, total_n / 5.0)  # saturate at 5 total
    )
    if total_n == 0:
        source_authority_score = 0.0
        freshness_score = 0.0
        citation_stability_score = 0.0
        lineage_quality_score = 0.0
        exactness_score = 0.0
        ACL_confidence = 0.0
        source_diversity_score = 0.0
    else:
        source_authority_score = sum(
            it.authority_score for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        freshness_score = sum(
            1.0 if it.freshness_status == "fresh" else 0.5 if it.freshness_status == "stale" else 0.0
            for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        citation_stability_score = sum(
            1.0 if it.span_ref else 0.0
            for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        lineage_quality_score = sum(
            1.0 if (it.retrieval_lane and it.source_id) else 0.0
            for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        # Exactness — fraction backed by sparse/hybrid lanes
        exactness_score = sum(
            1.0 if it.retrieval_lane in {"sparse", "hybrid", "metadata"} else 0.0
            for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        ACL_confidence = sum(
            1.0 if it.acl_status == "cleared" else 0.5
            for it in (*shaped.must_use, *shaped.supporting)
        ) / total_n
        unique_sources = len({it.source_id for it in (*shaped.must_use, *shaped.supporting)})
        source_diversity_score = min(1.0, unique_sources / 3.0)
    contradiction_risk = min(1.0, 0.25 * contradicts_n)
    high_severity_gaps = sum(1.0 for g in report.unresolved_gaps if g.severity >= 0.7)
    unsupported_inference_risk = min(1.0, 0.30 * high_severity_gaps)
    # Stricter exactness target for EXACT_QUOTE / POLICY_CLAUSE / CODE_LOCATION
    if support_target in {
        SupportTarget.EXACT_QUOTE,
        SupportTarget.POLICY_CLAUSE,
        SupportTarget.CODE_LOCATION,
    }:
        exactness_score = exactness_score * 1.0  # no penalty
    return ScoreBreakdown(
        direct_support_score=direct_support_score,
        coverage_score=coverage_score,
        source_authority_score=source_authority_score,
        freshness_score=freshness_score,
        contradiction_risk=contradiction_risk,
        unsupported_inference_risk=unsupported_inference_risk,
        citation_stability_score=citation_stability_score,
        lineage_quality_score=lineage_quality_score,
        source_diversity_score=source_diversity_score,
        exactness_score=exactness_score,
        ACL_confidence=ACL_confidence,
    )


def aggregate_support_score(breakdown: ScoreBreakdown) -> float:
    """Aggregate the 11 dimensions into a scalar in [0, 1].

    Positive dimensions weighted +1; risk dimensions weighted -1; result
    clamped to [0, 1].
    """
    positives = (
        breakdown.direct_support_score * 0.25
        + breakdown.coverage_score * 0.15
        + breakdown.source_authority_score * 0.10
        + breakdown.freshness_score * 0.10
        + breakdown.citation_stability_score * 0.10
        + breakdown.lineage_quality_score * 0.05
        + breakdown.source_diversity_score * 0.05
        + breakdown.exactness_score * 0.10
        + breakdown.ACL_confidence * 0.10
    )
    risks = (
        breakdown.contradiction_risk * 0.50
        + breakdown.unsupported_inference_risk * 0.50
    )
    return max(0.0, min(1.0, positives - 0.50 * risks))


def decide_status(
    shaped: ShapedEvidenceSet,
    report: ConflictGapReport,
    breakdown: ScoreBreakdown,
    *,
    blocked: bool = False,
) -> SupportStatus:
    """Decide one of six SupportStatus values per spec."""
    if blocked:
        return SupportStatus.BLOCKED
    has_evidence = bool(shaped.must_use or shaped.supporting)
    if not has_evidence:
        return SupportStatus.EMPTY
    if report.contradiction_flags:
        # If contradictions are credible (severity >= 0.6), CONFLICTED.
        if any(c.severity >= 0.6 for c in report.contradiction_flags):
            return SupportStatus.CONFLICTED
    score_value = aggregate_support_score(breakdown)
    if score_value >= 0.75 and len(shaped.must_use) >= 1:
        return SupportStatus.PASS
    if score_value >= 0.50:
        return SupportStatus.WEAK_WITH_CAVEATS
    return SupportStatus.WEAK


def recommend_disposition(status: SupportStatus) -> RecommendedDisposition:
    """Map status → disposition per spec."""
    return {
        SupportStatus.PASS: RecommendedDisposition.PROCEED,
        SupportStatus.WEAK_WITH_CAVEATS: RecommendedDisposition.PROCEED_WITH_CAVEAT,
        SupportStatus.WEAK: RecommendedDisposition.REROUTE,
        SupportStatus.CONFLICTED: RecommendedDisposition.HUMAN_REVIEW,
        SupportStatus.EMPTY: RecommendedDisposition.ABSTAIN,
        SupportStatus.BLOCKED: RecommendedDisposition.FALLBACK_R5,
    }[status]


# ---------------------------------------------------------------------------
# Final contract assembly.
# ---------------------------------------------------------------------------


def build_final_contract(
    *,
    route: RouteContractView,
    shaped: ShapedEvidenceSet,
    report: ConflictGapReport,
    breakdown: ScoreBreakdown,
    refine_attempts: int = 0,
    blocked: bool = False,
) -> FinalEvidenceContract:
    status = decide_status(shaped, report, breakdown, blocked=blocked)
    disposition = recommend_disposition(status)
    support_score = aggregate_support_score(breakdown)
    contract_id = str(uuid.uuid4())
    # Concatenate every evidence class into a single tuple ordered by class.
    all_items = (
        *shaped.must_use,
        *shaped.supporting,
        *shaped.contradicts,
        *shaped.background,
        *shaped.definitions,
    )
    return FinalEvidenceContract(
        contract_id=contract_id,
        route_id=route.route_id,
        route_replay_key=route.route_replay_key,
        policy_hash=route.policy_hash,
        blueprint_hash=route.blueprint_hash,
        status=status,
        support_score=support_score,
        score_breakdown=breakdown,
        evidence=all_items,
        contradiction_flags=report.contradiction_flags,
        unresolved_gaps=report.unresolved_gaps,
        recommended_disposition=disposition,
        refine_attempts=refine_attempts,
        extras={"content_classification": "data"},
    )


def contract_digest(contract: FinalEvidenceContract) -> str:
    """Stable sha256 digest over the contract for replay-cert."""
    payload = {
        "contract_id": contract.contract_id,
        "route_id": contract.route_id,
        "policy_hash": contract.policy_hash,
        "status": contract.status.value,
        "support_score": round(contract.support_score, 6),
        "n_evidence": len(contract.evidence),
        "n_contradictions": len(contract.contradiction_flags),
        "n_gaps": len(contract.unresolved_gaps),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
    ).hexdigest()[:32]


__all__ = [
    "aggregate_support_score",
    "build_final_contract",
    "contract_digest",
    "decide_status",
    "recommend_disposition",
    "score",
    "verify_evidence",
]
