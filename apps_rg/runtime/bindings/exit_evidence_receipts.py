"""apps_rg Exit evidence receipts — G21/G22 app-owned receipt types.

These dataclasses are apps_rg-owned.  They do NOT import from canonical
G21/G22 gate modules in agentic_core.  They carry structured evidence
that generic Exit gate evaluators consume.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "AppsRgSectionValidationReceipt",
    "AppsRgMetricPreservationEnvelope",
    "AppsRgVerbatimIntegrityReceipt",
    "AppsRgClaimSupportMap",
]


@dataclass(frozen=True)
class AppsRgSectionValidationReceipt:
    """G21 evidence: headline format and section/bullet counts."""

    headline_format_valid: bool
    headline_x: str
    headline_y: str
    headline_z: str
    section_count_expected: int
    section_count_actual: int
    sections_valid: bool
    bullet_counts: dict[str, int]
    bullet_count_valid: bool = True
    source_digest: str = ""

    @property
    def all_valid(self) -> bool:
        return (
            self.headline_format_valid
            and self.sections_valid
            and self.bullet_count_valid
        )


@dataclass(frozen=True)
class AppsRgMetricPreservationEnvelope:
    """G22 evidence: metric preservation — no invented metrics."""

    source_metrics: dict[str, Any]
    output_metrics: dict[str, Any]
    preserved_metrics: list[str]
    invented_metrics: list[str]
    omitted_metrics: list[str]
    source_resume_hash: str = ""

    @property
    def has_invention(self) -> bool:
        return len(self.invented_metrics) > 0

    @property
    def preservation_rate(self) -> float:
        total = len(self.source_metrics)
        if total == 0:
            return 1.0
        preserved = len(self.preserved_metrics)
        return round(preserved / total, 4)


@dataclass(frozen=True)
class AppsRgVerbatimIntegrityReceipt:
    """G22 evidence: verbatim section hash integrity."""

    education_source_hash: str
    certifications_source_hash: str
    early_career_source_hash: str
    education_output_hash: str
    certifications_output_hash: str
    early_career_output_hash: str
    education_verbatim: bool
    certifications_verbatim: bool
    early_career_verbatim: bool
    source_resume_hash: str = ""

    @property
    def all_verbatim(self) -> bool:
        return (
            self.education_verbatim
            and self.certifications_verbatim
            and self.early_career_verbatim
        )


@dataclass(frozen=True)
class AppsRgClaimSupportMap:
    """G22 evidence: claim support status map."""

    claims: list[dict[str, Any]]
    claim_evidence_refs: dict[str, list[str]]
    claim_support_status: dict[str, str]
    blocked_claims: list[str]
    source_resume_hash: str = ""
    jd_hash: str = ""
    briefing_hash: str = ""

    @property
    def blocked_claim_count(self) -> int:
        return len(self.blocked_claims)

    @property
    def unsupported_rate(self) -> float:
        total = len(self.claims)
        if total == 0:
            return 0.0
        unsupported = sum(
            1 for v in self.claim_support_status.values()
            if v not in ("PASS", "SUPPORTED")
        )
        return round(unsupported / total, 4)
