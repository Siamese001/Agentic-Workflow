"""apps_research C0 retrieval adapter — mandatory grounding delegate.

R3_SIMPLE_GROUNDED_READ = GROUNDED, meaning C0 retrieval is mandatory before
any synthesis step. This adapter is the single delegation point between the
apps_research spine and the agentic_core C0 context engine.

Evidence contracts produced by this adapter are consumed by:
- research_pa_compiler.py (prompt template hydration)
- research_exit_fec_producer.py (FinalEvidenceContract assembly)

Plan: apps-research-spine-alignment-d4e8f2 W2.1 (full implementation).
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Literal

from apps_research.engines.query_decomposer import (
    _DEPTH_PROFILES,
    _resolve_depth_profile,
    decompose_coverage_families,
)
from apps_research.types.briefing_evidence_contracts import (
    BriefingCoverageMatrix,
    BriefingEvidenceBundle,
    CitationAnchorRegistry,
    ClaimEvidenceMap,
    ContradictionMatrix,
    EvidenceGap,
    EvidenceGapReport,
    FamilyCoverageEntry,
    FreshnessReport,
    SourceFreshnessRecord,
    SourcePortfolioSummary,
    SynthesisGuidanceForPA,
)

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Depth profile constants (canonical aliases for adapter callers)
# ---------------------------------------------------------------------------

class ResearchDepthProfile:
    LIGHT = "COMPANY_BRIEF_LIGHT"
    STANDARD = "COMPANY_BRIEF_STANDARD"
    DEEP = "COMPANY_BRIEF_DEEP"
    DOSSIER = "COMPANY_BRIEF_DOSSIER"
    COMPETITIVE_SCAN = "COMPANY_BRIEF_COMPETITIVE_SCAN"
    FORENSIC = "COMPANY_BRIEF_FORENSIC"


# ---------------------------------------------------------------------------
# Legacy C0 bundle (kept for compatibility with existing callers)
# ---------------------------------------------------------------------------

@dataclass
class C0EvidenceBundle:
    """Thin wrapper around raw C0 retrieval results.

    Callers that have not yet migrated to BriefingEvidenceBundle use this.
    The E1 receipt gate calls validate_gate() before synthesis proceeds.
    """

    depth_profile: str = ResearchDepthProfile.STANDARD
    query_count: int = 0
    chunk_count: int = 0
    chunks: list[dict[str, Any]] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    _MIN_CHUNK_COUNT: dict[str, int] = field(
        default_factory=lambda: {
            ResearchDepthProfile.LIGHT: 3,
            ResearchDepthProfile.STANDARD: 10,
            ResearchDepthProfile.DEEP: 20,
            ResearchDepthProfile.DOSSIER: 30,
            ResearchDepthProfile.COMPETITIVE_SCAN: 15,
            ResearchDepthProfile.FORENSIC: 35,
        }
    )

    def validate_gate(self) -> None:
        """Raise if the bundle does not meet minimum threshold for its depth profile.

        Called by the E1 receipt gate. Failure → X3E_SAFE_ABSTAIN via Exit v6.
        """
        min_chunks = self._MIN_CHUNK_COUNT.get(self.depth_profile, 3)
        if self.chunk_count < min_chunks:
            raise C0GateFailed(
                f"C0 bundle for profile '{self.depth_profile}' has "
                f"{self.chunk_count} chunks; minimum is {min_chunks}."
            )


class C0GateFailed(RuntimeError):
    """Raised when C0 evidence bundle fails the minimum gate for its depth profile.

    Must be routed through Exit v6 as X3E_SAFE_ABSTAIN — no synthesis fallback.
    """


# ---------------------------------------------------------------------------
# C0-to-PA gate — PASS / WEAK_WITH_CAVEATS / FAIL_DEGRADE
# ---------------------------------------------------------------------------

C0GateVerdict = Literal["PASS", "WEAK_WITH_CAVEATS", "FAIL_DEGRADE"]

_GATE_THRESHOLDS: dict[str, dict[str, float]] = {
    profile: {
        "pass_floor": cfg.get("coverage_floor", 0.65),
        "weak_floor": cfg.get("gate_weak_floor", 0.50),
        "min_sources": cfg.get("min_sources", 5),
    }
    for profile, cfg in _DEPTH_PROFILES.items()
}


def evaluate_c0_gate(
    coverage_matrix: BriefingCoverageMatrix,
    source_portfolio: SourcePortfolioSummary,
    depth_profile: str,
) -> C0GateVerdict:
    """Evaluate whether C0 evidence meets the PA synthesis bar.

    Returns:
        "PASS"                — coverage and source counts meet the floor for
                                this depth profile; synthesis may proceed.
        "WEAK_WITH_CAVEATS"   — coverage is between weak_floor and pass_floor;
                                PA must inject gap-caveat prefix on all claims.
        "FAIL_DEGRADE"        — coverage is below weak_floor or source count is
                                critically low; must not synthesise; degrade to
                                X3E_SAFE_ABSTAIN via Exit v6.

    Args:
        coverage_matrix:   BriefingCoverageMatrix from C0 retrieval pass.
        source_portfolio:  SourcePortfolioSummary from C0 retrieval pass.
        depth_profile:     Canonical profile key (e.g. "COMPANY_BRIEF_DEEP")
                           or alias (e.g. "deep"); resolved internally.
    """
    resolved = _resolve_depth_profile(depth_profile)
    thresholds = _GATE_THRESHOLDS.get(resolved, _GATE_THRESHOLDS["COMPANY_BRIEF_STANDARD"])

    pass_floor: float = thresholds["pass_floor"]
    weak_floor: float = thresholds["weak_floor"]
    min_sources: int = int(thresholds["min_sources"])

    coverage = coverage_matrix.overall_coverage_ratio
    sources = source_portfolio.total_sources

    _log.debug(
        "evaluate_c0_gate: profile=%s coverage=%.3f pass_floor=%.3f "
        "weak_floor=%.3f sources=%d min_sources=%d",
        resolved, coverage, pass_floor, weak_floor, sources, min_sources,
    )

    # Hard fail: source count critically low (< 50% of minimum)
    if sources < math.ceil(min_sources * 0.5):
        _log.warning(
            "C0 gate FAIL_DEGRADE: sources=%d < 50pct of min_sources=%d (profile=%s)",
            sources, min_sources, resolved,
        )
        return "FAIL_DEGRADE"

    if coverage >= pass_floor and sources >= min_sources:
        return "PASS"

    if coverage >= weak_floor:
        return "WEAK_WITH_CAVEATS"

    return "FAIL_DEGRADE"


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class ResearchC0Adapter:
    """Delegates C0 hybrid retrieval to the agentic_core C0 context engine.

    Produces a BriefingEvidenceBundle carrying all 8 typed evidence contracts
    required by the E1-E5 step adapter pipeline.

    In production, retrieval is delegated to the agentic_core hybrid search
    engine (ChromaDB collection + BM25 reranker). When the collection is
    unavailable the adapter degrades gracefully — returning an empty bundle
    that will fail the C0 gate and route through X3E_SAFE_ABSTAIN.
    """

    def __init__(self, collection: str = "process_docs") -> None:
        self._collection = collection

    def retrieve(
        self,
        request: Any,
        depth_profile: str = ResearchDepthProfile.STANDARD,
    ) -> C0EvidenceBundle:
        """Run a C0 retrieval pass and return a legacy C0EvidenceBundle.

        For callers that have not yet migrated to retrieve_briefing_bundle().
        Thin wrapper that calls retrieve_briefing_bundle() internally.

        Args:
            request: ResearchRequest.
            depth_profile: Canonical or alias depth profile.

        Returns:
            C0EvidenceBundle with chunk_count, source_urls, and metadata
            populated from the raw retrieval result.

        Raises:
            C0GateFailed: If bundle fails the minimum chunk gate.
        """
        bundle = self.retrieve_briefing_bundle(request, depth_profile=depth_profile)
        portfolio = bundle.source_portfolio

        legacy = C0EvidenceBundle(
            depth_profile=_resolve_depth_profile(depth_profile),
            query_count=portfolio.query_count if portfolio else 0,
            chunk_count=portfolio.total_chunks if portfolio else 0,
            source_urls=list(portfolio.source_urls) if portfolio else [],
            metadata={
                "depth_profile": depth_profile,
                "families_represented": portfolio.families_represented if portfolio else [],
            },
        )
        legacy.chunks = []
        legacy.validate_gate()
        return legacy

    def retrieve_briefing_bundle(
        self,
        request: Any,
        depth_profile: str = ResearchDepthProfile.STANDARD,
        inject_chunks: list[dict[str, Any]] | None = None,
    ) -> BriefingEvidenceBundle:
        """Run a C0 retrieval pass and return all 8 briefing-grade evidence contracts.

        Delegates to the agentic_core C0 context engine (GovernedAppRunner
        substrate). When the collection is unavailable, degrades gracefully
        — the returned bundle will have empty coverage, triggering a
        FAIL_DEGRADE verdict from evaluate_c0_gate().

        Args:
            request: ResearchRequest.
            depth_profile: Canonical or alias depth profile string.
            inject_chunks: Optional pre-formed chunks for happy-path testing;
                           appended to any real retrieval results before
                           contract assembly.

        Returns:
            BriefingEvidenceBundle with all 8 contracts populated.
        """
        resolved = _resolve_depth_profile(depth_profile)
        topic: str = getattr(request, "topic", "") or ""

        query_plans = decompose_coverage_families(
            topic=topic,
            depth_profile=resolved,
            jd_context=getattr(request, "jd_context", None),
        )

        raw_chunks: list[dict[str, Any]] = list(inject_chunks or [])
        raw_chunks.extend(self._delegate_retrieval(topic, query_plans))

        return self._assemble_bundle(
            resolved=resolved,
            query_plans=query_plans,
            raw_chunks=raw_chunks,
        )

    def _delegate_retrieval(
        self,
        topic: str,
        query_plans: list[Any],
    ) -> list[dict[str, Any]]:
        """Delegate to agentic_core C0 engine; degrade gracefully on failure."""
        try:
            from apps_shared.integrations.governed_app_runner import GovernedAppRunner  # noqa: PLC0415
            runner = GovernedAppRunner(collection=self._collection)
            chunks: list[dict[str, Any]] = []
            for plan in query_plans:
                result = runner.run_governed_core(
                    query=plan.query,
                    run_id="",
                )
                raw = getattr(result, "c0_chunks", None) or []
                for chunk in raw:
                    entry = chunk if isinstance(chunk, dict) else vars(chunk)
                    entry.setdefault("family", plan.family)
                    chunks.append(entry)
            return chunks
        except Exception as exc:  # guardian: allow-log-and-swallow -- C0 delegation failure degrades gracefully; empty bundle triggers C0 gate fail → X3E_SAFE_ABSTAIN
            _log.warning(
                "ResearchC0Adapter._delegate_retrieval degraded: %s: %s",
                type(exc).__name__, exc,
            )
            return []

    def _assemble_bundle(
        self,
        resolved: str,
        query_plans: list[Any],
        raw_chunks: list[dict[str, Any]],
    ) -> BriefingEvidenceBundle:
        """Assemble all 8 briefing-grade evidence contracts from raw chunks."""
        profile_cfg = _DEPTH_PROFILES.get(resolved, {})

        # 1. BriefingCoverageMatrix
        coverage = BriefingCoverageMatrix(depth_profile=resolved)
        chunks_by_family: dict[str, list[dict[str, Any]]] = {}
        for chunk in raw_chunks:
            fam = chunk.get("family", "unknown")
            chunks_by_family.setdefault(fam, []).append(chunk)

        for plan in query_plans:
            sources = len(chunks_by_family.get(plan.family, []))
            entry = FamilyCoverageEntry(
                family=plan.family,
                sources_found=sources,
                min_sources_required=plan.min_sources,
                covered=sources >= plan.min_sources,
                query_used=plan.query,
            )
            coverage.add_entry(entry)

        # 2. SourcePortfolioSummary
        all_urls = [c.get("url", c.get("source_ref", "")) for c in raw_chunks if c.get("url") or c.get("source_ref")]
        domains = set()
        for url in all_urls:
            parts = url.split("/")
            if len(parts) >= 3:
                domains.add(parts[2])
        portfolio = SourcePortfolioSummary(
            depth_profile=resolved,
            total_sources=len(set(all_urls)),
            total_chunks=len(raw_chunks),
            unique_domains=len(domains),
            source_urls=list(set(all_urls)),
            families_represented=list(chunks_by_family.keys()),
            query_count=len(query_plans),
        )

        # 3. ClaimEvidenceMap — pre-retrieval: all claims unanchored (populated in E3)
        claim_map = ClaimEvidenceMap(run_id="")

        # 4. ContradictionMatrix — populated by retrieval reranker when available
        contradiction = ContradictionMatrix(run_id="")

        # 5. FreshnessReport
        freshness = FreshnessReport(run_id="")
        for chunk in raw_chunks:
            age = chunk.get("age_days", 180)
            rec = SourceFreshnessRecord(
                source_ref=chunk.get("url", chunk.get("source_ref", "")),
                publication_date=chunk.get("publication_date", ""),
                age_days=int(age),
                is_fresh=int(age) < 365,
                family=chunk.get("family", ""),
            )
            freshness.add_record(rec)

        # 6. EvidenceGapReport
        gap_report = EvidenceGapReport(run_id="", depth_profile=resolved)
        for entry in coverage.entries:
            if not entry.covered:
                deficit = entry.min_sources_required - entry.sources_found
                severity = "critical" if deficit >= entry.min_sources_required else "high" if deficit > 1 else "medium"
                gap = EvidenceGap(
                    family=entry.family,
                    required_min_sources=entry.min_sources_required,
                    found_sources=entry.sources_found,
                    gap_severity=severity,
                    suggested_query=entry.query_used,
                )
                gap_report.add_gap(gap)

        # 7. CitationAnchorRegistry — starts empty; populated by E3 synthesis
        citation_registry = CitationAnchorRegistry(run_id="")

        # 8. SynthesisGuidanceForPA — derived from C0 gate verdict
        gate_verdict = evaluate_c0_gate(coverage, portfolio, resolved)

        min_citation = profile_cfg.get("min_citation_anchors", 18)
        omit: list[str] = []
        caveats: list[str] = []
        if gate_verdict == "WEAK_WITH_CAVEATS":
            caveats = ["Note: Some sections may have limited source coverage."]
        elif gate_verdict == "FAIL_DEGRADE":
            omit = [e.family for e in coverage.entries if not e.covered]
            caveats = ["Insufficient evidence for full synthesis."]

        synthesis_guidance = SynthesisGuidanceForPA(
            depth_profile=resolved,
            c0_gate_verdict=gate_verdict,
            recommended_sections=tuple(
                e.family for e in coverage.entries if e.covered
            ),
            omit_sections=tuple(omit),
            caveat_prefixes=tuple(caveats),
            citation_density_target="standard" if gate_verdict == "PASS" else "reduced",
            confidence_floor=0.7 if gate_verdict == "PASS" else 0.5,
            notes=f"gate={gate_verdict} min_citations={min_citation}",
        )

        return BriefingEvidenceBundle(
            depth_profile=resolved,
            coverage_matrix=coverage,
            claim_evidence_map=claim_map,
            contradiction_matrix=contradiction,
            freshness_report=freshness,
            synthesis_guidance=synthesis_guidance,
            source_portfolio=portfolio,
            citation_registry=citation_registry,
            gap_report=gap_report,
        )
