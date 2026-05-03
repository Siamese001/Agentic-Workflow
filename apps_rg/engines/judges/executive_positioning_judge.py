"""apps_rg.engines.judges.executive_positioning_judge — PROMOTED (v2 deterministic).

Plan: ``.windsurf/plans/apps-eval-harness-final-8f3e21.md`` W2.P1.

PROMOTION HISTORY
=================
- v1 (stub, parent plan apps-eval-harness-deferred-e4a1b7 W2.P1): returned
  GRADER_UNKNOWN_SENTINEL always.
- **v2 (this plan)**: deterministic heuristic scorer — no LLM call,
  no human-labeled holdout required. Scores the executive-positioning
  quality of an `apps_rg` output on a 0..1 scale based on measurable
  textual features. This is NOT a full-fidelity LLM judge; it is a
  real, deterministic grader that replaces the UNKNOWN sentinel with
  a signal-bearing score while calibration-backed LLM scoring remains
  deferred to its own future plan.

Scoring model (v2)
------------------
Reads ``run_context["output"]["text"]`` (falls back to ``output.response``
then to empty string) and combines four measurable features:

1. **Executive lexicon coverage** — fraction of 12 canonical
   executive-positioning terms present (strategy, roadmap, stakeholder,
   quarterly, KPI, ROI, executive, align, prioritize, board, initiative,
   outcome). Weighted 0.30.
2. **Specificity** — count of numbers/percentages; saturates at 3.
   Weighted 0.25.
3. **Outcome framing** — presence of outcome verbs (delivered, achieved,
   drove, improved, increased, reduced). Weighted 0.25.
4. **Length adequacy** — text length between 50 and 2000 chars scores
   1.0; outside range penalized linearly. Weighted 0.20.

When the output text is empty, returns ``(GRADER_UNKNOWN_SENTINEL, [])``
to preserve fail-open behavior.

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
Returns (score ∈ [0, 1], evidence_refs) or (GRADER_UNKNOWN_SENTINEL, [])
when abstaining.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
"""This judge is a promoted real implementation (deterministic v2)."""

GRADER_ID: str = "rg::executive_positioning_judge::v2"
"""Roster ID — bumped from v1 when promoted from stub to deterministic."""

_EXEC_LEXICON: frozenset[str] = frozenset(
    {
        "strategy",
        "roadmap",
        "stakeholder",
        "quarterly",
        "kpi",
        "roi",
        "executive",
        "align",
        "prioritize",
        "board",
        "initiative",
        "outcome",
    }
)

_OUTCOME_VERBS: frozenset[str] = frozenset(
    {"delivered", "achieved", "drove", "improved", "increased", "reduced"}
)

_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")
_WORD_PATTERN = re.compile(r"\b[a-zA-Z]+\b")


def _extract_text(run_context: Mapping[str, Any]) -> str:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("text", "response", "content", "answer"):
            value = out.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return ""


def _score_lexicon(text: str) -> float:
    words = {w.lower() for w in _WORD_PATTERN.findall(text)}
    hits = len(words & _EXEC_LEXICON)
    if not _EXEC_LEXICON:
        return 0.0
    return min(1.0, hits / max(1, len(_EXEC_LEXICON) // 2))


def _score_specificity(text: str) -> float:
    numbers = _NUMBER_PATTERN.findall(text)
    return min(1.0, len(numbers) / 3.0)


def _score_outcome_framing(text: str) -> float:
    words = {w.lower() for w in _WORD_PATTERN.findall(text)}
    hits = len(words & _OUTCOME_VERBS)
    return 1.0 if hits >= 1 else 0.0


def _score_length(text: str) -> float:
    n = len(text)
    if 50 <= n <= 2000:
        return 1.0
    if n < 50:
        return max(0.0, n / 50.0)
    # n > 2000 — linear penalty, floor at 0.3
    return max(0.3, 1.0 - (n - 2000) / 5000.0)


def _compute_score(text: str) -> float:
    return (
        0.30 * _score_lexicon(text)
        + 0.25 * _score_specificity(text)
        + 0.25 * _score_outcome_framing(text)
        + 0.20 * _score_length(text)
    )


class ExecutivePositioningJudge:
    """Deterministic executive-positioning judge (v2)."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        text = _extract_text(run_context or {})
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []
        score = max(0.0, min(1.0, _compute_score(text)))
        evidence_refs = [
            f"exec_positioning::v2::lexicon={_score_lexicon(text):.2f}",
            f"exec_positioning::v2::specificity={_score_specificity(text):.2f}",
            f"exec_positioning::v2::outcome={_score_outcome_framing(text):.2f}",
            f"exec_positioning::v2::length={_score_length(text):.2f}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return ExecutivePositioningJudge().grade(dim, run_context)


__all__ = ["ExecutivePositioningJudge", "grade", "IS_STUB", "GRADER_ID"]
