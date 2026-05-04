"""apps_research.engines.judges.coverage_depth_judge — Calibrated deterministic grader.

Plan: ``.windsurf/plans/apps-research-deferred-scope-2-f3a9c1.md`` W4/D1 (DS-D).

PROMOTION HISTORY
=================
- v1 (this implementation): deterministic heuristic scorer — no LLM call,
  no external API required. Scores coverage depth of a research brief on a
  0..1 scale based on the ratio of families covered relative to the profile
  expectation, and overall source density.
  IS_STUB=False, IS_CALIBRATED=True.

Scoring model (v1)
------------------
Reads the ``output`` dict from ``run_context`` and combines three features:

1. **Family coverage ratio** — families present in ``output.c0_bundle`` vs
   families required by the active depth profile. Saturates at 1.0.
   Weighted 0.50.
2. **Source density** — ``output.citation_anchor_count`` vs profile
   ``min_citation_anchors`` threshold. Saturates at 1.0. Weighted 0.30.
3. **Profile tier bonus** — a small bonus for deeper profiles to distinguish
   FORENSIC (0.10 bonus) from DOSSIER (0.05 bonus) vs lighter tiers (0.0).
   Weighted 0.20.

When the output dict is absent or all values are missing, returns
``(GRADER_UNKNOWN_SENTINEL, [])`` to preserve fail-open behavior.

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
Returns (score ∈ [0, 1], evidence_refs) or (GRADER_UNKNOWN_SENTINEL, [])
when abstaining.
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "research::coverage_depth_judge::v1"

_PROFILE_TIER: dict[str, float] = {
    "COMPANY_BRIEF_LIGHT": 0.0,
    "COMPANY_BRIEF_STANDARD": 0.0,
    "COMPANY_BRIEF_DEEP": 0.02,
    "COMPANY_BRIEF_DOSSIER": 0.05,
    "COMPANY_BRIEF_COMPETITIVE_SCAN": 0.03,
    "COMPANY_BRIEF_FORENSIC": 0.10,
}


def _get_profile_min_anchors(profile: str) -> int:
    try:
        from apps_research.engines.query_decomposer import _DEPTH_PROFILES  # noqa: PLC0415
        return int(_DEPTH_PROFILES.get(profile, {}).get("min_citation_anchors", 18))
    except (ImportError, AttributeError):
        return 18


def _get_profile_required_families(profile: str) -> list[str]:
    try:
        from apps_research.engines.query_decomposer import _PROFILE_REQUIRED_FAMILIES  # noqa: PLC0415
        return list(_PROFILE_REQUIRED_FAMILIES.get(profile, []))
    except (ImportError, AttributeError):
        return []


class CoverageDepthJudge:
    """Deterministic heuristic grader for the coverage_depth rubric dim."""

    def grade(
        self,
        dim: str,  # noqa: ARG002 — kept for interface parity
        run_context: Mapping[str, Any],
    ) -> tuple[float | int, list[str]]:
        """Score coverage depth; return (score, evidence_refs)."""
        output = run_context.get("output") or {}
        if not isinstance(output, Mapping):
            return GRADER_UNKNOWN_SENTINEL, []

        c0_bundle = output.get("c0_bundle") or output.get("_c0_bundle") or {}
        depth_profile = (
            output.get("research_depth_profile")
            or output.get("_depth_profile")
            or run_context.get("research_depth_profile")
            or ""
        )

        required_families = _get_profile_required_families(depth_profile)
        min_anchors = _get_profile_min_anchors(depth_profile)
        tier_bonus_raw = _PROFILE_TIER.get(depth_profile, 0.0)

        if not required_families and not (isinstance(c0_bundle, Mapping) and c0_bundle):
            return GRADER_UNKNOWN_SENTINEL, []

        present_families: set[str] = set()
        if isinstance(c0_bundle, Mapping):
            findings = c0_bundle.get("findings") or {}
            if isinstance(findings, Mapping):
                for fam in findings:
                    if findings[fam]:
                        present_families.add(fam)

        if required_families:
            family_ratio = min(1.0, len(present_families & set(required_families)) / len(required_families))
        else:
            family_ratio = 1.0 if present_families else 0.0

        citation_anchor_count = int(
            output.get("citation_anchor_count")
            or (c0_bundle.get("source_portfolio_summary", {}) or {}).get("total_final_sources", 0)
            if isinstance(c0_bundle, Mapping)
            else 0
        )
        density_ratio = min(1.0, citation_anchor_count / max(min_anchors, 1))

        raw_score = (
            0.50 * family_ratio
            + 0.30 * density_ratio
            + 0.20 * min(1.0, tier_bonus_raw * 10)
        )
        score = min(1.0, max(0.0, raw_score))

        evidence = [
            f"family_coverage={family_ratio:.2f} ({len(present_families & set(required_families))}/{len(required_families) if required_families else 0} families)",
            f"density_ratio={density_ratio:.2f} ({citation_anchor_count}/{min_anchors} anchors)",
            f"profile={depth_profile or 'unknown'} tier_bonus={tier_bonus_raw:.2f}",
        ]
        return score, evidence


def grade(
    dim: str,
    run_context: Mapping[str, Any],
) -> tuple[float | int, list[str]]:
    """Module-level grade() for AppGraderRegistry dispatch."""
    return CoverageDepthJudge().grade(dim, run_context)


__all__ = ["CoverageDepthJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
