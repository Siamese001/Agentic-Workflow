"""C0.5 EVIDENCE CONTRACT — verification + scoring.

Spec: C0 Context Engine.md lines 567-635. Pure-data; produces an
EvidenceContract for the dispatcher to seal into a FinalEvidenceContract.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass, field
from typing import Iterable

from .contradiction_gap import ConflictGapReport
from .shape import RankedChunk, ShapedEvidenceSet
from .verdicts import (
    EXACTNESS_REQUIRED,
    EvidenceClass,
    RecommendedDisposition,
    RetrievalLane,
    SupportStatus,
    SupportTarget,
)

_HMAC_KEY = b"agentic-core-c0-final-contract-v1"


@dataclass(frozen=True)
class ScoreBreakdown:
    """C0.5 SCORE DIMENSIONS — spec lines 589-600 + final-contract 754-763.

    Every field is a float in [0,1]. Higher = better support for that
    dimension. Risk fields (contradiction_risk, unsupported_inference_risk)
    are inverted: higher = MORE risk = worse for downstream.
    """

    direct_support_score: float = 0.0
    coverage_score: float = 0.0
    source_authority_score: float = 0.0
    freshness_score: float = 0.0
    citation_stability_score: float = 0.0
    lineage_quality_score: float = 0.0
    source_diversity_score: float = 0.0
    exactness_score: float = 0.0
    contradiction_risk: float = 0.0
    unsupported_inference_risk: float = 0.0
    acl_confidence: float = 1.0

    def __post_init__(self) -> None:
        for name in (
            "direct_support_score", "coverage_score", "source_authority_score",
            "freshness_score", "citation_stability_score",
            "lineage_quality_score", "source_diversity_score",
            "exactness_score", "contradiction_risk",
            "unsupported_inference_risk", "acl_confidence",
        ):
            v = getattr(self, name)
            if not 0.0 <= float(v) <= 1.0:
                raise ValueError(f"ScoreBreakdown.{name}={v} out of [0,1]")

    def aggregate(self) -> float:
        """Single-number support score in [0,1].

        Positive signals minus risk penalties, clamped.
        """
        positives = (
            self.direct_support_score * 0.20
            + self.coverage_score * 0.15
            + self.source_authority_score * 0.10
            + self.freshness_score * 0.05
            + self.citation_stability_score * 0.10
            + self.lineage_quality_score * 0.05
            + self.exactness_score * 0.10
            + self.source_diversity_score * 0.05
            + self.acl_confidence * 0.10
        )
        penalties = (
            self.contradiction_risk * 0.15
            + self.unsupported_inference_risk * 0.10
        )
        return max(0.0, min(1.0, positives - penalties))


@dataclass(frozen=True)
class EvidenceContract:
    """Spec lines 617-622 — typed output of C0.5."""

    plan_id: str
    request_id: str
    status: SupportStatus
    support_score: float
    score_breakdown: ScoreBreakdown
    verified_chunk_ids: tuple[str, ...]
    cited_span_refs: tuple[str, ...]
    source_ids: tuple[str, ...]
    evidence_classes: dict[EvidenceClass, tuple[str, ...]] = field(default_factory=dict)
    contradiction_chunk_pairs: tuple[tuple[str, str], ...] = ()
    unresolved_gap_codes: tuple[str, ...] = ()
    recommended_disposition: RecommendedDisposition = RecommendedDisposition.PROCEED
    abstain_hint: bool = False
    evidence_hmac: str = ""

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("EvidenceContract.plan_id required")
        if not self.request_id.strip():
            raise ValueError("EvidenceContract.request_id required")
        if not 0.0 <= self.support_score <= 1.0:
            raise ValueError("support_score must be in [0,1]")
        if self.status == SupportStatus.PASS and self.abstain_hint:
            raise ValueError("PASS contract cannot carry abstain_hint=True")
        if self.status == SupportStatus.PASS and not self.verified_chunk_ids:
            raise ValueError("PASS contract requires at least one verified chunk")
        if not self.evidence_hmac:
            raise ValueError("evidence_hmac is required")

    @staticmethod
    def compute_hmac(
        plan_id: str,
        request_id: str,
        verified_chunk_ids: Iterable[str],
        score_breakdown: ScoreBreakdown,
    ) -> str:
        payload = json.dumps(
            {
                "plan_id": plan_id,
                "request_id": request_id,
                "chunks": sorted(verified_chunk_ids),
                "scores": asdict(score_breakdown),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hmac.new(_HMAC_KEY, payload, hashlib.sha256).hexdigest()


# ----- helpers -----


def _verify_chunk(rc: RankedChunk) -> bool:
    """Spec lines 577-587 — every must verify."""
    q = rc.chunk.quality
    return (
        q.span_resolves
        and q.acl_clear
        and q.citation_anchor_stable
        and rc.chunk.canonical_source_path != ""
    )


def _score_breakdown_from(
    shaped: ShapedEvidenceSet,
    *,
    target: SupportTarget,
    conflict_report: ConflictGapReport,
) -> ScoreBreakdown:
    if not shaped.ranked:
        return ScoreBreakdown()

    # direct_support: fraction of MUST_USE chunks
    n = len(shaped.ranked)
    direct_support = (len(shaped.must_use) + 0.5 * len(shaped.supporting)) / max(1, n)
    coverage = min(1.0, (len(shaped.must_use) + len(shaped.supporting)) / 5)

    auths = [r.signals.get(_authority_key(), 0.5) for r in shaped.ranked]
    source_authority = sum(auths) / len(auths) if auths else 0.0

    fresh = [1.0 if r.chunk.quality.source_version_current else 0.0 for r in shaped.ranked]
    freshness = sum(fresh) / len(fresh) if fresh else 0.0

    cite = [1.0 if r.chunk.quality.citation_anchor_stable else 0.0 for r in shaped.ranked]
    citation_stability = sum(cite) / len(cite) if cite else 0.0

    lineage_quality = (
        len([r for r in shaped.ranked if r.chunk.candidate.found_by_lanes]) / max(1, n)
    )

    if target in EXACTNESS_REQUIRED:
        exact = [
            1.0 if RetrievalLane.SPARSE in r.chunk.candidate.found_by_lanes else 0.0
            for r in shaped.ranked
        ]
        exactness = sum(exact) / len(exact)
    else:
        exactness = 0.5

    contradiction_risk = min(1.0, len(conflict_report.contradictions) / 5)
    unsupported_inference_risk = (
        min(1.0, len([g for g in conflict_report.gaps if g.severity == "high"]) / 3)
    )

    classes = {r.chunk.candidate.source_class for r in shaped.ranked}
    source_diversity = min(1.0, len(classes) / 3)

    acl = [1.0 if r.chunk.quality.acl_clear else 0.0 for r in shaped.ranked]
    acl_confidence = sum(acl) / len(acl) if acl else 0.0

    return ScoreBreakdown(
        direct_support_score=direct_support,
        coverage_score=coverage,
        source_authority_score=source_authority,
        freshness_score=freshness,
        citation_stability_score=citation_stability,
        lineage_quality_score=lineage_quality,
        exactness_score=exactness,
        contradiction_risk=contradiction_risk,
        unsupported_inference_risk=unsupported_inference_risk,
        source_diversity_score=source_diversity,
        acl_confidence=acl_confidence,
    )


def _authority_key():
    """Resolve at runtime to avoid circular import with shape.RerankSignal."""
    from .shape import RerankSignal
    return RerankSignal.AUTHORITY


def _choose_status(
    score: ScoreBreakdown,
    conflict: ConflictGapReport,
    *,
    has_evidence: bool,
    acl_blocked: bool,
) -> SupportStatus:
    if acl_blocked:
        return SupportStatus.BLOCKED
    if not has_evidence:
        return SupportStatus.EMPTY
    has_high_conflict = any(cf.severity == "high" for cf in conflict.contradictions)
    if has_high_conflict:
        return SupportStatus.CONFLICTED
    aggregate = score.aggregate()
    if aggregate >= 0.70 and score.direct_support_score >= 0.40:
        return SupportStatus.PASS
    if aggregate >= 0.40:
        return SupportStatus.WEAK_WITH_CAVEATS
    return SupportStatus.WEAK


def _disposition_for(status: SupportStatus) -> RecommendedDisposition:
    return {
        SupportStatus.PASS: RecommendedDisposition.PROCEED,
        SupportStatus.WEAK_WITH_CAVEATS: RecommendedDisposition.PROCEED_WITH_CAVEAT,
        SupportStatus.WEAK: RecommendedDisposition.ABSTAIN,
        SupportStatus.CONFLICTED: RecommendedDisposition.HUMAN_REVIEW,
        SupportStatus.EMPTY: RecommendedDisposition.FALLBACK_R5,
        SupportStatus.BLOCKED: RecommendedDisposition.ABSTAIN,
    }[status]


def verify_and_score(
    shaped: ShapedEvidenceSet,
    *,
    request_id: str,
    target: SupportTarget,
    conflict_report: ConflictGapReport,
) -> EvidenceContract:
    """Convert ShapedEvidenceSet + ConflictGapReport into an EvidenceContract."""

    verified: list[str] = []
    for r in shaped.ranked:
        if r.bucket == EvidenceClass.EXCLUDED:
            continue
        if _verify_chunk(r):
            verified.append(r.chunk.candidate.chunk_id)

    cited_spans: list[str] = []
    source_ids: list[str] = []
    for r in shaped.ranked:
        if r.chunk.candidate.chunk_id not in verified:
            continue
        for anchor in r.chunk.citation_anchor_candidates:
            cited_spans.append(f"{r.chunk.canonical_source_path}#{anchor}")
        source_ids.append(r.chunk.canonical_source_path)

    by_class: dict[EvidenceClass, list[str]] = {ec: [] for ec in EvidenceClass}
    for r in shaped.ranked:
        if r.chunk.candidate.chunk_id in verified or r.bucket == EvidenceClass.EXCLUDED:
            by_class[r.bucket].append(r.chunk.candidate.chunk_id)

    score_breakdown = _score_breakdown_from(
        shaped, target=target, conflict_report=conflict_report,
    )

    has_evidence = bool(verified)
    acl_blocked = (
        not has_evidence
        and len(shaped.excluded) > 0
        and all(not r.chunk.quality.acl_clear for r in shaped.excluded)
    )
    status = _choose_status(
        score_breakdown,
        conflict_report,
        has_evidence=has_evidence,
        acl_blocked=acl_blocked,
    )
    aggregate = score_breakdown.aggregate()
    abstain = status in (SupportStatus.EMPTY, SupportStatus.WEAK, SupportStatus.BLOCKED) or aggregate < 0.20

    contradiction_pairs = tuple(
        (cf.source_a_chunk_id, cf.source_b_chunk_id)
        for cf in conflict_report.contradictions
    )
    unresolved_codes = tuple(g.gap_type.value for g in conflict_report.gaps)

    evidence_hmac = EvidenceContract.compute_hmac(
        plan_id=shaped.plan_id,
        request_id=request_id,
        verified_chunk_ids=verified,
        score_breakdown=score_breakdown,
    )

    return EvidenceContract(
        plan_id=shaped.plan_id,
        request_id=request_id,
        status=status,
        support_score=aggregate,
        score_breakdown=score_breakdown,
        verified_chunk_ids=tuple(verified),
        cited_span_refs=tuple(cited_spans),
        source_ids=tuple(dict.fromkeys(source_ids)),  # de-dupe preserving order
        evidence_classes={ec: tuple(ids) for ec, ids in by_class.items()},
        contradiction_chunk_pairs=contradiction_pairs,
        unresolved_gap_codes=unresolved_codes,
        recommended_disposition=_disposition_for(status),
        abstain_hint=abstain,
        evidence_hmac=evidence_hmac,
    )


__all__ = [
    "EvidenceContract",
    "ScoreBreakdown",
    "verify_and_score",
]
