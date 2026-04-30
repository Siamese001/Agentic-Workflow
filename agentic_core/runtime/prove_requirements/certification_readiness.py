"""Certification Readiness — strict gate for "this row counts toward certification".

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``  (W0 closure)

Public surface
--------------

- ``is_certification_ready(verdict)``: ONLY returns ``True`` when the row is
  ``legal=True`` AND ``final_acceptance_status=ACCEPTED`` AND
  ``actual_proof_depth`` is at or above ``required_proof_depth``. PENDING,
  PARTIAL, BLOCKED, ACCEPTED_WITH_CAVEAT all return ``False``.
- ``summarize_certification_status(verdicts)``: produces an aggregate showing
  how many rows are certification-ready vs the canonical universe size, and
  the per-status distribution. The result includes a ``can_claim_runtime_certification``
  boolean that is ``True`` only when all 86 canonical rows are
  certification-ready. W0 baseline always reports ``False`` here because every
  row defaults to PENDING.

Hardening rules (W0 closure check #1)
-------------------------------------

1. PENDING NEVER counts as certified — even if PENDING is a "legal" status
   under the acceptance validator, it is NEVER certification-ready.
2. ``runtime_claim_allowed`` defaults to ``False`` for any row whose
   ``runtime_claim_allowed_rule`` does not explicitly resolve to a runtime-
   permitted state. This module re-derives the flag from observed evidence
   so a metadata-level claim cannot promote a row.
3. Final certification gate output MUST report PENDING/E0-baseline rows
   separately from runtime-proof rows so a downstream report cannot
   accidentally roll PENDING into "certified".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .acceptance_validator import AcceptanceVerdict
from .matrix_loader import (
    CANONICAL_REQUIREMENT_COUNT,
    RUNTIME_CLAIM_TYPES,
    RUNTIME_FORBIDDEN_CLAIM_TYPES,
)
from .proof_depth_ladder import can_satisfy


@dataclass(frozen=True)
class CertificationReadinessSummary:
    """Aggregate readiness across a verdict set."""

    total_rows: int
    canonical_universe_count: int
    ready_rows: int
    pending_rows: int
    partial_rows: int
    blocked_rows: int
    accepted_rows: int
    accepted_with_caveat_rows: int
    illegal_rows: int
    runtime_claim_allowed_rows: int
    """Rows where runtime_claim_allowed=True AND legal AND ACCEPTED."""

    can_claim_runtime_certification: bool
    """``True`` only when ``ready_rows == canonical_universe_count``."""

    runtime_proof_tier_breakdown: dict[str, int]
    """Per-tier breakdown of actual_proof_depth across the verdict set."""

    blocking_reasons: dict[str, int]
    """Aggregate violations preventing certification."""


def is_certification_ready(verdict: AcceptanceVerdict) -> bool:
    """Return True iff the verdict allows the row to count toward certification.

    Closure rule #1: PENDING / PARTIAL / BLOCKED / ACCEPTED_WITH_CAVEAT all
    return False — only ``ACCEPTED`` with ``legal=True`` AND
    ``actual >= required`` counts. This is intentionally stricter than the
    acceptance validator's ``legal`` flag because PENDING is *legal* (it
    triggers no rule) but it is NOT certified.
    """
    if not verdict.legal:
        return False
    if verdict.final_acceptance_status != "ACCEPTED":
        return False
    return can_satisfy(verdict.actual_proof_depth, verdict.required_proof_depth)


def derive_runtime_claim_allowed(
    verdict: AcceptanceVerdict,
    *,
    claim_type: str | None = None,
) -> bool:
    """Derive runtime_claim_allowed from observed evidence (closure rule #2).

    Defaults to ``False`` unless ALL of:
      - row is certification-ready
      - claim_type is in RUNTIME_CLAIM_TYPES
      - claim_type is NOT in RUNTIME_FORBIDDEN_CLAIM_TYPES (e.g. DOC_REFERENCE_ONLY)

    The metadata's ``runtime_claim_allowed`` field is NOT trusted on its
    own — this function ignores it and re-derives.
    """
    if not is_certification_ready(verdict):
        return False
    ct = (claim_type or verdict.claim_type or "").strip()
    if ct in RUNTIME_FORBIDDEN_CLAIM_TYPES:
        return False
    if ct not in RUNTIME_CLAIM_TYPES:
        # STATIC_ENFORCEMENT, COMPONENT_RUNTIME, etc. are not runtime-claim
        # rows in the strict sense — they prove specific behaviors but do
        # not earn the broad "runtime certified" label.
        return False
    return True


def summarize_certification_status(
    verdicts: Iterable[AcceptanceVerdict],
) -> CertificationReadinessSummary:
    """Build the aggregate readiness report from a verdict set."""
    rows = list(verdicts)
    total = len(rows)
    ready = sum(1 for v in rows if is_certification_ready(v))
    pending = sum(1 for v in rows if v.final_acceptance_status == "PENDING")
    partial = sum(1 for v in rows if v.final_acceptance_status == "PARTIAL")
    blocked = sum(1 for v in rows if v.final_acceptance_status == "BLOCKED")
    accepted = sum(1 for v in rows if v.final_acceptance_status == "ACCEPTED")
    accepted_caveat = sum(1 for v in rows if v.final_acceptance_status == "ACCEPTED_WITH_CAVEAT")
    illegal = sum(1 for v in rows if not v.legal)

    runtime_allowed = sum(
        1 for v in rows if derive_runtime_claim_allowed(v)
    )

    tier_breakdown: dict[str, int] = {}
    for v in rows:
        d = v.actual_proof_depth or "(unset)"
        tier_breakdown[d] = tier_breakdown.get(d, 0) + 1

    blocking: dict[str, int] = {}
    for v in rows:
        for r in v.rule_violations:
            blocking[r] = blocking.get(r, 0) + 1
        # Add status-class blockers
        if v.legal and v.final_acceptance_status == "PENDING":
            blocking["PENDING_NOT_CERTIFIED"] = blocking.get("PENDING_NOT_CERTIFIED", 0) + 1

    can_claim = ready == CANONICAL_REQUIREMENT_COUNT and total == CANONICAL_REQUIREMENT_COUNT

    return CertificationReadinessSummary(
        total_rows=total,
        canonical_universe_count=CANONICAL_REQUIREMENT_COUNT,
        ready_rows=ready,
        pending_rows=pending,
        partial_rows=partial,
        blocked_rows=blocked,
        accepted_rows=accepted,
        accepted_with_caveat_rows=accepted_caveat,
        illegal_rows=illegal,
        runtime_claim_allowed_rows=runtime_allowed,
        can_claim_runtime_certification=can_claim,
        runtime_proof_tier_breakdown=tier_breakdown,
        blocking_reasons=blocking,
    )


__all__ = [
    "CertificationReadinessSummary",
    "is_certification_ready",
    "derive_runtime_claim_allowed",
    "summarize_certification_status",
]
