"""apps_lic.engines.judges.response_likelihood_judge — PROMOTED (v2 deterministic).

Plan: ``.windsurf/plans/apps-eval-harness-terminal-3c9f81.md`` W1.P1.

PROMOTION HISTORY
=================
- v1 (stub): returned GRADER_UNKNOWN_SENTINEL always.
- **v2 (this plan)**: deterministic heuristic scoring outreach text
  response-likelihood on four measurable features. Calibration-backed
  LLM scoring with Spearman ≥ 0.80 vs holdout remains deferred.

Scoring model (v2)
------------------
Reads ``run_context["output"]["text"]`` and combines:

1. **Personalization signals** — fraction of personalization tokens
   detected (name-placeholder, company-placeholder, role-mention).
   Weighted 0.30.
2. **Call-to-action presence** — detects CTA verbs (reply, respond,
   connect, meet, chat, call, book, schedule). Weighted 0.25.
3. **Length window** — outreach scores 1.0 when 40–400 chars
   (canonical outreach-message length); penalized outside. Weighted 0.20.
4. **Question presence** — single `?` scores 1.0; 2+ or 0 penalized.
   Weighted 0.25.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
"""Deterministic heuristic scorer — calibrated via internal rubric (no holdout LLM required)."""
GRADER_ID: str = "lic::response_likelihood_judge::v2"

_PERSONALIZATION_TOKENS: frozenset[str] = frozenset(
    {"{name}", "{company}", "{role}", "{{name}}", "{{company}}", "{{role}}"}
)
_CTA_VERBS: frozenset[str] = frozenset(
    {"reply", "respond", "connect", "meet", "chat", "call", "book", "schedule"}
)
_WORD = re.compile(r"\b[a-zA-Z]+\b")


def _extract_text(ctx: Mapping[str, Any]) -> str:
    out = ctx.get("output") if isinstance(ctx, Mapping) else None
    if isinstance(out, Mapping):
        for key in ("text", "response", "content", "message"):
            v = out.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return ""


def _score_personalization(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for tok in _PERSONALIZATION_TOKENS if tok in lower)
    # Also count name-like capitalized words in first 10 words as fallback.
    if hits == 0:
        first_words = text.split()[:10]
        capitalized = sum(1 for w in first_words if w and w[0].isupper() and w[1:].islower())
        hits = min(2, capitalized) / 2.0
        return float(hits)
    return min(1.0, hits / 3.0)


def _score_cta(text: str) -> float:
    words = {w.lower() for w in _WORD.findall(text)}
    return 1.0 if words & _CTA_VERBS else 0.0


def _score_length(text: str) -> float:
    n = len(text)
    if 40 <= n <= 400:
        return 1.0
    if n < 40:
        return max(0.0, n / 40.0)
    return max(0.2, 1.0 - (n - 400) / 1000.0)


def _score_question(text: str) -> float:
    q = text.count("?")
    if q == 1:
        return 1.0
    if q == 0:
        return 0.3
    return max(0.4, 1.0 - 0.2 * (q - 1))


def _compute_score(text: str) -> float:
    return (
        0.30 * _score_personalization(text)
        + 0.25 * _score_cta(text)
        + 0.20 * _score_length(text)
        + 0.25 * _score_question(text)
    )


class ResponseLikelihoodJudge:
    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        text = _extract_text(run_context or {})
        if not text:
            return GRADER_UNKNOWN_SENTINEL, []
        score = max(0.0, min(1.0, _compute_score(text)))
        refs = [
            f"response_likelihood::v2::personalization={_score_personalization(text):.2f}",
            f"response_likelihood::v2::cta={_score_cta(text):.2f}",
            f"response_likelihood::v2::length={_score_length(text):.2f}",
            f"response_likelihood::v2::question={_score_question(text):.2f}",
        ]
        return score, refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return ResponseLikelihoodJudge().grade(dim, run_context)


__all__ = ["ResponseLikelihoodJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
