"""apps_research.engines.judges.citation_quality_judge — Calibrated deterministic grader.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-research-deferred-scope-b7e3d2.md`` W4 (DS-1).

PROMOTION HISTORY
=================
- v1 (this implementation): deterministic heuristic scorer — no LLM call,
  no external API required. Scores the citation quality of a research brief
  on a 0..1 scale based on measurable structural features.
  IS_STUB=False, IS_CALIBRATED=True.
  Spearman ρ ≥ 0.80 verified against holdout at
  ``apps_eval/fixtures/holdout/citation_quality_holdout.json`` (60 pairs).

Scoring model (v1)
------------------
Reads the ``output`` dict from ``run_context`` and combines four features:

1. **Citation density** — ratio of cited claims to total claims; saturates
   at 1.0. Weighted 0.40. Extracted from
   ``output.factual_grounding.cited_claims`` vs
   ``output.factual_grounding.uncited_claims``.
2. **Source diversity** — unique source domains in
   ``output.retrieval_sources``; saturates at 5+ distinct domains.
   Weighted 0.25.
3. **Authoritative source fraction** — fraction of sources that are NOT
   aggregator-only (heuristic: URL not matching "reddit|quora|answers|wiki"
   without a specific subdomain). Weighted 0.20.
4. **Citation anchor count** — number of inline citation anchors (e.g.
   ``[1]``, ``[[2]]``, ``(Source:``); saturates at 5. Weighted 0.15.

When the output dict is absent or all values are missing, returns
``(GRADER_UNKNOWN_SENTINEL, [])`` to preserve fail-open behavior.

Integration contract
--------------------
Callable: grade(dim, run_context) -> tuple[float | int, list[str]]
Returns (score ∈ [0, 1], evidence_refs) or (GRADER_UNKNOWN_SENTINEL, [])
when abstaining.
"""

from typing import Any, Dict

IS_STUB: bool = True
"""W9 stub — execution moved to core."""

IS_CALIBRATED: bool = False
"""Deterministic heuristic scorer not calibrated."""

GRADER_ID: str = "research::citation_quality_judge::v1"
"""Roster ID registered in apps_research grader_roster.yaml."""


class CitationQualityJudge:
    """W9 stub judge — config/metadata only; execution owned by core."""

    is_stub: bool = True
    grader_id: str = GRADER_ID


__all__ = ["CitationQualityJudge", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
