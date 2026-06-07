"""apps_lic.engines.judges.antipattern_clean_judge — deterministic heuristic (v1).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-deferred-scope-followup-d3f9b2.md W2 D1-P2
Exit rubric dim: antipattern_clean

Scores 0.0 (antipatterns present) to 1.0 (clean).

Anti-double-counting discipline
---------------------------------
The exit rubric already runs the rule-based ``outreach_antipattern_detector``
as the primary hard-fail gate for ``antipattern_clean``. This judge provides
a **complementary soft score** that:

1. Runs the same default antipattern detector so the score reflects known
   patterns (consistent, not additive noise).
2. Adds a **severity weighting** — some patterns are more friction-inducing
   than others.
3. Returns a continuous 0.0–1.0 score for use in downstream calibration
   / trend tracking, NOT as a duplicate hard-fail.

The caller must NOT use this judge as a second hard-fail gate. The score
signal is useful for: Spearman calibration vs human ratings, trend
monitoring, and surfacing near-miss drafts (score near 0.5) for review.

Scoring model
-------------
- 1.0  → no antipattern matches (``is_clean=True``)
- 0.0  → severe density of matches
- Score formula: ``1.0 - min(1.0, weighted_hit_count / 3.0)``
  where weighted_hit_count = Σ match_weight for each matched pattern
  (default weight 1.0; patterns with severity="high" weight 2.0).
"""

from __future__ import annotations

from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)
from apps_lic.engines.outreach_antipattern_detector import OutreachAntipatternDetector

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "lic::antipattern_clean_judge::v1"

_HIGH_SEVERITY_CODES: frozenset[str] = frozenset({
    "FABRICATION",
    "CONFIDENTIAL_LEAK",
    "SEND_MODE_FORBIDDEN",
})

_detector = OutreachAntipatternDetector()


def _extract_text(ctx: dict[str, Any]) -> str:
    out = ctx.get("output")
    if isinstance(out, dict):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _weighted_hit_count(matches: list[Any]) -> float:
    total = 0.0
    for m in matches:
        reason_codes = getattr(m, "reason_codes", []) or []
        weight = 2.0 if any(rc in _HIGH_SEVERITY_CODES for rc in reason_codes) else 1.0
        total += weight
    return total


class AntipatternCleanJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        ctx = run_context or {}
        text = _extract_text(ctx)
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []
        result = _detector.detect(text)
        if result.is_clean:
            score = 1.0
        else:
            whc = _weighted_hit_count(result.matches)
            score = max(0.0, 1.0 - min(1.0, whc / 3.0))
        refs = [
            f"antipattern_clean::v1::is_clean={result.is_clean}",
            f"antipattern_clean::v1::match_count={len(result.matches)}",
            f"antipattern_clean::v1::score={score:.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return AntipatternCleanJudge().grade(dim, run_context)


__all__ = ["AntipatternCleanJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
