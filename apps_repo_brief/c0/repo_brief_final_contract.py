"""
P3.7 — apps_repo_brief Authoritative FinalEvidenceContract.v1

The authoritative FinalEvidenceContract (FEC) is produced by C0 BEFORE
PA and L2. It is NOT minted post-L2.

This module defines the dataclass schema that C0 populates and PA/L2/Exit
consume. apps_repo_brief.cert.cert_projection_adapter may REFERENCE the
FEC but must NOT replace it with a new authoritative instance.

Responsibility boundary:
  C0 mints → PA reads (S0-R0 slot binding) → L2 reads (synthesis only)
  → Exit validates → cert_projection_adapter projects (reference only, no new mint)

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.7, §11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Evidence status vocabulary
# ---------------------------------------------------------------------------

class EvidenceStatus(str, Enum):
    PASS = "PASS"
    WEAK = "WEAK"
    WEAK_WITH_CAVEATS = "WEAK_WITH_CAVEATS"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    MISSING = "MISSING"


class DepthProfile(str, Enum):
    REPO_BRIEF_LIGHT = "REPO_BRIEF_LIGHT"
    REPO_BRIEF_STANDARD = "REPO_BRIEF_STANDARD"
    REPO_BRIEF_DEEP = "REPO_BRIEF_DEEP"
    REPO_BRIEF_BOARD_DOSSIER = "REPO_BRIEF_BOARD_DOSSIER"


# ---------------------------------------------------------------------------
# C0 output sub-contracts (P3.11)
# ---------------------------------------------------------------------------

@dataclass
class SourceRef:
    source_id: str
    source_type: str  # e.g. "architecture_doc", "test_file", "adr", "runtime_proof"
    path: str
    authority: str  # "high" | "medium" | "low"
    freshness_days: int
    is_stale: bool
    origin_marker: str  # preserved in output citations


@dataclass
class SourcePortfolioSummary:
    """P3.11 — Source portfolio produced by C0."""
    total_sources: int
    by_source_type: dict[str, int]
    authority_distribution: dict[str, int]  # high/medium/low counts
    stale_count: int
    freshness_window_days: int
    source_refs: list[SourceRef] = field(default_factory=list)


@dataclass
class ClaimEvidenceEntry:
    claim_id: str
    claim_text: str
    status: EvidenceStatus
    supporting_source_ids: list[str]
    caveat_required: bool
    caveat_text: str = ""


@dataclass
class ClaimEvidenceMap:
    """P3.11 — Per-claim support status produced by C0."""
    entries: list[ClaimEvidenceEntry] = field(default_factory=list)
    pass_count: int = 0
    weak_count: int = 0
    unsupported_count: int = 0
    contradicted_count: int = 0

    def get_entry(self, claim_id: str) -> ClaimEvidenceEntry | None:
        for e in self.entries:
            if e.claim_id == claim_id:
                return e
        return None


@dataclass
class ContradictionEntry:
    contradiction_id: str
    claim_a: str
    claim_b: str
    resolution: str  # "omit_both" | "flag_unresolved" | "caveat_both"
    is_critical: bool


@dataclass
class ContradictionMatrix:
    """P3.11 — Unresolved conflicts produced by C0."""
    entries: list[ContradictionEntry] = field(default_factory=list)
    has_critical: bool = False


@dataclass
class FreshnessReport:
    """P3.11 — Source recency and staleness caveats produced by C0."""
    stale_sources: list[str]  # source_ids
    freshness_caveats: dict[str, str]  # source_id → caveat text
    max_age_days: int
    policy_freshness_window_days: int


@dataclass
class SectionCoverage:
    section_id: str
    selected: bool
    evidence_status: EvidenceStatus
    source_count: int
    coverage_pct: float
    omit_if_unsupported: bool


@dataclass
class BriefingCoverageMatrix:
    """P3.10 — Adaptive section selection produced by C0."""
    depth_profile: DepthProfile
    audience: str
    sections: list[SectionCoverage] = field(default_factory=list)
    overall_coverage_pct: float = 0.0
    meets_depth_floor: bool = False

    def selected_section_ids(self) -> list[str]:
        return [s.section_id for s in self.sections if s.selected]


@dataclass
class SectionGapEntry:
    section_id: str
    gap_reason: str
    omit_if_unsupported: bool
    fallback_action: str  # "omit" | "caveat" | "abstain"


@dataclass
class SectionGapReport:
    """P3.10/P3.11 — Sections C0 could not fully evidence."""
    gaps: list[SectionGapEntry] = field(default_factory=list)
    abstain_required: bool = False


@dataclass
class SynthesisGuidanceForPA:
    """C0 → PA handoff: gap handling and caveat injection policy."""
    caveat_injection_policy: str  # "inline" | "section_footer" | "appendix"
    gap_handling: str  # "omit" | "placeholder" | "abstain"
    unsupported_claim_policy: str  # "omit" | "caveat_required"
    weak_claim_policy: str  # "caveat_required" | "flag_only"
    stale_source_policy: str  # "caveat_required" | "block"
    board_mode_strict: bool = False


# ---------------------------------------------------------------------------
# P3.12 — Board gate thresholds (used by C0 + Exit)
# ---------------------------------------------------------------------------

@dataclass
class BoardGateThresholds:
    """P3.12 — Hard gates that must pass for BOARD_DOSSIER depth profile."""
    min_section_coverage_pct: float = 95.0
    auth_governance_anchor_required: bool = True
    stale_source_policy: str = "block"
    min_sources: int = 30
    min_citation_anchors: int = 25
    critical_contradiction_policy: str = "escalate_hitl"


# ---------------------------------------------------------------------------
# P3.7 — Authoritative FinalEvidenceContract.v1
# ---------------------------------------------------------------------------

@dataclass
class RepoBriefFinalEvidenceContract:
    """
    Authoritative FinalEvidenceContract.v1 for apps_repo_brief.

    Produced by C0. Referenced (never replaced) by:
    - PA compiler (slot binding)
    - L2 synthesis (evidence-only synthesis)
    - Exit v6 (groundedness validation)
    - cert_projection_adapter (projection only)

    Schema version: apps_repo_brief.FinalEvidenceContract/v1
    """

    schema_version: str = "apps_repo_brief.FinalEvidenceContract/v1"

    # Identity
    contract_id: str = ""
    trace_id: str = ""
    replay_key: str = ""

    # Retrieval surface
    retrieval_surface_id: str = "repo_brief_docs"
    repo_snapshot_id: str = ""
    policy_hash: str = ""
    blueprint_hash: str = ""

    # Depth and audience
    depth_profile: DepthProfile = DepthProfile.REPO_BRIEF_STANDARD
    audience: str = ""
    persona_schema_version: str = ""

    # Core evidence outputs (P3.11)
    evidence_status: EvidenceStatus = EvidenceStatus.MISSING
    source_portfolio: SourcePortfolioSummary | None = None
    claim_evidence_map: ClaimEvidenceMap | None = None
    contradiction_matrix: ContradictionMatrix | None = None
    freshness_report: FreshnessReport | None = None

    # Coverage (P3.10)
    briefing_coverage_matrix: BriefingCoverageMatrix | None = None
    section_gap_report: SectionGapReport | None = None

    # PA handoff
    synthesis_guidance: SynthesisGuidanceForPA | None = None

    # Board gate results (P3.12 — set by C0 before handing to PA)
    board_gate_passed: bool | None = None
    board_gate_details: dict[str, Any] = field(default_factory=dict)

    # Provenance
    c0_completed_at: str = ""
    c0_retrieval_lanes_used: list[str] = field(default_factory=list)
    authoritative: bool = True  # always True; cert_projection_adapter must NOT flip this

    def is_grounded(self) -> bool:
        """True only when evidence_status is PASS or WEAK_WITH_CAVEATS."""
        return self.evidence_status in (EvidenceStatus.PASS, EvidenceStatus.WEAK_WITH_CAVEATS)

    def requires_abstain(self) -> bool:
        """True when C0 determined no brief can be produced."""
        return (
            self.evidence_status == EvidenceStatus.MISSING
            or (self.section_gap_report is not None and self.section_gap_report.abstain_required)
        )
