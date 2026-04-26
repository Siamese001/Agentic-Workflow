"""Per-evidence-class typed projections — spec lines 1041-1080.

The FinalEvidenceContract carries seven evidence classes (MUST_USE, SUPPORTING,
CONTRADICTS, BACKGROUND, DEFINITIONS, LINEAGE, EXCLUDED). The detailed spec
(C0 Context Engine_detailed.md, OUTPUT SCHEMA block) requires each class to
expose specific per-item fields, not just the raw HydratedChunk.

This module defines those typed projections and the helpers that build them
from a ShapedEvidenceSet. Projections are DERIVED VIEWS — they never carry
information not already present in the chunk + retrieval lane + ACL state.

Hard invariants:
- C0.I3 — every projection preserves source_id, version, ACL, and lane.
- C0.I11 — projections never contain answer text or routing decisions.
- C0.I12 — every public field is verified, labeled, budgeted, and ranked.
"""

from __future__ import annotations

from dataclasses import dataclass

from .hydration import HydratedChunk
from .verdicts import RetrievalLane


# Token cost is a heuristic — 1 token ≈ 4 characters of English text.
# Spec line 1052 requires `token_cost` per MUST_USE entry. The estimate is
# safe for prompt-budget hint computation; a real tokenizer can plug in later.
def estimate_token_cost(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def _freshness_status(h: HydratedChunk) -> str:
    """Spec line 1050. Tri-state freshness label."""
    if h.quality.source_version_current:
        return "current"
    if h.candidate.manifest.version or h.candidate.manifest.commit:
        return "versioned_stale"
    return "unknown"


def _acl_status(h: HydratedChunk) -> str:
    """Spec line 1051. Tri-state ACL label."""
    if h.quality.acl_clear:
        return "cleared"
    return "blocked"


def _primary_lane(h: HydratedChunk) -> str:
    """Spec line 1048 / 790 retrieval_lane projection (single label)."""
    lanes = h.candidate.found_by_lanes
    if not lanes:
        return RetrievalLane.DENSE.value
    # Stable order: prefer sparse > metadata > dense > others.
    for preferred in (
        RetrievalLane.SPARSE,
        RetrievalLane.METADATA,
        RetrievalLane.DENSE,
        RetrievalLane.GRAPH_SEED,
        RetrievalLane.CACHE,
        RetrievalLane.TRACE,
        RetrievalLane.CODE,
    ):
        if preferred in lanes:
            return preferred.value
    return lanes[0].value


def _quote_or_summary(h: HydratedChunk) -> str:
    """Spec line 1047. For MUST_USE we keep the raw span; for others we
    truncate so that downstream prompt assembly never gets a giant blob."""
    text = h.candidate.text or ""
    if len(text) <= 500:
        return text
    return text[:497] + "..."


def _span_ref(h: HydratedChunk) -> str:
    """Stable citation anchor — best of citation_anchor_candidates."""
    if h.citation_anchor_candidates:
        return h.citation_anchor_candidates[0]
    return ""


def _source_type(h: HydratedChunk) -> str:
    """Spec line 1045 — class label for the evidence."""
    return h.candidate.source_class.value


# ---------- typed projections ----------


@dataclass(frozen=True)
class MustUseEvidence:
    """Spec lines 1042-1052 — MUST_USE entry shape."""

    evidence_id: str
    source_id: str
    source_type: str
    span_ref: str
    quote_or_summary: str
    retrieval_lane: str
    authority_score: float
    freshness_status: str
    acl_status: str
    token_cost: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.authority_score <= 1.0:
            raise ValueError("authority_score must be in [0,1]")
        if self.token_cost < 0:
            raise ValueError("token_cost must be >= 0")


@dataclass(frozen=True)
class SupportingEvidence:
    """Spec lines 1053-1057 — SUPPORTING entry shape."""

    evidence_id: str
    source_id: str
    span_ref: str
    reason: str = ""


@dataclass(frozen=True)
class ContradictsEvidence:
    """Spec lines 1058-1063 — CONTRADICTS entry shape."""

    evidence_id: str
    source_id: str
    span_ref: str
    conflict_type: str
    conflict_summary: str = ""


@dataclass(frozen=True)
class BackgroundEvidence:
    """Spec lines 1064-1068 — BACKGROUND entry shape."""

    evidence_id: str
    source_id: str
    span_ref: str
    reason: str = ""


@dataclass(frozen=True)
class DefinitionEntry:
    """Spec lines 1069-1072 — DEFINITIONS entry shape."""

    term: str
    source_id: str
    span_ref: str


@dataclass(frozen=True)
class ExcludedEntry:
    """Spec lines 1078-1080 — EXCLUDED entry shape."""

    evidence_id: str
    exclusion_reason: str


# ---------- builders ----------


def project_must_use(h: HydratedChunk, *, authority_score: float) -> MustUseEvidence:
    return MustUseEvidence(
        evidence_id=h.candidate.chunk_id,
        source_id=h.canonical_source_path,
        source_type=_source_type(h),
        span_ref=_span_ref(h),
        quote_or_summary=_quote_or_summary(h),
        retrieval_lane=_primary_lane(h),
        authority_score=authority_score,
        freshness_status=_freshness_status(h),
        acl_status=_acl_status(h),
        token_cost=estimate_token_cost(h.candidate.text),
    )


def project_supporting(h: HydratedChunk, *, reason: str = "") -> SupportingEvidence:
    return SupportingEvidence(
        evidence_id=h.candidate.chunk_id,
        source_id=h.canonical_source_path,
        span_ref=_span_ref(h),
        reason=reason,
    )


def project_contradicts(
    h: HydratedChunk, *, conflict_type: str, conflict_summary: str = "",
) -> ContradictsEvidence:
    return ContradictsEvidence(
        evidence_id=h.candidate.chunk_id,
        source_id=h.canonical_source_path,
        span_ref=_span_ref(h),
        conflict_type=conflict_type,
        conflict_summary=conflict_summary,
    )


def project_background(h: HydratedChunk, *, reason: str = "") -> BackgroundEvidence:
    return BackgroundEvidence(
        evidence_id=h.candidate.chunk_id,
        source_id=h.canonical_source_path,
        span_ref=_span_ref(h),
        reason=reason,
    )


def project_definition(h: HydratedChunk, *, term: str = "") -> DefinitionEntry:
    return DefinitionEntry(
        term=term or h.candidate.chunk_id,
        source_id=h.canonical_source_path,
        span_ref=_span_ref(h),
    )


def project_excluded(h: HydratedChunk, *, reason: str) -> ExcludedEntry:
    return ExcludedEntry(
        evidence_id=h.candidate.chunk_id,
        exclusion_reason=reason,
    )


__all__ = [
    "BackgroundEvidence",
    "ContradictsEvidence",
    "DefinitionEntry",
    "ExcludedEntry",
    "MustUseEvidence",
    "SupportingEvidence",
    "estimate_token_cost",
    "project_background",
    "project_contradicts",
    "project_definition",
    "project_excluded",
    "project_must_use",
    "project_supporting",
]
