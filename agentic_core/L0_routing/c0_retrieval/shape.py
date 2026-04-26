"""C0.4 SHAPE / RERANK / STRATIFY.

Spec: C0 Context Engine.md lines 455-530. Pure-data; produces a ranked,
stratified, compressed evidence set ready for the EvidenceContract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .graph_traverse import GraphExpandedEvidencePool
from .hydration import HydratedChunk
from .verdicts import EvidenceClass, RetrievalLane, SupportTarget, EXACTNESS_REQUIRED


class RerankSignal(str, Enum):
    """Spec lines 474-488 — 14 rerank signals."""

    RELEVANCE = "relevance_to_support_target"
    DIRECTNESS = "directness_of_support"
    AUTHORITY = "source_authority"
    FRESHNESS = "freshness_match"
    CITATION_STABILITY = "citation_anchor_stability"
    GRAPH_PROXIMITY = "graph_proximity"
    EXACT_LEXICAL = "exact_lexical_support"
    DENSE_SEMANTIC = "dense_semantic_support"
    METADATA_FIT = "metadata_fit"
    CONTRADICTION_VALUE = "contradiction_value"
    SOURCE_DIVERSITY = "source_diversity"
    COVERAGE = "coverage_contribution"
    QUOTE_DISTORTION_RISK = "risk_of_quote_distortion"
    ACL_CLEANLINESS = "acl_cleanliness"


@dataclass(frozen=True)
class CompressionManifest:
    """Spec lines 508-514 + 518 — what was kept vs trimmed and why."""

    must_keep_chunk_ids: tuple[str, ...]
    trimmed_chunk_ids: tuple[str, ...]
    near_duplicates: tuple[tuple[str, str], ...]  # (kept, dropped)
    excluded_with_reasons: tuple[tuple[str, str], ...]  # (chunk_id, reason)
    total_token_estimate: int = 0


@dataclass(frozen=True)
class RankedChunk:
    """A HydratedChunk with computed signals + final ranking score."""

    chunk: HydratedChunk
    signals: dict[RerankSignal, float] = field(default_factory=dict)
    final_score: float = 0.0
    bucket: EvidenceClass = EvidenceClass.SUPPORTING

    def __post_init__(self) -> None:
        if not 0.0 <= self.final_score <= 1.0:
            raise ValueError("final_score must be in [0,1]")
        for s, v in self.signals.items():
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"signal {s.value!r} value {v} out of [0,1]")


@dataclass(frozen=True)
class StratifiedBucket:
    """Spec lines 499-506 — one of MUST_USE/SUPPORTING/CONTRADICTS/etc."""

    evidence_class: EvidenceClass
    members: tuple[RankedChunk, ...]


@dataclass(frozen=True)
class ShapedEvidenceSet:
    """Spec lines 516-520 — output of C0.4."""

    plan_id: str
    ranked: tuple[RankedChunk, ...]
    must_use: tuple[RankedChunk, ...]
    supporting: tuple[RankedChunk, ...]
    contradicts: tuple[RankedChunk, ...]
    background: tuple[RankedChunk, ...]
    definitions: tuple[RankedChunk, ...]
    lineage: tuple[RankedChunk, ...]
    excluded: tuple[RankedChunk, ...]
    compression: CompressionManifest
    token_estimate: int = 0

    def buckets(self) -> tuple[StratifiedBucket, ...]:
        return (
            StratifiedBucket(EvidenceClass.MUST_USE, self.must_use),
            StratifiedBucket(EvidenceClass.SUPPORTING, self.supporting),
            StratifiedBucket(EvidenceClass.CONTRADICTS, self.contradicts),
            StratifiedBucket(EvidenceClass.BACKGROUND, self.background),
            StratifiedBucket(EvidenceClass.DEFINITIONS, self.definitions),
            StratifiedBucket(EvidenceClass.LINEAGE, self.lineage),
            StratifiedBucket(EvidenceClass.EXCLUDED, self.excluded),
        )


# ----- helpers -----

# Spec line 487: source authority is class-dependent.
_AUTHORITY_BY_CLASS: dict[str, float] = {
    "policy": 1.00,
    "code": 0.85,
    "docs": 0.80,
    "logs": 0.70,
    "tickets": 0.55,
    "tables": 0.65,
    "prior_artifacts": 0.75,
}


def _signal_relevance(c: HydratedChunk, target: SupportTarget) -> float:
    if target in EXACTNESS_REQUIRED:
        # exact targets reward sparse/metadata lanes more heavily
        return 1.0 if RetrievalLane.SPARSE in c.candidate.found_by_lanes else 0.5
    return 0.7


def _signal_directness(c: HydratedChunk) -> float:
    return c.candidate.scores.normalized_score or 0.5


def _signal_authority(c: HydratedChunk) -> float:
    return _AUTHORITY_BY_CLASS.get(c.candidate.source_class.value, 0.5)


def _signal_citation_stability(c: HydratedChunk) -> float:
    return 1.0 if c.quality.citation_anchor_stable else 0.0


def _signal_acl(c: HydratedChunk) -> float:
    return 1.0 if c.quality.acl_clear else 0.0


def _signal_quote_distortion_risk(c: HydratedChunk) -> float:
    risk = c.quality.chunk_boundary_risk.value
    return {"low": 0.05, "medium": 0.4, "high": 0.85}.get(risk, 0.5)


def _signal_exact_lexical(c: HydratedChunk) -> float:
    return 1.0 if RetrievalLane.SPARSE in c.candidate.found_by_lanes else 0.0


def _signal_dense_semantic(c: HydratedChunk) -> float:
    return 1.0 if RetrievalLane.DENSE in c.candidate.found_by_lanes else 0.0


def _signal_metadata_fit(c: HydratedChunk) -> float:
    return 1.0 if RetrievalLane.METADATA in c.candidate.found_by_lanes else 0.5


def _signal_graph_proximity(c: HydratedChunk) -> float:
    return 1.0 if RetrievalLane.GRAPH_SEED in c.candidate.found_by_lanes else 0.5


def _signal_freshness_match(c: HydratedChunk) -> float:
    return 1.0 if c.quality.source_version_current else 0.4


def _classify_bucket(
    c: HydratedChunk,
    *,
    contradiction_chunk_ids: frozenset[str],
    is_duplicate: bool,
    target: SupportTarget,
    final_score: float,
) -> EvidenceClass:
    if is_duplicate or not c.quality.acl_clear:
        return EvidenceClass.EXCLUDED
    if c.candidate.chunk_id in contradiction_chunk_ids:
        return EvidenceClass.CONTRADICTS
    if c.candidate.source_class.value in ("docs",) and "definition" in (c.candidate.text or "").lower()[:120]:
        # heuristic: a chunk explicitly containing a definition near the start is glossary
        return EvidenceClass.DEFINITIONS
    if final_score >= 0.75:
        return EvidenceClass.MUST_USE
    if final_score >= 0.40:
        return EvidenceClass.SUPPORTING
    return EvidenceClass.BACKGROUND


def _estimate_tokens(text: str) -> int:
    """Crude 4-char-per-token approximation."""
    return max(1, len(text) // 4)


def shape_pool(
    expanded: GraphExpandedEvidencePool,
    *,
    target: SupportTarget,
    max_token_context: int,
    contradiction_chunk_ids: frozenset[str] = frozenset(),
) -> ShapedEvidenceSet:
    """Run dedupe → rerank → stratify → compress.

    `contradiction_chunk_ids` is the precomputed set from C0.4A; this
    function does NOT scan for contradictions itself (separation of concerns).
    """
    chunks = expanded.all_chunks

    # ---- DEDUPE (spec lines 466-472) ----
    seen_text: dict[str, str] = {}  # text-prefix -> kept chunk_id
    near_dups: list[tuple[str, str]] = []
    duplicates: set[str] = set()
    for c in chunks:
        key = c.candidate.text.strip()[:200]
        if key in seen_text:
            kept = seen_text[key]
            duplicates.add(c.candidate.chunk_id)
            near_dups.append((kept, c.candidate.chunk_id))
        else:
            seen_text[key] = c.candidate.chunk_id

    # ---- RERANK ----
    ranked: list[RankedChunk] = []
    weights = {
        RerankSignal.RELEVANCE: 0.20,
        RerankSignal.DIRECTNESS: 0.15,
        RerankSignal.AUTHORITY: 0.10,
        RerankSignal.FRESHNESS: 0.05,
        RerankSignal.CITATION_STABILITY: 0.10,
        RerankSignal.EXACT_LEXICAL: 0.05,
        RerankSignal.DENSE_SEMANTIC: 0.05,
        RerankSignal.METADATA_FIT: 0.05,
        RerankSignal.GRAPH_PROXIMITY: 0.05,
        RerankSignal.QUOTE_DISTORTION_RISK: -0.10,  # penalty
        RerankSignal.ACL_CLEANLINESS: 0.10,  # gating signal
    }
    for c in chunks:
        sig = {
            RerankSignal.RELEVANCE: _signal_relevance(c, target),
            RerankSignal.DIRECTNESS: _signal_directness(c),
            RerankSignal.AUTHORITY: _signal_authority(c),
            RerankSignal.FRESHNESS: _signal_freshness_match(c),
            RerankSignal.CITATION_STABILITY: _signal_citation_stability(c),
            RerankSignal.EXACT_LEXICAL: _signal_exact_lexical(c),
            RerankSignal.DENSE_SEMANTIC: _signal_dense_semantic(c),
            RerankSignal.METADATA_FIT: _signal_metadata_fit(c),
            RerankSignal.GRAPH_PROXIMITY: _signal_graph_proximity(c),
            RerankSignal.QUOTE_DISTORTION_RISK: _signal_quote_distortion_risk(c),
            RerankSignal.ACL_CLEANLINESS: _signal_acl(c),
        }
        score = 0.0
        for s, w in weights.items():
            score += w * sig[s]
        # clamp
        score = max(0.0, min(1.0, score))
        bucket = _classify_bucket(
            c,
            contradiction_chunk_ids=contradiction_chunk_ids,
            is_duplicate=c.candidate.chunk_id in duplicates,
            target=target,
            final_score=score,
        )
        ranked.append(
            RankedChunk(
                chunk=c,
                signals=sig,
                final_score=score,
                bucket=bucket,
            )
        )

    ranked.sort(key=lambda r: r.final_score, reverse=True)

    # ---- STRATIFY ----
    must_use = tuple(r for r in ranked if r.bucket == EvidenceClass.MUST_USE)
    supporting = tuple(r for r in ranked if r.bucket == EvidenceClass.SUPPORTING)
    contradicts = tuple(r for r in ranked if r.bucket == EvidenceClass.CONTRADICTS)
    background = tuple(r for r in ranked if r.bucket == EvidenceClass.BACKGROUND)
    definitions = tuple(r for r in ranked if r.bucket == EvidenceClass.DEFINITIONS)
    lineage_b = tuple(r for r in ranked if r.bucket == EvidenceClass.LINEAGE)
    excluded = tuple(r for r in ranked if r.bucket == EvidenceClass.EXCLUDED)

    # ---- COMPRESS (spec lines 508-514) ----
    must_ids = tuple(r.chunk.candidate.chunk_id for r in must_use)
    excluded_with_reasons = tuple(
        (r.chunk.candidate.chunk_id,
         "ACL not clear" if not r.chunk.quality.acl_clear
         else "near-duplicate of higher-ranked chunk")
        for r in excluded
    )

    # Token-budget trim: keep MUST_USE first, then CONTRADICTS, then SUPPORTING.
    running = 0
    trimmed: list[str] = []
    keep_order: tuple[tuple[RankedChunk, ...], ...] = (
        must_use, contradicts, supporting, definitions, lineage_b, background,
    )
    protected = (must_use, contradicts)
    kept_chunks: set[str] = set()
    for bucket_members in keep_order:
        for ranked_chunk in bucket_members:
            t = _estimate_tokens(ranked_chunk.chunk.candidate.text)
            if running + t > max_token_context and bucket_members not in protected:
                trimmed.append(ranked_chunk.chunk.candidate.chunk_id)
                continue
            running += t
            kept_chunks.add(ranked_chunk.chunk.candidate.chunk_id)

    compression = CompressionManifest(
        must_keep_chunk_ids=must_ids,
        trimmed_chunk_ids=tuple(trimmed),
        near_duplicates=tuple(near_dups),
        excluded_with_reasons=excluded_with_reasons,
        total_token_estimate=running,
    )

    return ShapedEvidenceSet(
        plan_id=expanded.plan_id,
        ranked=tuple(ranked),
        must_use=must_use,
        supporting=supporting,
        contradicts=contradicts,
        background=background,
        definitions=definitions,
        lineage=lineage_b,
        excluded=excluded,
        compression=compression,
        token_estimate=running,
    )


__all__ = [
    "CompressionManifest",
    "RankedChunk",
    "RerankSignal",
    "ShapedEvidenceSet",
    "StratifiedBucket",
    "shape_pool",
]
