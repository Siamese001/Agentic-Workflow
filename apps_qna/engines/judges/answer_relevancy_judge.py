"""apps_qna.engines.judges.answer_relevancy_judge — RAG answer-relevancy scorer.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-qna-deferred-e5-f7a2b1.md`` E2.3

Scores how well the generated answer addresses the interview question intent.

Scoring model (dual-path)
-------------------------
**LLM path** (preferred): When ``run_context["provider_context"]`` is present
and has a configured model, dispatches an LLM judge prompt.

**Heuristic fallback**: Deterministic multi-signal heuristic (overlap, length,
uniqueness).

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "qna::answer_relevancy_judge::v2"

_SCORE_RE = re.compile(r"\b([01]\.\d{1,2})\b|\b(1\.0|0\.0)\b")

_RELEVANCY_PROMPT_TEMPLATE = """You are a RAG evaluation judge. Score answer relevancy on a scale of 0.0 to 1.0.

Answer relevancy measures: how well the generated answer directly addresses the interview question. Penalize off-topic, evasive, or overly generic answers.

**Question**: {question}

**Answer**: {answer}

Score 1.0 = answer directly and completely addresses the question.
Score 0.0 = answer is completely off-topic or non-responsive.

Respond with ONLY a JSON object: {{"score": <float 0.0-1.0>, "rationale": "<brief reason>"}}
"""


def _parse_llm_score(response: str) -> float | None:
    """Parse a 0.0-1.0 score from LLM response."""
    if not response:
        return None
    try:
        data = json.loads(response)
        if isinstance(data, dict) and "score" in data:
            val = float(data["score"])
            if 0.0 <= val <= 1.0:
                return val
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    m = _SCORE_RE.search(response)
    if m:
        val = float(m.group(1) or m.group(2))
        if 0.0 <= val <= 1.0:
            return val
    return None

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
    """LLM-backed answer-relevancy judge with heuristic fallback."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"answer_relevancy::v2::precomputed={pre:.2f}"]

        answer: str = output.get("answer") or output.get("response") or ""
        question: str = output.get("question") or output.get("query") or ""

        if not answer or not question:
            return GRADER_UNKNOWN_SENTINEL, []

        # LLM judge path — use injected context or auto-build from env
        provider_ctx = (run_context or {}).get("provider_context")
        if provider_ctx is None:
            try:
                from apps_qna.integrations.provider_adapter import (  # noqa: PLC0415
                    build_judge_provider_context_from_env,
                )
                provider_ctx = build_judge_provider_context_from_env()
            except Exception:
                provider_ctx = None
        if provider_ctx is not None and hasattr(provider_ctx, "dispatch") and hasattr(provider_ctx, "has_model"):
            if provider_ctx.has_model():
                prompt = _RELEVANCY_PROMPT_TEMPLATE.format(
                    question=question[:500],
                    answer=answer[:1000],
                )
                response = provider_ctx.dispatch(prompt)
                llm_score = _parse_llm_score(response)
                if llm_score is not None:
                    return llm_score, [
                        f"answer_relevancy::v2::llm_judge={llm_score:.2f}",
                    ]

        # Heuristic fallback
        q_words = _tokenize(question)
        a_words = _tokenize(answer)

        overlap = _score_overlap(q_words, a_words)
        length = _score_length(answer)
        uniqueness = _score_uniqueness(answer)

        score = max(0.0, min(1.0, 0.40 * overlap + 0.30 * length + 0.30 * uniqueness))
        evidence_refs = [
            f"answer_relevancy::v2::heuristic_overlap={overlap:.2f}",
            f"answer_relevancy::v2::heuristic_length={length:.2f}",
            f"answer_relevancy::v2::heuristic_uniqueness={uniqueness:.2f}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return AnswerRelevancyJudge().grade(dim, run_context)


__all__ = ["AnswerRelevancyJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
