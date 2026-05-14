"""Generic C0 evidence metrics extractor.

Derives a structured metrics summary from a ``FinalEvidenceContract`` without
any app-specific logic.  Apps supply a ``SupportTarget`` (declarative) that
drives ``support_target_met`` — the extractor never hard-codes which evidence
sources constitute sufficiency.

W2 invariants
-------------
- Zero imports from ``apps_rg.*`` or any other ``apps_*`` package.
- ``support_target_met`` is computed against the caller-supplied target, not
  inferred from evidence field names.
- ``PARTIAL`` is not a permitted ``support_status`` value.  Any contract that
  carries ``PARTIAL`` is coerced to ``WEAK_WITH_CAVEATS`` by the extractor
  and a warning is surfaced in ``coercion_warnings``.
- Returns a plain ``dataclass`` (typed dict equivalent); no I/O, no retrieval.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    EvidenceItem,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    STATUS_UNKNOWN,
)

# ---------------------------------------------------------------------------
# Canonical enum — the only values this extractor will ever emit.
# ---------------------------------------------------------------------------

CANONICAL_SUPPORT_STATUS_VALUES: frozenset[str] = frozenset({
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    STATUS_UNKNOWN,
})

#: Values that are NOT in the canonical set and must be coerced.
_COERCE_TO_WEAK: frozenset[str] = frozenset({"PARTIAL", "WEAK"})


# ---------------------------------------------------------------------------
# Support target (app-supplied, declarative)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SupportTarget:
    """Declarative description of what constitutes a sufficient evidence set.

    The extractor computes ``support_target_met`` by checking whether
    ``required_source_prefixes`` are all represented in the FEC's
    ``retrieval_sources``.  Apps supply this; the extractor never infers it
    from field names.

    Parameters
    ----------
    required_source_prefixes:
        Iterable of source-prefix strings that MUST be present in
        ``FinalEvidenceContract.retrieval_sources`` for the target to be met.
        Example: ``("jd_payload", "resume_payload")`` — both must appear as a
        prefix of at least one retrieval source entry.
    label:
        Human-readable name for this target (for logging / metrics output).
    """

    required_source_prefixes: tuple[str, ...]
    label: str = "default"

    @classmethod
    def from_prefix_list(
        cls,
        prefixes: Sequence[str],
        label: str = "default",
    ) -> "SupportTarget":
        return cls(required_source_prefixes=tuple(prefixes), label=label)


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvidenceMetrics:
    """Structured metrics derived from a ``FinalEvidenceContract``.

    All fields are safe defaults — callers MUST NOT treat absent/zero fields
    as implying PASS.

    support_status
        Canonical enum value.  PARTIAL is forbidden; see ``coercion_warnings``.
    support_target_met
        True iff every required_source_prefix in the supplied ``SupportTarget``
        appears in ``retrieval_sources``.  Computed from the target, not
        hard-coded.
    evidence_count
        Total evidence items in the FEC.
    retrieval_sources
        Tuple of source identifiers from the FEC.
    excluded_evidence_refs
        Tuple of excluded evidence refs from the FEC.
    blocked_source_refs
        Tuple of retrieval sources whose items carry ``support_status=BLOCKED``.
    confidence_scores
        Per-item confidence scores (0.0 when not set).
    freshness_receipts
        Tuple of freshness receipt strings from the FEC.
    citation_map
        Tuple of (evidence_id, citation_anchor) pairs from the FEC.
    final_evidence_digest
        Provenance digest from the FEC.
    support_score_profile
        Dict of source-class → item-count for normative items.
    coercion_warnings
        List of warnings emitted when a non-canonical status was coerced.
    """

    support_status: str
    support_target_met: bool
    support_target_label: str
    evidence_count: int
    retrieval_sources: tuple[str, ...]
    excluded_evidence_refs: tuple[str, ...]
    blocked_source_refs: tuple[str, ...]
    confidence_scores: tuple[float, ...]
    freshness_receipts: tuple[str, ...]
    citation_map: tuple[tuple[str, str], ...]
    final_evidence_digest: str
    support_score_profile: dict[str, int]
    coercion_warnings: tuple[str, ...]


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

def extract_evidence_metrics(
    fec: FinalEvidenceContract,
    support_target: SupportTarget,
) -> EvidenceMetrics:
    """Extract generic retrieval metrics from a ``FinalEvidenceContract``.

    This function is app-agnostic.  It reads the FEC fields and the
    caller-supplied ``support_target``; it never inspects app_id or imports
    from any ``apps_*`` module.

    Parameters
    ----------
    fec:
        A populated ``FinalEvidenceContract``.
    support_target:
        Declarative target supplied by the calling app or profile loader.
        Drives ``support_target_met`` computation.

    Returns
    -------
    EvidenceMetrics
        Structured metrics summary.  Never raises — returns a safe-default
        ``EvidenceMetrics`` on unexpected input.
    """
    coercion_warnings: list[str] = []

    # --- support_status coercion ---
    raw_status = getattr(fec, "support_status", STATUS_UNKNOWN) or STATUS_UNKNOWN
    if raw_status in _COERCE_TO_WEAK:
        coercion_warnings.append(
            f"support_status={raw_status!r} is not in the canonical enum; "
            f"coerced to {SUPPORT_STATUS_WEAK_WITH_CAVEATS!r}. "
            "PARTIAL is forbidden (W2 hard rule §4)."
        )
        support_status = SUPPORT_STATUS_WEAK_WITH_CAVEATS
    elif raw_status not in CANONICAL_SUPPORT_STATUS_VALUES:
        coercion_warnings.append(
            f"support_status={raw_status!r} is unrecognised; coerced to UNKNOWN."
        )
        support_status = STATUS_UNKNOWN
    else:
        support_status = raw_status

    # --- retrieval_sources ---
    retrieval_sources: tuple[str, ...] = tuple(
        getattr(fec, "retrieval_sources", ()) or ()
    )

    # --- support_target_met: computed from supplied target, not field names ---
    support_target_met = _compute_target_met(retrieval_sources, support_target)

    # --- evidence items ---
    items: tuple[EvidenceItem, ...] = tuple(
        getattr(fec, "evidence_items", ()) or ()
    )
    confidence_scores = tuple(
        float(getattr(item, "confidence_score", 0.0)) for item in items
    )

    # --- blocked sources ---
    blocked_source_refs = tuple(
        item.source
        for item in items
        if getattr(item, "support_status", None) == SUPPORT_STATUS_BLOCKED
    )

    # --- support_score_profile: source-class → item count ---
    support_score_profile: dict[str, int] = {}
    for item in items:
        src = getattr(item, "source", "")
        if ":" in src:
            source_class = src.split(":", 1)[1]
        else:
            source_class = src
        support_score_profile[source_class] = (
            support_score_profile.get(source_class, 0) + 1
        )

    # --- citation_map ---
    raw_citation_map = getattr(fec, "citation_map", ()) or ()
    citation_map: tuple[tuple[str, str], ...] = tuple(
        (str(pair[0]), str(pair[1])) for pair in raw_citation_map if len(pair) == 2
    )

    return EvidenceMetrics(
        support_status=support_status,
        support_target_met=support_target_met,
        support_target_label=support_target.label,
        evidence_count=len(items),
        retrieval_sources=retrieval_sources,
        excluded_evidence_refs=tuple(
            getattr(fec, "excluded_evidence_refs", ()) or ()
        ),
        blocked_source_refs=blocked_source_refs,
        confidence_scores=confidence_scores,
        freshness_receipts=tuple(
            getattr(fec, "freshness_receipts", ()) or ()
        ),
        citation_map=citation_map,
        final_evidence_digest=str(
            getattr(fec, "final_evidence_digest", "")
            or getattr(fec, "evidence_digest", "")
            or ""
        ),
        support_score_profile=support_score_profile,
        coercion_warnings=tuple(coercion_warnings),
    )


def _compute_target_met(
    retrieval_sources: tuple[str, ...],
    target: SupportTarget,
) -> bool:
    """Return True iff every required prefix in target is represented.

    Matching is prefix-based: a retrieval source ``"jd_payload:jd_text"``
    satisfies prefix ``"jd_payload"``.

    This is the ONLY place ``support_target_met`` is derived.  It is driven
    entirely by the caller-supplied ``SupportTarget``; no field names are
    hard-coded here.
    """
    if not target.required_source_prefixes:
        return True
    for prefix in target.required_source_prefixes:
        if not any(src.startswith(prefix) for src in retrieval_sources):
            return False
    return True
