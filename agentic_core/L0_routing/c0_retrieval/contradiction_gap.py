"""C0.4A CONTRADICTION + GAP SCAN.

Spec: C0 Context Engine.md lines 533-563. 8 contradiction types × 9 gap
types. Pure-data; produces ConflictGapReport for the EvidenceContract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .graph_traverse import GraphExpandedEvidencePool
from .hydration import HydratedChunk
from .verdicts import (
    EXACTNESS_REQUIRED,
    ContradictionType,
    GapType,
    GraphRelation,
    RefineTactic,
    SourceClass,
    SupportTarget,
)


@dataclass(frozen=True)
class ContradictionFlag:
    """One credible disagreement between sources."""

    contradiction_type: ContradictionType
    source_a_chunk_id: str
    source_b_chunk_id: str
    severity: str = "medium"  # low | medium | high
    summary: str = ""
    required_downstream_behavior: str = "caveat"  # caveat | abstain | reroute

    def __post_init__(self) -> None:
        if self.severity not in ("low", "medium", "high"):
            raise ValueError(f"invalid severity {self.severity!r}")
        if self.required_downstream_behavior not in ("caveat", "abstain", "reroute"):
            raise ValueError(
                f"invalid required_downstream_behavior "
                f"{self.required_downstream_behavior!r}",
            )


@dataclass(frozen=True)
class GapFlag:
    """One missing piece of support."""

    gap_type: GapType
    severity: str = "medium"
    impact_on_answer: str = ""
    suggested_next_step: RefineTactic = RefineTactic.REWRITE

    def __post_init__(self) -> None:
        if self.severity not in ("low", "medium", "high"):
            raise ValueError(f"invalid severity {self.severity!r}")


@dataclass(frozen=True)
class ConflictGapReport:
    """Spec line 561 — output of C0.4A."""

    plan_id: str
    contradictions: tuple[ContradictionFlag, ...]
    gaps: tuple[GapFlag, ...]
    likely_failure_modes: tuple[str, ...] = field(default_factory=tuple)
    recommended_refine_tactic: RefineTactic | None = None

    def contradiction_chunk_ids(self) -> frozenset[str]:
        ids: set[str] = set()
        for cf in self.contradictions:
            ids.add(cf.source_a_chunk_id)
            ids.add(cf.source_b_chunk_id)
        return frozenset(ids)


# ----- detection helpers -----


def _scope_mismatch(a: HydratedChunk, b: HydratedChunk) -> bool:
    am, bm = a.candidate.manifest, b.candidate.manifest
    if am.tenant and bm.tenant and am.tenant != bm.tenant:
        return True
    if am.region and bm.region and am.region != bm.region:
        return True
    return False


def _time_mismatch(a: HydratedChunk, b: HydratedChunk) -> bool:
    am, bm = a.candidate.manifest, b.candidate.manifest
    if am.timestamp and bm.timestamp and am.timestamp[:10] != bm.timestamp[:10]:
        # different ISO date
        return True
    return False


def _version_mismatch(a: HydratedChunk, b: HydratedChunk) -> bool:
    am, bm = a.candidate.manifest, b.candidate.manifest
    return bool(am.version) and bool(bm.version) and am.version != bm.version


def _cross_class_pair(
    a: HydratedChunk, b: HydratedChunk, class_a: SourceClass, class_b: SourceClass,
) -> bool:
    return (
        a.candidate.source_class == class_a and b.candidate.source_class == class_b
    ) or (
        a.candidate.source_class == class_b and b.candidate.source_class == class_a
    )


def _detect_contradictions(
    expanded: GraphExpandedEvidencePool,
) -> list[ContradictionFlag]:
    """Detect contradictions across the full pool (originals + neighbors).

    Spec lines 539-547 — eight contradiction types.
    """
    flags: list[ContradictionFlag] = []
    chunks = expanded.all_chunks

    # Graph-derived contradicts/supersedes hops are direct evidence.
    for hop in expanded.traverse.hops:
        if hop.relation == GraphRelation.CONTRADICTS:
            flags.append(
                ContradictionFlag(
                    contradiction_type=ContradictionType.SOURCE,
                    source_a_chunk_id=hop.src_chunk_id,
                    source_b_chunk_id=hop.dst_chunk_id,
                    severity="high",
                    summary="graph edge: contradicts",
                    required_downstream_behavior="caveat",
                )
            )
        elif hop.relation == GraphRelation.SUPERSEDES:
            flags.append(
                ContradictionFlag(
                    contradiction_type=ContradictionType.VERSION,
                    source_a_chunk_id=hop.src_chunk_id,
                    source_b_chunk_id=hop.dst_chunk_id,
                    severity="medium",
                    summary="graph edge: supersedes (newer source wins)",
                    required_downstream_behavior="caveat",
                )
            )

    # Pairwise heuristics across the pool (cap at first 200 pairs to bound work).
    pair_count = 0
    for i, a in enumerate(chunks):
        for b in chunks[i + 1:]:
            pair_count += 1
            if pair_count > 200:
                break
            if a.candidate.chunk_id == b.candidate.chunk_id:
                continue
            if _scope_mismatch(a, b):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.SCOPE,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="high",
                        summary="tenant or region mismatch",
                        required_downstream_behavior="abstain",
                    )
                )
            elif _version_mismatch(a, b):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.VERSION,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="medium",
                        summary="document version mismatch",
                        required_downstream_behavior="caveat",
                    )
                )
            elif _time_mismatch(a, b):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.TIME,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="low",
                        summary="differing effective timestamps",
                        required_downstream_behavior="caveat",
                    )
                )
            if _cross_class_pair(a, b, SourceClass.DOCS, SourceClass.CODE):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.CODE,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="medium",
                        summary="docs ↔ code pair — verify alignment",
                        required_downstream_behavior="caveat",
                    )
                )
            elif _cross_class_pair(a, b, SourceClass.DOCS, SourceClass.LOGS):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.RUNTIME,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="medium",
                        summary="docs ↔ runtime traces — possible drift",
                        required_downstream_behavior="caveat",
                    )
                )
            elif _cross_class_pair(a, b, SourceClass.POLICY, SourceClass.CODE):
                flags.append(
                    ContradictionFlag(
                        contradiction_type=ContradictionType.POLICY,
                        source_a_chunk_id=a.candidate.chunk_id,
                        source_b_chunk_id=b.candidate.chunk_id,
                        severity="high",
                        summary="policy ↔ implementation — verify legal alignment",
                        required_downstream_behavior="abstain",
                    )
                )
        if pair_count > 200:
            break
    return flags


def _detect_gaps(
    expanded: GraphExpandedEvidencePool,
    *,
    target: SupportTarget,
    have_contradictions: bool,
) -> list[GapFlag]:
    """Spec lines 549-558 — nine gap types."""
    gaps: list[GapFlag] = []
    chunks = expanded.all_chunks

    if not chunks:
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_DIRECT_SUPPORT,
                severity="high",
                impact_on_answer="No evidence retrieved — answer cannot be grounded",
                suggested_next_step=RefineTactic.BROADEN,
            )
        )
        return gaps

    # No exact-quote-bearing chunk for an exact target?
    if target in EXACTNESS_REQUIRED:
        from .verdicts import RetrievalLane
        any_sparse = any(
            RetrievalLane.SPARSE in c.candidate.found_by_lanes for c in chunks
        )
        if not any_sparse:
            gaps.append(
                GapFlag(
                    gap_type=GapType.MISSING_EXACT_QUOTE,
                    severity="high",
                    impact_on_answer=(
                        "Exact-target retrieval has no sparse-lane support; "
                        "C0.I5 violated"
                    ),
                    suggested_next_step=RefineTactic.HYBRIDIZE,
                )
            )

    if not any(c.quality.source_version_current for c in chunks):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_CURRENT_VERSION,
                severity="medium",
                impact_on_answer="No source carries a current version stamp",
                suggested_next_step=RefineTactic.FRESHEN,
            )
        )

    if not any(c.quality.citation_anchor_stable for c in chunks):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_CITATION_ANCHOR,
                severity="medium",
                impact_on_answer="No retrievable citation anchor — quote distortion risk",
                suggested_next_step=RefineTactic.NARROW,
            )
        )

    # Source diversity: at least 2 distinct source classes for non-trivial targets.
    classes = {c.candidate.source_class for c in chunks}
    if len(classes) < 2 and target != SupportTarget.EXACT_QUOTE:
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_SOURCE_DIVERSITY,
                severity="low",
                impact_on_answer="Single-source evidence — confirmation bias risk",
                suggested_next_step=RefineTactic.BROADEN,
            )
        )

    if not any(c.quality.acl_clear for c in chunks):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_TENANT_PROOF,
                severity="high",
                impact_on_answer="No ACL-cleared evidence",
                suggested_next_step=RefineTactic.ABSTAIN,
            )
        )

    if target == SupportTarget.CODE_LOCATION and not any(
        c.candidate.source_class == SourceClass.CODE for c in chunks
    ):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_VALIDATION,
                severity="high",
                impact_on_answer="CODE_LOCATION target has no code-class evidence",
                suggested_next_step=RefineTactic.NARROW,
            )
        )

    if target in (
        SupportTarget.INCIDENT_EVIDENCE,
        SupportTarget.ROOT_CAUSE_RANKING,
    ) and not any(c.candidate.manifest.timestamp for c in chunks):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_TIME_RANGE,
                severity="medium",
                impact_on_answer="Incident/RCA target with no timestamps",
                suggested_next_step=RefineTactic.NARROW,
            )
        )

    if target == SupportTarget.POLICY_CLAUSE and not any(
        c.candidate.manifest.version for c in chunks
    ):
        gaps.append(
            GapFlag(
                gap_type=GapType.MISSING_OWNER,
                severity="high",
                impact_on_answer="Policy target with no version/owner",
                suggested_next_step=RefineTactic.FRESHEN,
            )
        )

    return gaps


def _likely_failure_modes(
    contradictions: Iterable[ContradictionFlag],
    gaps: Iterable[GapFlag],
) -> list[str]:
    modes: set[str] = set()
    for cf in contradictions:
        if cf.contradiction_type == ContradictionType.CODE:
            modes.add("docs_vs_code_mismatch")
        if cf.contradiction_type == ContradictionType.RUNTIME:
            modes.add("runtime_vs_design_mismatch")
        if cf.contradiction_type == ContradictionType.SCOPE:
            modes.add("wrong_tenant_evidence")
        if cf.contradiction_type == ContradictionType.VERSION:
            modes.add("stale_policy_answer")
    for g in gaps:
        if g.gap_type == GapType.MISSING_EXACT_QUOTE:
            modes.add("dense_only_hallucination")
        if g.gap_type == GapType.MISSING_CITATION_ANCHOR:
            modes.add("quote_distortion")
        if g.gap_type == GapType.MISSING_SOURCE_DIVERSITY:
            modes.add("fake_confidence")
        if g.gap_type == GapType.MISSING_DIRECT_SUPPORT:
            modes.add("unsupported_synthesis")
    return sorted(modes)


def _recommend_tactic(
    gaps: list[GapFlag], contradictions: list[ContradictionFlag],
) -> RefineTactic | None:
    if not gaps and not contradictions:
        return None
    # Highest-severity gap first.
    sev_rank = {"high": 3, "medium": 2, "low": 1}
    if gaps:
        gaps_sorted = sorted(gaps, key=lambda g: sev_rank.get(g.severity, 0), reverse=True)
        return gaps_sorted[0].suggested_next_step
    return RefineTactic.NARROW


def scan_conflicts_and_gaps(
    expanded: GraphExpandedEvidencePool,
    *,
    target: SupportTarget,
) -> ConflictGapReport:
    contradictions = _detect_contradictions(expanded)
    gaps = _detect_gaps(
        expanded, target=target, have_contradictions=bool(contradictions),
    )
    return ConflictGapReport(
        plan_id=expanded.plan_id,
        contradictions=tuple(contradictions),
        gaps=tuple(gaps),
        likely_failure_modes=tuple(_likely_failure_modes(contradictions, gaps)),
        recommended_refine_tactic=_recommend_tactic(gaps, contradictions),
    )


__all__ = [
    "ConflictGapReport",
    "ContradictionFlag",
    "GapFlag",
    "scan_conflicts_and_gaps",
]
