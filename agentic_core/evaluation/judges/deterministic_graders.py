"""W9 Boundary Hardening — Deterministic Graders (Core-Owned)

Implements deterministic grading logic for apps_research dimensions.
Core owns execution. Apps own config/rubrics.

This module provides:
- Deterministic grading heuristics for company brief evaluation
- Score computation based on measurable features
- Evidence generation for downstream gate consumption

W9 Constraints:
- Judges do NOT emit X3 (Exit owns that)
- Judges do NOT write cache (read-only evaluation)
- Judges do NOT write L4 (read-only evaluation)
- Core owns judge execution; apps own config
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime, timezone
import re


@dataclass(frozen=True)
class DeterministicGradeResult:
    """Result from deterministic grading.
    
    Immutable result suitable for gate evidence consumption.
    """
    dimension: str
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    reasoning: str
    evidence_refs: Tuple[str, ...]
    grader_id: str
    is_calibrated: bool = True
    is_stub: bool = False
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    calibration_refs: Tuple[str, ...] = field(default_factory=tuple)


# ─────────────────────────────────────────────────────────────────────────────
# Dimension-Specific Deterministic Graders
# ─────────────────────────────────────────────────────────────────────────────

class DeterministicGraderRegistry:
    """Registry of deterministic graders for dimensions.
    
    Core owns this registry. Apps register dimension configs.
    """
    
    _graders: Dict[str, Callable[[str, Dict[str, Any]], DeterministicGradeResult]] = {}
    
    @classmethod
    def register(cls, dimension: str, grader_fn: Callable) -> None:
        """Register a deterministic grader for a dimension."""
        cls._graders[dimension] = grader_fn
    
    @classmethod
    def get(cls, dimension: str) -> Optional[Callable]:
        """Get grader for dimension if registered."""
        return cls._graders.get(dimension)
    
    @classmethod
    def grade(cls, dimension: str, content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
        """Execute grading for dimension."""
        grader = cls._graders.get(dimension)
        if grader is None:
            return DeterministicGradeResult(
                dimension=dimension,
                score=0.0,
                confidence=0.0,
                reasoning=f"No deterministic grader registered for dimension: {dimension}",
                evidence_refs=(),
                grader_id="core_unknown",
                is_stub=True,
                is_calibrated=False,
            )
        return grader(content, context)


# ─────────────────────────────────────────────────────────────────────────────
# Research Brief Dimension Graders
# ─────────────────────────────────────────────────────────────────────────────

def _grade_claim_support(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade claim support: citations per factual claim."""
    claim_pattern = r'[^.]+?(?:\d{4}|\$[\d,]+|percent|%)[^.]*\.'
    claims = re.findall(claim_pattern, content, re.IGNORECASE)
    
    claims_with_citations = sum(1 for claim in claims if re.search(r'\[\d+\]', claim))
    total_claims = len(claims) if claims else 1
    support_ratio = claims_with_citations / total_claims
    
    if support_ratio >= 0.8:
        score = 0.85 + (support_ratio - 0.8) * 0.375
    elif support_ratio >= 0.5:
        score = 0.60 + (support_ratio - 0.5) * 0.833
    else:
        score = support_ratio * 1.2
    
    score = min(1.0, max(0.0, score))
    confidence = 0.75 if claims else 0.5
    
    return DeterministicGradeResult(
        dimension="claim_support",
        score=score,
        confidence=confidence,
        reasoning=f"{claims_with_citations}/{len(claims)} claims with citations (ratio={support_ratio:.2f})",
        evidence_refs=("core://deterministic_graders/claim_support",),
        grader_id="core_claim_support",
        calibration_refs=("docs/reference/calibration/claim_support_baseline.json",),
    )


