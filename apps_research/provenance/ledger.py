"""Per-claim provenance ledger — apps_research.

Closes a gap surfaced in `apps_research/SVP_ENGINEERING_REVIEW.md`: today's
ResearchResult exposes section-level provenance via SourceEntry references,
but individual claims within a section do not carry their own source links.
For SVP-bar narrative ("every claim is auditable to its source") the
provenance must be at the claim level.

Architecture (deliberate):
  - This module is **additive**. ``ResearchSection``/``ResearchResult``
    keep their existing shape. ``ClaimWithProvenance`` is a new model
    that the research engine can populate when running in
    ``ProvenanceMode.PER_CLAIM``.
  - The ledger is a **lookup-only** structure — building it does NOT
    mutate the ResearchResult. Callers can attach the ledger as
    sidecar data (e.g. via a `claim_provenance` extra field, or
    serialize alongside the result).
  - Validation is **strict** — a claim with zero supporting sources or
    references to unknown source_ids fails the contract. Callers can
    surface validation errors in ``ResearchResult.gate_violations``.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P3 NEXT_STEP)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProvenanceMode(str, Enum):
    """Which level of provenance the research run produced."""

    NONE = "none"
    SECTION = "section"
    PER_CLAIM = "per_claim"


class ConfidenceBand(str, Enum):
    """Discrete confidence buckets for a claim — easier to communicate
    than raw floats and matches how SVPs read research output."""

    HIGH = "high"        # ≥ 0.85
    MEDIUM = "medium"    # 0.60 - 0.85
    LOW = "low"          # 0.40 - 0.60
    SPECULATIVE = "speculative"  # < 0.40

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceBand":
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"score must be in [0, 1], got {score}")
        if score >= 0.85:
            return cls.HIGH
        if score >= 0.60:
            return cls.MEDIUM
        if score >= 0.40:
            return cls.LOW
        return cls.SPECULATIVE


class ClaimWithProvenance(BaseModel):
    """A single research claim with explicit per-claim source references.

    The claim text MUST be supported by at least one source from the
    parent ResearchResult's source list. The resolution / validation step
    is handled by :class:`ProvenanceLedger`, which checks that every
    ``supporting_source_id`` resolves to a real ``SourceEntry``.
    """

    model_config = ConfigDict(frozen=True)

    claim_id: str = Field(..., min_length=1, description="Stable id within the result")
    text: str = Field(..., min_length=10, description="The claim itself")
    supporting_source_ids: tuple[str, ...] = Field(
        ..., description="One or more source_id values from the parent ResearchResult.sources",
    )
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_band: ConfidenceBand
    section_id: str | None = Field(None, description="Optional parent section id")

    @field_validator("supporting_source_ids", mode="before")
    @classmethod
    def _coerce_to_tuple(cls, v):
        # Allow lists in JSON input → tuple internally.
        if isinstance(v, list):
            return tuple(v)
        return v

    @field_validator("supporting_source_ids")
    @classmethod
    def _at_least_one_source(cls, v):
        if not v:
            raise ValueError("a claim with provenance MUST cite at least one source")
        return v


@dataclass(frozen=True)
class ProvenanceValidationResult:
    """Result of validating a ledger against the parent SourceEntry pool."""

    passed: bool
    n_claims: int
    n_orphan_claims: int
    """Claims whose supporting_source_ids reference unknown source_ids."""
    orphan_claim_ids: tuple[str, ...]
    n_unsupported_sources: int
    """SourceEntries with no claims pointing to them — soft warning, not fail."""
    unsupported_source_ids: tuple[str, ...]
    violation_strings: tuple[str, ...]


class ProvenanceLedger:
    """Builder + validator for per-claim provenance.

    Usage:
        ledger = ProvenanceLedger()
        for claim in extract_claims(result):
            ledger.add(claim)
        verdict = ledger.validate(known_source_ids={s.source_id for s in result.sources})
        if not verdict.passed:
            result.gate_violations.extend(verdict.violation_strings)
    """

    def __init__(self) -> None:
        self._claims: list[ClaimWithProvenance] = []

    def add(self, claim: ClaimWithProvenance) -> None:
        self._claims.append(claim)

    def add_many(self, claims: Iterable[ClaimWithProvenance]) -> None:
        self._claims.extend(claims)

    @property
    def claims(self) -> tuple[ClaimWithProvenance, ...]:
        return tuple(self._claims)

    def validate(self, known_source_ids: Iterable[str]) -> ProvenanceValidationResult:
        known = set(known_source_ids)
        cited: set[str] = set()
        orphan_claims: list[str] = []
        violations: list[str] = []

        for claim in self._claims:
            unknown_refs = [sid for sid in claim.supporting_source_ids if sid not in known]
            if unknown_refs:
                orphan_claims.append(claim.claim_id)
                violations.append(
                    f"PROVENANCE: claim {claim.claim_id!r} cites unknown sources "
                    f"{unknown_refs!r}"
                )
            cited.update(claim.supporting_source_ids)

        unsupported = sorted(known - cited)
        passed = len(orphan_claims) == 0
        return ProvenanceValidationResult(
            passed=passed,
            n_claims=len(self._claims),
            n_orphan_claims=len(orphan_claims),
            orphan_claim_ids=tuple(orphan_claims),
            n_unsupported_sources=len(unsupported),
            unsupported_source_ids=tuple(unsupported),
            violation_strings=tuple(violations),
        )

    def to_jsonable(self) -> list[dict]:
        """Serialize the ledger as a list of dicts (for sidecar export)."""
        return [c.model_dump(mode="json") for c in self._claims]


_CLAIM_TYPE_TO_BAND: dict[str, ConfidenceBand] = {
    "direct_evidence": ConfidenceBand.HIGH,
    "interpretation": ConfidenceBand.MEDIUM,
    "analyst_inference": ConfidenceBand.LOW,
    "assumption": ConfidenceBand.SPECULATIVE,
}

_CLAIM_TYPE_TO_SCORE: dict[str, float] = {
    "direct_evidence": 0.92,
    "interpretation": 0.72,
    "analyst_inference": 0.50,
    "assumption": 0.30,
}


def _split_into_claim_sentences(body: str, *, min_len: int = 10) -> list[str]:
    """Pragmatic sentence splitter for skeleton — splits on '. ' and '.\\n'.

    Real per-claim provenance extraction would use proper sentence tokenization
    (spaCy / NLTK) — this is the structural skeleton. Filters out fragments
    shorter than ``min_len`` chars after strip.
    """
    if not body:
        return []
    # Normalize newlines, then split on sentence terminators followed by space.
    chunks: list[str] = []
    buf = ""
    for ch in body.replace("\n", " "):
        buf += ch
        if ch in ".!?" and len(buf) >= min_len:
            chunks.append(buf.strip())
            buf = ""
    if buf.strip():
        chunks.append(buf.strip())
    return [c for c in chunks if len(c) >= min_len]


def build_ledger_from_sections(sections, *, claim_id_prefix: str = "claim"):
    """Build a ProvenanceLedger from a list of ResearchSection objects.

    Each section's body is split into claim-level sentences; every sentence
    inherits the section's ``sources`` list. The section's ``claim_type``
    drives the ConfidenceBand and a default confidence_score (the engine
    can override per-claim later when scoring is added).

    Args:
        sections: Iterable of ResearchSection (duck-typed — needs
            ``section_id``, ``body``, ``sources``, ``claim_type``).
        claim_id_prefix: Prefix for generated claim ids
            (``{prefix}-{section_id}-{n}``).

    Returns:
        ProvenanceLedger populated with one ClaimWithProvenance per
        extracted sentence. Empty ledger when no sections produce
        extractable claims.
    """
    ledger = ProvenanceLedger()
    for section in sections:
        sources = tuple(getattr(section, "sources", ()) or ())
        if not sources:
            continue  # Section with no sources cannot contribute provenance.
        claim_type = getattr(section, "claim_type", "interpretation")
        band = _CLAIM_TYPE_TO_BAND.get(claim_type, ConfidenceBand.MEDIUM)
        score = _CLAIM_TYPE_TO_SCORE.get(claim_type, 0.7)
        sentences = _split_into_claim_sentences(getattr(section, "body", "") or "")
        for idx, sentence in enumerate(sentences):
            ledger.add(
                ClaimWithProvenance(
                    claim_id=f"{claim_id_prefix}-{section.section_id}-{idx + 1}",
                    text=sentence,
                    supporting_source_ids=sources,
                    confidence_score=score,
                    confidence_band=band,
                    section_id=section.section_id,
                )
            )
    return ledger


__all__ = [
    "ClaimWithProvenance",
    "ConfidenceBand",
    "ProvenanceLedger",
    "ProvenanceMode",
    "ProvenanceValidationResult",
    "build_ledger_from_sections",
]
