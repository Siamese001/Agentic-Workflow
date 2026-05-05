"""apps_qna.engines.judges.answer_relevancy_judge — deterministic answer-relevancy scorer.

Plan: ``.windsurf/plans/apps-qna-spine-deferred-e9c5b3.md`` D1.2

Scores how well the generated answer addresses the interview question intent.

Scoring model
-------------
Reads the following output keys (graceful fallback to empty on missing):

- ``output.answer``          — generated answer text
- ``output.question``        — interview question text
- ``output.dim_scores.answer_relevancy`` — pre-computed score (takes precedence)

When ``dim_scores.answer_relevancy`` is present and numeric, returns it directly.
Otherwise applies a deterministic heuristic combining:

1. **Token overlap** — Jaccard similarity of question vs answer word sets.
   Weighted 0.40.
2. **Answer length adequacy** — 20–500 chars → 1.0; outside → penalized.
   Weighted 0.30.
3. **Non-repetition** — fraction of unique words in answer. Weighted 0.30.

When answer or question is empty, returns ``GRADER_UNKNOWN_SENTINEL``.

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "qna::answer_relevancy_judge::v1"

_WORD_RE = re.compile(r"\b[a-zA-Z0-9]+\b")
_STOP_WORDS: frozenset[str] = frozenset(
    {"the", "a", "an", "is", "in", "of", "to", "and", "or", "for", "with", "on", "at"}
)


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)} - _STOP_WORDS


def _get_output(run_context: Mapping[str, Any]) -> Mapping[str, Any]:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    return out if isinstance(out, Mapping) else {}


def _precomputed_score(output: Mapping[str, Any]) -> float | None:
    dim_scores = output.get("dim_scores")
    if not isinstance(dim_scores, Mapping):
        return None
    val = dim_scores.get("answer_relevancy")
    if isinstance(val, (int, float)) and 0.0 <= float(val) <= 1.0:
        return float(val)
    return None


def _score_overlap(q_words: set[str], a_words: set[str]) -> float:
    if not q_words or not a_words:
        return 0.0
    union = q_words | a_words
    return len(q_words & a_words) / max(1, len(union))


def _score_length(answer: str) -> float:
    n = len(answer)
    if 20 <= n <= 500:
        return 1.0
    if n < 20:
        return max(0.0, n / 20.0)
    return max(0.3, 1.0 - (n - 500) / 2000.0)


def _score_uniqueness(answer: str) -> float:
    all_words = _WORD_RE.findall(answer.lower())
    if not all_words:
        return 0.0
    return len(set(all_words)) / max(1, len(all_words))


class AnswerRelevancyJudge:
    """Deterministic answer-relevancy judge for apps_qna RAG evaluation."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"answer_relevancy::v1::precomputed={pre:.2f}"]

        answer: str = output.get("answer") or output.get("response") or ""
        question: str = output.get("question") or output.get("query") or ""

        if not answer or not question:
            return GRADER_UNKNOWN_SENTINEL, []

        q_words = _tokenize(question)
        a_words = _tokenize(answer)

        overlap = _score_overlap(q_words, a_words)
        length = _score_length(answer)
        uniqueness = _score_uniqueness(answer)

        score = max(0.0, min(1.0, 0.40 * overlap + 0.30 * length + 0.30 * uniqueness))
        evidence_refs = [
            f"answer_relevancy::v1::overlap={overlap:.2f}",
            f"answer_relevancy::v1::length={length:.2f}",
            f"answer_relevancy::v1::uniqueness={uniqueness:.2f}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return AnswerRelevancyJudge().grade(dim, run_context)


__all__ = ["AnswerRelevancyJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
