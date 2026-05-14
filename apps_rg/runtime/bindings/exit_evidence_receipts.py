"""W6 G21/G22 payload extensions — app-owned evidence receipts for Exit.

Per W6 bundle requirements:
- AppsRgSectionValidationReceipt: headline X|Y|Z format, section/bullet counts
- AppsRgMetricPreservationEnvelope: metric preservation, no invented metrics
- AppsRgVerbatimIntegrityReceipt: education/certifications/early_career hash match
- AppsRgClaimSupportMap: claim refs, support status, blocked claims

These receipts are produced by apps_rg bindings and consumed by the Exit
evidence path WITHOUT changing canonical G21/G22 gates.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping


@dataclasses.dataclass(frozen=True)
class AppsRgSectionValidationReceipt:
    """Receipt validating section structure and headline format.
    
    G21 evidence: headline X|Y|Z format, section/bullet counts.
    """
    headline_format_valid: bool  # X|Y|Z format
    headline_x: str  # First part (e.g., "Insurance Technology Executive")
    headline_y: str  # Second part (e.g., "AI Strategy & Automation")
    headline_z: str  # Third part (e.g., "Operational Excellence")
    
    section_count_expected: int
    section_count_actual: int
    sections_valid: bool
    
    # Per-section bullet counts
    bullet_counts: dict[str, int]  # section_id -> bullet count
    bullet_count_valid: bool
    
    # Digest for provenance
    source_digest: str
    
    @property
    def all_valid(self) -> bool:
        """True if headline format and counts are valid."""
        return self.headline_format_valid and self.sections_valid and self.bullet_count_valid


@dataclasses.dataclass(frozen=True)
class AppsRgMetricPreservationEnvelope:
    """Envelope proving metric preservation without invention.
    
    G22 evidence: metrics from source resume preserved, no invented metrics.
    """
    # Metrics found in source resume (ground truth)
    source_metrics: dict[str, Any]  # metric_name -> value
    
    # Metrics appearing in generated output
    output_metrics: dict[str, Any]  # metric_name -> value
    
    # Metrics that were preserved (present in both)
    preserved_metrics: list[str]
    
    # Metrics that appear in output but NOT in source (invention = violation)
    invented_metrics: list[str]
    
    # Metrics in source that are missing from output (omission = ok if not relevant)
    omitted_metrics: list[str]
    
    # Hash of source for provenance
    source_resume_hash: str
    
    @property
    def has_invention(self) -> bool:
        """True if any metrics were invented (not in source)."""
        return len(self.invented_metrics) > 0
    
    @property
    def preservation_rate(self) -> float:
        """Fraction of source metrics preserved in output."""
        if not self.source_metrics:
            return 1.0
        return len(self.preserved_metrics) / len(self.source_metrics)


@dataclasses.dataclass(frozen=True)
class AppsRgVerbatimIntegrityReceipt:
    """Receipt proving verbatim integrity of education, certifications, early career.
    
    G21/G22 evidence: education/certifications/early_career hash match.
    """
    # Section hashes from source resume
    education_source_hash: str
    certifications_source_hash: str
    early_career_source_hash: str
    
    # Section hashes from generated output
    education_output_hash: str
    certifications_output_hash: str
    early_career_output_hash: str
    
    # Match results
    education_verbatim: bool
    certifications_verbatim: bool
    early_career_verbatim: bool
    
    # Overall integrity
    @property
    def all_verbatim(self) -> bool:
        """True if all verbatim sections match."""
        return self.education_verbatim and self.certifications_verbatim and self.early_career_verbatim
    
    # Source of truth hash for provenance
    source_resume_hash: str


@dataclasses.dataclass(frozen=True)
class AppsRgClaimSupportMap:
    """Map of claims to their supporting evidence.
    
    Tracks claim references, support status, and blocked claims.
    """
    # Claims made in generated output
    claims: list[dict[str, Any]]  # Each claim has text, section_id, claim_id
    
    # Evidence references supporting each claim
    claim_evidence_refs: dict[str, list[str]]  # claim_id -> list of evidence refs
    
    # Support status per claim
    claim_support_status: dict[str, str]  # claim_id -> "PASS", "PARTIAL", "WEAK", "UNSUPPORTED"
    
    # Claims that were blocked (unsupported or contradicted)
    blocked_claims: list[str]  # claim_ids that failed support check
    
    # Source hashes for provenance
    source_resume_hash: str
    jd_hash: str
    briefing_hash: str
    
    @property
    def blocked_claim_count(self) -> int:
        """Number of claims that were blocked."""
        return len(self.blocked_claims)
    
    @property
    def unsupported_rate(self) -> float:
        """Fraction of claims that are unsupported."""
        if not self.claims:
            return 0.0
        unsupported = sum(
            1 for c in self.claims
            if self.claim_support_status.get(c["claim_id"], "UNSUPPORTED") == "UNSUPPORTED"
        )
        return unsupported / len(self.claims)


# Export all receipt types
__all__ = [
    "AppsRgSectionValidationReceipt",
    "AppsRgMetricPreservationEnvelope",
    "AppsRgVerbatimIntegrityReceipt",
    "AppsRgClaimSupportMap",
]
