"""C0.4 shape (dedupe/rerank/stratify/compress) + C0.4A contradiction/gap scan.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace

from agentic_core.L1_cognition.c0_context.types import (
    ContradictionFlag,
    ContradictionType,
    EvidenceClass,
    EvidenceItem,
    GapType,
    SupportTarget,
    UnresolvedGap,
)


@dataclass(frozen=True)
class ShapedEvidenceSet:
    """C0.4 output."""

    must_use: tuple[EvidenceItem, ...]
    supporting: tuple[EvidenceItem, ...]
    contradicts: tuple[EvidenceItem, ...]
    background: tuple[EvidenceItem, ...]
    definitions: tuple[EvidenceItem, ...]
    lineage: tuple[EvidenceItem, ...]
    excluded: tuple[tuple[EvidenceItem, str], ...]  # (item, exclusion_reason)
    token_estimate: int


@dataclass(frozen=True)
class ConflictGapReport:
    """C0.4A output."""

    contradiction_flags: tuple[ContradictionFlag, ...]
    unresolved_gaps: tuple[UnresolvedGap, ...]


def dedupe(items: list[EvidenceItem]) -> list[EvidenceItem]:
    """Collapse duplicate (source_id, span_ref); keep highest-authority."""
    by_key: dict[tuple[str, str], EvidenceItem] = {}
    for it in items:
        key = (it.source_id, it.span_ref)
        existing = by_key.get(key)
        if existing is None or it.authority_score > existing.authority_score:
            by_key[key] = it
    return list(by_key.values())


def stratify(
    items: list[EvidenceItem],
    *,
    must_use_authority: float = 0.85,
    supporting_authority: float = 0.50,
    background_authority: float = 0.25,
) -> ShapedEvidenceSet:
    """Partition items into the seven evidence classes per spec.

    Items already labeled with EvidenceClass keep that class (e.g.
    CONTRADICTS items from C0.4A).
    """
    must_use: list[EvidenceItem] = []
    supporting: list[EvidenceItem] = []
    contradicts: list[EvidenceItem] = []
    background: list[EvidenceItem] = []
    definitions: list[EvidenceItem] = []
    lineage: list[EvidenceItem] = []
    excluded: list[tuple[EvidenceItem, str]] = []
    token_estimate = 0
    for it in items:
        # Honor pre-labeled classes when present and not the default.
        cls = it.evidence_class
        if cls == EvidenceClass.CONTRADICTS:
            contradicts.append(it)
        elif cls == EvidenceClass.DEFINITIONS:
            definitions.append(it)
        elif cls == EvidenceClass.LINEAGE:
            lineage.append(it)
        elif cls == EvidenceClass.EXCLUDED:
            excluded.append((it, "pre-labeled excluded"))
            continue
        elif cls == EvidenceClass.MUST_USE:
            must_use.append(it)
        elif cls == EvidenceClass.BACKGROUND:
            background.append(it)
        else:
            # Default SUPPORTING — re-stratify by authority threshold.
            if it.authority_score >= must_use_authority:
                must_use.append(replace(it, evidence_class=EvidenceClass.MUST_USE))
            elif it.authority_score >= supporting_authority:
                supporting.append(it)
            elif it.authority_score >= background_authority:
                background.append(replace(it, evidence_class=EvidenceClass.BACKGROUND))
            else:
                excluded.append((it, f"authority {it.authority_score:.2f} below threshold"))
                continue
        token_estimate += it.token_cost
    return ShapedEvidenceSet(
        must_use=tuple(must_use),
        supporting=tuple(supporting),
        contradicts=tuple(contradicts),
        background=tuple(background),
        definitions=tuple(definitions),
        lineage=tuple(lineage),
        excluded=tuple(excluded),
        token_estimate=token_estimate,
    )


def compress_to_budget(
    shaped: ShapedEvidenceSet,
    *,
    max_token_context: int,
) -> ShapedEvidenceSet:
    """Trim BACKGROUND, then SUPPORTING, before touching MUST_USE / CONTRADICTS.

    Per spec:
    - preserve citation-bearing spans first
    - compress background before must-use
    - keep contradiction snippets even if uncomfortable
    """
    if max_token_context <= 0:
        raise ValueError("max_token_context must be > 0")

    def _budget(items: tuple[EvidenceItem, ...]) -> int:
        return sum(it.token_cost for it in items)

    must_keep = (
        _budget(shaped.must_use)
        + _budget(shaped.contradicts)
        + _budget(shaped.definitions)
    )
    if must_keep > max_token_context:
        raise ValueError(
            f"must-keep evidence ({must_keep} tokens) exceeds budget {max_token_context}; "
            "G9 budget gate would fail",
        )
    remaining = max_token_context - must_keep
    # Allocate to SUPPORTING first (higher priority than BACKGROUND per spec).
    trimmed_supporting: list[EvidenceItem] = []
    used = 0
    for it in shaped.supporting:
        if used + it.token_cost <= remaining:
            trimmed_supporting.append(it)
            used += it.token_cost
    remaining -= used
    # Then BACKGROUND fills any leftover budget.
    trimmed_background: list[EvidenceItem] = []
    used = 0
    for it in shaped.background:
        if used + it.token_cost <= remaining:
            trimmed_background.append(it)
            used += it.token_cost
    new_estimate = (
        must_keep
        + sum(it.token_cost for it in trimmed_supporting)
        + sum(it.token_cost for it in trimmed_background)
    )
    return ShapedEvidenceSet(
        must_use=shaped.must_use,
        supporting=tuple(trimmed_supporting),
        contradicts=shaped.contradicts,
        background=tuple(trimmed_background),
        definitions=shaped.definitions,
        lineage=shaped.lineage,
        excluded=shaped.excluded,
        token_estimate=new_estimate,
    )


# ---------------------------------------------------------------------------
# C0.4A — contradiction + gap scan.
# ---------------------------------------------------------------------------


def scan_contradictions_and_gaps(
    shaped: ShapedEvidenceSet,
    *,
    support_target: SupportTarget,
    high_stakes: bool,
) -> ConflictGapReport:
    """Detect contradictions surfaced in CONTRADICTS bucket + missing-coverage gaps."""
    flags: list[ContradictionFlag] = []
    # Contradiction flags — pair every CONTRADICTS item with the strongest
    # MUST_USE / SUPPORTING source. Use the item's source_id and the
    # highest-authority MUST_USE source as the pair.
    if shaped.contradicts:
        anchor = (
            max(shaped.must_use, key=lambda x: x.authority_score)
            if shaped.must_use
            else (
                max(shaped.supporting, key=lambda x: x.authority_score)
                if shaped.supporting
                else None
            )
        )
        for c_item in shaped.contradicts:
            anchor_source = anchor.source_id if anchor is not None else "unknown"
            flags.append(
                ContradictionFlag(
                    contradiction_type=_infer_contradiction_type(c_item, anchor),
                    source_a=c_item.source_id,
                    source_b=anchor_source,
                    severity=min(1.0, c_item.authority_score),
                    summary=f"contradiction at {c_item.span_ref}",
                ),
            )
    gaps: list[UnresolvedGap] = []
    # Gap detection per support_target.
    if support_target == SupportTarget.EXACT_QUOTE and not _has_exact_quote(shaped):
        gaps.append(UnresolvedGap(
            gap_type=GapType.MISSING_EXACT_QUOTE,
            severity=1.0,
            impact_on_answer="exact quote target not satisfied",
            suggested_next_step="add sparse/metadata search for the quoted term",
        ))
    if not shaped.must_use and (shaped.supporting or shaped.background):
        gaps.append(UnresolvedGap(
            gap_type=GapType.MISSING_DIRECT_SUPPORT,
            severity=0.8,
            impact_on_answer="downstream answer cannot be directly grounded",
            suggested_next_step="refine search; broaden authority threshold",
        ))
    if not shaped.must_use and not shaped.supporting:
        gaps.append(UnresolvedGap(
            gap_type=GapType.MISSING_DIRECT_SUPPORT,
            severity=1.0,
            impact_on_answer="empty evidence pool",
            suggested_next_step="abstain or fallback R5",
        ))
    if high_stakes and len({it.source_id for it in shaped.must_use + shaped.supporting}) < 2:
        gaps.append(UnresolvedGap(
            gap_type=GapType.MISSING_SOURCE_DIVERSITY,
            severity=0.7,
            impact_on_answer="single-source claim for high-stakes target",
            suggested_next_step="search additional source classes",
        ))
    if any(it.acl_status not in {"cleared", "default-allow"} for it in shaped.must_use):
        gaps.append(UnresolvedGap(
            gap_type=GapType.MISSING_TENANT_ACL_PROOF,
            severity=0.9,
            impact_on_answer="ACL not proven for must-use evidence",
            suggested_next_step="exclude or escalate to ACL verification",
        ))
    return ConflictGapReport(
        contradiction_flags=tuple(flags),
        unresolved_gaps=tuple(gaps),
    )


def _has_exact_quote(shaped: ShapedEvidenceSet) -> bool:
    """True iff the pool contains a stable-anchor item from a lane capable
    of exact-quote support.

    Per spec invariant **I5** (and ``i5_exact_claims_need_sparse_or_metadata``
    + ``exactness_score`` in contract.py), exact-quote claims MUST be backed
    by sparse / hybrid / metadata lanes; dense alone is not enough.

    Bug 1 fix (2026-04-26): the original implementation accepted only
    ``{sparse, hybrid}`` and would emit MISSING_EXACT_QUOTE even when an
    item came from the metadata lane with a valid span_ref \u2014 contradicting
    every other site that treats metadata as a valid exact-quote lane.
    """
    return any(
        it.retrieval_lane in {"sparse", "hybrid", "metadata"} and bool(it.span_ref)
        for it in shaped.must_use + shaped.supporting
    )


def _infer_contradiction_type(
    c_item: EvidenceItem,
    anchor: EvidenceItem | None,
) -> ContradictionType:
    """Heuristic mapping from item metadata to ContradictionType."""
    if anchor is None:
        return ContradictionType.SOURCE
    if c_item.source_class == "code" and anchor.source_class == "docs":
        return ContradictionType.CODE
    if c_item.source_class == "logs" or anchor.source_class == "logs":
        return ContradictionType.RUNTIME
    if c_item.source_class == "policy" or anchor.source_class == "policy":
        return ContradictionType.POLICY
    if c_item.freshness_status != anchor.freshness_status:
        return ContradictionType.TIME
    return ContradictionType.SOURCE


__all__ = [
    "ConflictGapReport",
    "ShapedEvidenceSet",
    "compress_to_budget",
    "dedupe",
    "scan_contradictions_and_gaps",
    "stratify",
]
