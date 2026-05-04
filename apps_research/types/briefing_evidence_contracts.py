"""apps_research briefing-grade C0 evidence contracts.

Eight typed dataclasses produced by the C0 retrieval pass and consumed by:
- research_pa_compiler.py   (prompt template hydration — S0/C0/U0 slots)
- research_exit_fec_producer.py (FinalEvidenceContract assembly)
- research_l2_step_adapters.py  (E1 receipt gate, E2 evidence validation)

All contracts are frozen (immutable after construction). The C0-to-PA gate
function ``evaluate_c0_gate`` lives in research_c0_adapter.py and consumes
``BriefingCoverageMatrix`` + ``SourcePortfolioSummary``.

Plan: apps-research-spine-alignment-d4e8f2 W2.1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# 1. BriefingCoverageMatrix
#    Tracks which canonical coverage families were retrieved and how well.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FamilyCoverageEntry:
    """Per-family coverage record."""

    family: str
    sources_found: int
    min_sources_required: int
    covered: bool
    query_used: str = ""

    @property
    def coverage_ratio(self) -> float:
        if self.min_sources_required == 0:
            return 1.0
        return min(self.sources_found / self.min_sources_required, 1.0)


@dataclass
class BriefingCoverageMatrix:
    """Coverage matrix across all canonical research families.

    Produced after C0 retrieval completes. Consumed by:
    - evaluate_c0_gate() to determine PASS/WEAK/FAIL verdict
    - PA compiler S0 slot hydration (coverage summary)
    - FEC c0_evidence_summary field
    """

    depth_profile: str
    entries: list[FamilyCoverageEntry] = field(default_factory=list)
    total_families_required: int = 0
    families_covered: int = 0
    overall_coverage_ratio: float = 0.0

    def add_entry(self, entry: FamilyCoverageEntry) -> None:
        self.entries.append(entry)
        self.total_families_required = len(self.entries)
        self.families_covered = sum(1 for e in self.entries if e.covered)
        if self.total_families_required > 0:
            self.overall_coverage_ratio = self.families_covered / self.total_families_required

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "depth_profile": self.depth_profile,
            "total_families_required": self.total_families_required,
            "families_covered": self.families_covered,
            "overall_coverage_ratio": round(self.overall_coverage_ratio, 4),
            "entries": [
                {
                    "family": e.family,
                    "sources_found": e.sources_found,
                    "min_sources_required": e.min_sources_required,
                    "covered": e.covered,
                }
                for e in self.entries
            ],
        }


# ---------------------------------------------------------------------------
# 2. ClaimEvidenceMap
#    Maps synthesis claims to supporting source references.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ClaimAnchor:
    """A single claim-to-source binding."""

    claim_id: str
    claim_text: str
    source_refs: tuple[str, ...]
    confidence: float = 1.0
    family: str = ""


@dataclass
class ClaimEvidenceMap:
    """Map from synthesis claims to their C0 source anchors.

    Consumed by:
    - PA compiler U0 slot (unsupported claim detection)
    - E2 evidence validation (check source refs exist)
    - FEC evidence trail
    """

    run_id: str = ""
    anchors: list[ClaimAnchor] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    total_claims: int = 0
    supported_claim_ratio: float = 0.0

    def add_anchor(self, anchor: ClaimAnchor) -> None:
        self.anchors.append(anchor)
        self.total_claims = len(self.anchors) + len(self.unsupported_claims)
        supported = len(self.anchors)
        if self.total_claims > 0:
            self.supported_claim_ratio = supported / self.total_claims

    def add_unsupported(self, claim_text: str) -> None:
        self.unsupported_claims.append(claim_text)
        self.total_claims = len(self.anchors) + len(self.unsupported_claims)
        supported = len(self.anchors)
        if self.total_claims > 0:
            self.supported_claim_ratio = supported / self.total_claims


# ---------------------------------------------------------------------------
# 3. ContradictionMatrix
#    Records contradictions found between retrieved sources.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ContradictionEntry:
    """A single source contradiction record."""

    subject: str
    source_a_ref: str
    source_b_ref: str
    source_a_claim: str
    source_b_claim: str
    severity: str = "low"


@dataclass
class ContradictionMatrix:
    """Matrix of inter-source contradictions detected during retrieval.

    Consumed by:
    - PA compiler C0 slot (caveat injection)
    - E2 evidence validation (high-severity contradictions block synthesis)
    - FEC evidence trail
    """

    run_id: str = ""
    contradictions: list[ContradictionEntry] = field(default_factory=list)
    high_severity_count: int = 0

    def add(self, entry: ContradictionEntry) -> None:
        self.contradictions.append(entry)
        if entry.severity == "high":
            self.high_severity_count += 1

    def has_blocking_contradictions(self) -> bool:
        return self.high_severity_count > 0


# ---------------------------------------------------------------------------
# 4. FreshnessReport
#    Tracks source recency across the retrieved corpus.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SourceFreshnessRecord:
    """Per-source freshness record."""

    source_ref: str
    publication_date: str
    age_days: int
    is_fresh: bool
    family: str = ""


@dataclass
class FreshnessReport:
    """Source freshness report across all retrieved chunks.

    Consumed by:
    - PA compiler D0 slot (depth profile downgrade trigger)
    - E2 evidence validation (stale-dominated corpus triggers caveat)
    - FEC evidence trail
    """

    run_id: str = ""
    records: list[SourceFreshnessRecord] = field(default_factory=list)
    fresh_source_count: int = 0
    stale_source_count: int = 0
    freshness_ratio: float = 0.0
    median_age_days: int = 0

    def add_record(self, record: SourceFreshnessRecord) -> None:
        self.records.append(record)
        self.fresh_source_count = sum(1 for r in self.records if r.is_fresh)
        self.stale_source_count = len(self.records) - self.fresh_source_count
        total = len(self.records)
        self.freshness_ratio = self.fresh_source_count / total if total > 0 else 0.0

    def is_dominated_by_stale(self, threshold: float = 0.6) -> bool:
        return self.freshness_ratio < threshold


# ---------------------------------------------------------------------------
# 5. SynthesisGuidanceForPA
#    Carries C0-derived guidance consumed by PA compiler slot rendering.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SynthesisGuidanceForPA:
    """Guidance produced by C0 gate for PA compiler slot hydration.

    Consumed by:
    - PA compiler R0 slot (synthesis guidance)
    - company_brief_synthesis_v1.yaml slot bodies
    """

    depth_profile: str
    c0_gate_verdict: str
    recommended_sections: tuple[str, ...]
    omit_sections: tuple[str, ...]
    caveat_prefixes: tuple[str, ...]
    citation_density_target: str = "standard"
    confidence_floor: float = 0.7
    notes: str = ""

    def should_include_section(self, section_id: str) -> bool:
        return section_id not in self.omit_sections


# ---------------------------------------------------------------------------
# 6. SourcePortfolioSummary
#    Aggregate statistics across the full retrieved source portfolio.
# ---------------------------------------------------------------------------

@dataclass
class SourcePortfolioSummary:
    """Portfolio-level statistics across all retrieved sources.

    Consumed by:
    - evaluate_c0_gate() (source count threshold check)
    - FEC c0_evidence_summary field
    - PA compiler I0 slot (input context summary)
    """

    depth_profile: str
    total_sources: int = 0
    total_chunks: int = 0
    unique_domains: int = 0
    source_urls: list[str] = field(default_factory=list)
    families_represented: list[str] = field(default_factory=list)
    query_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "depth_profile": self.depth_profile,
            "total_sources": self.total_sources,
            "total_chunks": self.total_chunks,
            "unique_domains": self.unique_domains,
            "families_represented": self.families_represented,
            "query_count": self.query_count,
        }


# ---------------------------------------------------------------------------
# 7. CitationAnchorRegistry
#    Index of all citation anchors emitted during synthesis.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CitationAnchor:
    """A single citation anchor binding output text to a source."""

    anchor_id: str
    source_ref: str
    text_span: str
    section_id: str = ""
    family: str = ""


@dataclass
class CitationAnchorRegistry:
    """Registry of all citation anchors for the current synthesis run.

    Consumed by:
    - E4 FEC producer (anchor count validation)
    - brief_citation_repair_v1 template (citation repair gate)
    - FEC evidence trail
    """

    run_id: str = ""
    anchors: list[CitationAnchor] = field(default_factory=list)

    def add(self, anchor: CitationAnchor) -> None:
        self.anchors.append(anchor)

    @property
    def count(self) -> int:
        return len(self.anchors)

    def meets_minimum(self, min_anchors: int) -> bool:
        return self.count >= min_anchors


# ---------------------------------------------------------------------------
# 8. EvidenceGapReport
#    Records coverage gaps detected after retrieval completes.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvidenceGap:
    """A single evidence gap for a required family or section."""

    family: str
    required_min_sources: int
    found_sources: int
    gap_severity: str
    suggested_query: str = ""


@dataclass
class EvidenceGapReport:
    """Full report of evidence gaps detected after C0 retrieval.

    Consumed by:
    - evidence_gap_analysis_v1 template
    - PA compiler (determines whether gap-caveat slot injection is needed)
    - E2 evidence validation (high-severity gaps block synthesis)
    """

    run_id: str = ""
    depth_profile: str = ""
    gaps: list[EvidenceGap] = field(default_factory=list)
    critical_gap_count: int = 0
    high_gap_count: int = 0

    def add_gap(self, gap: EvidenceGap) -> None:
        self.gaps.append(gap)
        if gap.gap_severity == "critical":
            self.critical_gap_count += 1
        elif gap.gap_severity == "high":
            self.high_gap_count += 1

    def has_blocking_gaps(self) -> bool:
        return self.critical_gap_count > 0


# ---------------------------------------------------------------------------
# Bundle — carries all 8 contracts through the E1-E5 pipeline
# ---------------------------------------------------------------------------

@dataclass
class BriefingEvidenceBundle:
    """All 8 briefing-grade evidence contracts in a single carrier.

    Assembled by ResearchC0Adapter.retrieve() and passed through the
    E1-E5 step adapter pipeline. Each field is typed; None means the
    contract was not yet populated (triggers E1 gate failure).
    """

    depth_profile: str
    coverage_matrix: BriefingCoverageMatrix | None = None
    claim_evidence_map: ClaimEvidenceMap | None = None
    contradiction_matrix: ContradictionMatrix | None = None
    freshness_report: FreshnessReport | None = None
    synthesis_guidance: SynthesisGuidanceForPA | None = None
    source_portfolio: SourcePortfolioSummary | None = None
    citation_registry: CitationAnchorRegistry | None = None
    gap_report: EvidenceGapReport | None = None

    def is_complete(self) -> bool:
        """True iff all 8 contracts are populated (non-None)."""
        return all([
            self.coverage_matrix is not None,
            self.claim_evidence_map is not None,
            self.contradiction_matrix is not None,
            self.freshness_report is not None,
            self.synthesis_guidance is not None,
            self.source_portfolio is not None,
            self.citation_registry is not None,
            self.gap_report is not None,
        ])

    def missing_contracts(self) -> list[str]:
        names = [
            "coverage_matrix", "claim_evidence_map", "contradiction_matrix",
            "freshness_report", "synthesis_guidance", "source_portfolio",
            "citation_registry", "gap_report",
        ]
        return [n for n in names if getattr(self, n) is None]
