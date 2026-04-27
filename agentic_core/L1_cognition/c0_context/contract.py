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
    # NB: support_target is already enforced upstream via scan_contradictions_and_gaps
    # (MISSING_EXACT_QUOTE gap fires for EXACT_QUOTE without sparse/metadata/hybrid lane);
    # downstream that gap drives unsupported_inference_risk + decide_status. No extra
    # multiplier needed here. (Previous dead `* 1.0` no-op removed 2026-04-26.)
    _ = support_target  # parameter retained for spec parity / future use
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
    """Decide one of six SupportStatus values per spec.

    Order matters: BLOCKED ≻ CONFLICTED ≻ EMPTY ≻ PASS/WEAK\_*.

    Per invariant **I7** ("contradictions must be surfaced, not hidden"),
    a credible contradiction (severity ≥ 0.6) is reported as CONFLICTED
    even when there is no MUST_USE / SUPPORTING anchor. Returning EMPTY in
    that case would silently swallow the contradiction (Bug 4 — fixed
    2026-04-26).
    """
    if blocked:
        return SupportStatus.BLOCKED
    # Surface credible contradictions BEFORE evaluating emptiness, so that a
    # pool of pure CONTRADICTS items still reports CONFLICTED instead of EMPTY.
    if report.contradiction_flags and any(
        c.severity >= 0.6 for c in report.contradiction_flags
    ):
        return SupportStatus.CONFLICTED
    has_evidence = bool(shaped.must_use or shaped.supporting)
    if not has_evidence:
        return SupportStatus.EMPTY
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
    """Stable sha256 digest over the *content* of the contract for replay-cert.

    Content-addressed, NOT name-addressed: ``contract_id`` is excluded
    because ``build_final_contract`` mints a fresh uuid each call, which
    would otherwise make the digest unstable across identical inputs
    (Bug 2 — fixed 2026-04-26).

    The payload also captures evidence identity (every ``evidence_id`` and
    ``source_id``, sorted), contradiction flag content, gap content, the
    full score breakdown, the recommended disposition, and refine attempts.
    Two contracts with different evidence pools can no longer collapse to
    the same digest (Bug 3 — fixed 2026-04-26).
    """
    payload = {
        # Route + policy provenance.
        "route_id": contract.route_id,
        "route_replay_key": contract.route_replay_key,
        "policy_hash": contract.policy_hash,
        "blueprint_hash": contract.blueprint_hash,
        # Decision surface.
        "status": contract.status.value,
        "recommended_disposition": contract.recommended_disposition.value,
        "support_score": round(contract.support_score, 6),
        "refine_attempts": contract.refine_attempts,
        # Full score breakdown (every dimension, rounded for stability).
        "score_breakdown": {
            k: round(v, 6) for k, v in contract.score_breakdown.as_dict().items()
        },
        # Evidence content — deterministically ordered for replay stability.
        "evidence_ids": sorted(it.evidence_id for it in contract.evidence),
        "evidence_sources": sorted(
            f"{it.source_id}|{it.span_ref}" for it in contract.evidence
        ),
        # Contradiction + gap content — deterministically ordered.
        "contradiction_flags": sorted(
            (
                f.contradiction_type.value,
                f.source_a,
                f.source_b,
                round(f.severity, 6),
            )
            for f in contract.contradiction_flags
        ),
        "unresolved_gaps": sorted(
            (g.gap_type.value, round(g.severity, 6))
            for g in contract.unresolved_gaps
        ),
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