def _grade_citation_quality(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade citation quality: source authority indicators."""
    tier_1 = ["sec.gov", "10-k", "10-q", "annual report", "official", "earnings"]
    tier_2 = ["reuters", "bloomberg", "wsj", "cnbc", "forbes"]
    
    content_lower = content.lower()
    t1_count = sum(content_lower.count(ind) for ind in tier_1)
    t2_count = sum(content_lower.count(ind) for ind in tier_2)
    total = t1_count + t2_count
    
    if total == 0:
        score = 0.5
        reasoning = "No identifiable authority sources"
    else:
        weighted = (t1_count * 1.0 + t2_count * 0.8) / total
        score = 0.5 + weighted * 0.5
        reasoning = f"{t1_count} primary, {t2_count} credible sources"
    
    return DeterministicGradeResult(
        dimension="citation_quality",
        score=min(1.0, score),
        confidence=0.70,
        reasoning=reasoning,
        evidence_refs=("core://deterministic_graders/citation_quality",),
        grader_id="core_citation_quality",
        calibration_refs=("docs/reference/calibration/citation_quality_baseline.json",),
    )


def _grade_coverage_depth(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade coverage depth: section coverage against profile expectations."""
    expected_sections = context.get("expected_sections", ["overview", "financials", "leadership"])
    content_lower = content.lower()
    
    found = sum(1 for section in expected_sections if section in content_lower)
    coverage = found / len(expected_sections) if expected_sections else 0
    
    score = 0.4 + coverage * 0.6
    
    return DeterministicGradeResult(
        dimension="coverage_depth",
        score=min(1.0, score),
        confidence=0.75,
        reasoning=f"{found}/{len(expected_sections)} expected sections found",
        evidence_refs=("core://deterministic_graders/coverage_depth",),
        grader_id="core_coverage_depth",
        calibration_refs=("docs/reference/calibration/coverage_depth_baseline.json",),
    )


def _grade_contradiction_resolution(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade contradiction resolution: contradiction markers vs resolution markers."""
    contra_markers = ["however", "but", "although", "whereas"]
    resolution_markers = ["according to", "per [", "sources indicate"]
    
    content_lower = content.lower()
    contra_count = sum(content_lower.count(m) for m in contra_markers)
    res_count = sum(content_lower.count(m) for m in resolution_markers)
    
    if contra_count == 0:
        score = 1.0
        reasoning = "No contradiction markers detected"
    else:
        ratio = res_count / (contra_count * 2)
        score = 0.4 + min(ratio, 1.0) * 0.6
        reasoning = f"{contra_count} potential conflicts, {res_count} resolution markers"
    
    return DeterministicGradeResult(
        dimension="contradiction_resolution",
        score=min(1.0, score),
        confidence=0.70,
        reasoning=reasoning,
        evidence_refs=("core://deterministic_graders/contradiction_resolution",),
        grader_id="core_contradiction_resolution",
        calibration_refs=("docs/reference/calibration/contradiction_resolution_baseline.json",),
    )


def _grade_source_authority(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade source authority: tiered source indicators."""
    tier_1 = ["sec.gov", "10-k", "official", "annual report"]
    tier_2 = ["reuters", "bloomberg", "wsj", "ft.com"]
    
    content_lower = content.lower()
    t1 = sum(content_lower.count(ind) for ind in tier_1)
    t2 = sum(content_lower.count(ind) for ind in tier_2)
    total = t1 + t2
    
    if total == 0:
        score = 0.5
        reasoning = "No identifiable authority indicators"
    else:
        weighted = (t1 * 1.0 + t2 * 0.8) / total
        score = 0.5 + weighted * 0.5
        reasoning = f"{t1} primary, {t2} credible authority sources"
    
    return DeterministicGradeResult(
        dimension="source_authority",
        score=min(1.0, score),
        confidence=0.75,
        reasoning=reasoning,
        evidence_refs=("core://deterministic_graders/source_authority",),
        grader_id="core_source_authority",
        calibration_refs=("docs/reference/calibration/source_authority_baseline.json",),
    )


def _grade_cache_compatibility(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade cache compatibility: stable vs volatile indicators."""
    stable = [r"\d{4}", r"\$[\d,]+", r"founded in \d{4}", r"headquartered"]
    volatile = ["today", "yesterday", "breaking", "recently"]
    
    stable_count = sum(len(re.findall(p, content, re.I)) for p in stable)
    vol_count = sum(content.lower().count(v) for v in volatile)
    total = stable_count + vol_count
    
    if total == 0:
        score = 0.6
        reasoning = "No clear cacheability indicators"
    else:
        ratio = stable_count / total
        score = 0.4 + ratio * 0.6
        reasoning = f"{stable_count} stable, {vol_count} volatile indicators"
    
    return DeterministicGradeResult(
        dimension="cache_compatibility",
        score=min(1.0, score),
        confidence=0.70,
        reasoning=reasoning,
        evidence_refs=("core://deterministic_graders/cache_compatibility",),
        grader_id="core_cache_compatibility",
        calibration_refs=("docs/reference/calibration/cache_compatibility_baseline.json",),
    )


def _grade_briefing_injection(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade briefing injection: coverage of key briefing elements."""
    indicators = ["overview", "summary", "background", "founded", "revenue", "employees"]
    content_lower = content.lower()
    
    found = sum(1 for ind in indicators if ind in content_lower)
    coverage = found / len(indicators)
    
    score = 0.3 + coverage * 0.7
    
    return DeterministicGradeResult(
        dimension="briefing_injection",
        score=min(1.0, score),
        confidence=0.75,
        reasoning=f"{found}/{len(indicators)} briefing elements present",
        evidence_refs=("core://deterministic_graders/briefing_injection",),
        grader_id="core_briefing_injection",
        calibration_refs=("docs/reference/calibration/briefing_injection_baseline.json",),
    )


def _grade_downstream_relevance(content: str, context: Dict[str, Any]) -> DeterministicGradeResult:
    """Grade downstream relevance: indicators for target apps."""
    target = context.get("target_downstream", "both")
    
    if target == "rg":
        indicators = ["skills", "leadership", "achievements", "awards"]
    elif target == "lic":
        indicators = ["regulatory", "compliance", "financial strength", "risk"]
    else:
        indicators = ["skills", "compliance", "leadership", "financial"]
    
    content_lower = content.lower()
    found = sum(1 for ind in indicators if ind in content_lower)
    coverage = found / len(indicators)
    
    score = 0.5 + coverage * 0.5
    
    return DeterministicGradeResult(
        dimension="downstream_relevance",
        score=min(1.0, score),
        confidence=0.70,
        reasoning=f"{found}/{len(indicators)} relevance indicators for {target}",
        evidence_refs=("core://deterministic_graders/downstream_relevance",),
        grader_id="core_downstream_relevance",
        calibration_refs=("docs/reference/calibration/downstream_relevance_baseline.json",),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Register Core Deterministic Graders
# ─────────────────────────────────────────────────────────────────────────────

DeterministicGraderRegistry.register("claim_support", _grade_claim_support)
DeterministicGraderRegistry.register("citation_quality", _grade_citation_quality)
DeterministicGraderRegistry.register("coverage_depth", _grade_coverage_depth)
DeterministicGraderRegistry.register("contradiction_resolution", _grade_contradiction_resolution)
DeterministicGraderRegistry.register("source_authority", _grade_source_authority)
DeterministicGraderRegistry.register("cache_compatibility", _grade_cache_compatibility)
DeterministicGraderRegistry.register("briefing_injection", _grade_briefing_injection)
DeterministicGraderRegistry.register("downstream_relevance", _grade_downstream_relevance)


# ─────────────────────────────────────────────────────────────────────────────
# Run-context interface graders (AppGraderRegistry dispatch protocol)
# These accept (dim: str, run_context: Mapping[str, Any]) and return
# (score: float|int, evidence_refs: list[str]).  Apps may alias these without
# holding local scoring logic.
# ─────────────────────────────────────────────────────────────────────────────

_COVERAGE_DEPTH_PROFILE_TIER: Dict[str, float] = {
    "COMPANY_BRIEF_LIGHT": 0.0,
    "COMPANY_BRIEF_STANDARD": 0.0,
    "COMPANY_BRIEF_DEEP": 0.02,
    "COMPANY_BRIEF_DOSSIER": 0.05,
    "COMPANY_BRIEF_COMPETITIVE_SCAN": 0.03,
    "COMPANY_BRIEF_FORENSIC": 0.10,
}


def _get_coverage_depth_profile_min_anchors(profile: str) -> int:
    try:
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES  # noqa: PLC0415
        return int(_DEPTH_PROFILES.get(profile, {}).get("min_citation_anchors", 18))
    except (ImportError, AttributeError):
        return 18


def _get_coverage_depth_profile_required_families(profile: str) -> List[str]:
    try:
        from apps_research.engines.query_decomposer import _PROFILE_REQUIRED_FAMILIES  # noqa: PLC0415
        return list(_PROFILE_REQUIRED_FAMILIES.get(profile, []))
    except (ImportError, AttributeError):
        return []


def grade_coverage_depth_run_context(
    dim: str,  # noqa: ARG001 — kept for AppGraderRegistry dispatch interface parity
    run_context: Dict[str, Any],
) -> Tuple[Any, List[str]]:
    """Core-owned coverage_depth grader using the AppGraderRegistry run_context protocol.

    Accepts (dim, run_context) and returns (score, evidence_refs) per the protocol used
    by AppGraderRegistry dispatch and the apps_research compatibility facade.

    apps_research does NOT own this logic. This function lives in agentic_core and is
    re-exported by apps_research/engines/judges/coverage_depth_judge.py as a compatibility
    alias. No scoring logic may exist inside apps_research.
    """
    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (  # noqa: PLC0415
        GRADER_UNKNOWN_SENTINEL,
    )

    output = run_context.get("output") or {}
    if not hasattr(output, "get"):
        return GRADER_UNKNOWN_SENTINEL, []

    c0_bundle = output.get("c0_bundle") or output.get("_c0_bundle") or {}
    depth_profile = (
        output.get("research_depth_profile")
        or output.get("_depth_profile")
        or run_context.get("research_depth_profile")
        or ""
    )

    required_families = _get_coverage_depth_profile_required_families(depth_profile)
    min_anchors = _get_coverage_depth_profile_min_anchors(depth_profile)
    tier_bonus_raw = _COVERAGE_DEPTH_PROFILE_TIER.get(depth_profile, 0.0)

    if not required_families and not (hasattr(c0_bundle, "get") and c0_bundle):
        return GRADER_UNKNOWN_SENTINEL, []

    present_families: set = set()
    if hasattr(c0_bundle, "get"):
        findings = c0_bundle.get("findings") or {}
        if hasattr(findings, "items"):
            for fam, val in findings.items():
                if val:
                    present_families.add(fam)

    if required_families:
        matched = len(present_families & set(required_families))
        family_ratio = min(1.0, matched / len(required_families))
    else:
        family_ratio = 1.0 if present_families else 0.0

    citation_anchor_count = 0
    raw_count = output.get("citation_anchor_count")
    if raw_count is not None:
        try:
            citation_anchor_count = int(raw_count)
        except (TypeError, ValueError):
            pass
    elif hasattr(c0_bundle, "get"):
        sps = c0_bundle.get("source_portfolio_summary") or {}
        if hasattr(sps, "get"):
            try:
                citation_anchor_count = int(sps.get("total_final_sources", 0) or 0)
            except (TypeError, ValueError):
                pass

    density_ratio = min(1.0, citation_anchor_count / max(min_anchors, 1))

    raw_score = (
        0.50 * family_ratio
        + 0.30 * density_ratio
        + 0.20 * min(1.0, tier_bonus_raw * 10)
    )
    score = min(1.0, max(0.0, raw_score))

    n_required = len(required_families) if required_families else 0
    n_matched = len(present_families & set(required_families)) if required_families else 0
    evidence = [
        f"family_coverage={family_ratio:.2f} ({n_matched}/{n_required} families)",
        f"density_ratio={density_ratio:.2f} ({citation_anchor_count}/{min_anchors} anchors)",
        f"profile={depth_profile or 'unknown'} tier_bonus={tier_bonus_raw:.2f}",
    ]
    return score, evidence
