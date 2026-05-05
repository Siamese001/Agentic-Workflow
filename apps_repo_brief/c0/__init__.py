# apps_repo_brief C0 adapter package.
#
# Defines the interface contract between apps_repo_brief and the C0
# Context Engine. apps_repo_brief does NOT implement C0 retrieval —
# it provides normalization adapters and depth-profile configs that
# C0 consumes to produce its authoritative FinalEvidenceContract.v1.
#
# Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.4, §P3.7
from apps_repo_brief.c0.repo_brief_c0_adapter import RepoBriefC0Adapter
from apps_repo_brief.c0.repo_brief_final_contract import (
    RepoBriefFinalEvidenceContract,
    BriefingCoverageMatrix,
    SourcePortfolioSummary,
    ClaimEvidenceMap,
    ContradictionMatrix,
    FreshnessReport,
    SectionGapReport,
    SynthesisGuidanceForPA,
)

__all__ = [
    "RepoBriefC0Adapter",
    "RepoBriefFinalEvidenceContract",
    "BriefingCoverageMatrix",
    "SourcePortfolioSummary",
    "ClaimEvidenceMap",
    "ContradictionMatrix",
    "FreshnessReport",
    "SectionGapReport",
    "SynthesisGuidanceForPA",
]
