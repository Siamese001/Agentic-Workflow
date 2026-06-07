"""apps_qna.engines.judges.interview_card_quality_judge — LLM-as-judge for interview card quality.

Plan: ``docs/archive/windsurf/legacy-tree/plans/bge-m3-deferred-scope-remaining-c4e7a1.md`` W2

Scores the overall quality of a generated interview card answer using an LLM
judge (Anthropic claude-sonnet-4-6 by default, configured via ANTHROPIC_MODEL).

Scoring model
-------------
Sends a structured rubric prompt to the LLM judge with:
  - ``output.question``   — interview question text
  - ``output.answer``     — generated answer text
  - ``output.context``    — retrieved context chunks (optional)

The LLM returns a JSON score on [0.0, 1.0] with reasoning.

Graceful degradation
--------------------
- When ``ANTHROPIC_API_KEY`` is not set, returns ``GRADER_UNKNOWN_SENTINEL``.
- When the LLM call fails (timeout, rate-limit, bad JSON), logs a warning and
  returns ``GRADER_UNKNOWN_SENTINEL`` — never raises.
- ``IS_CALIBRATED`` is ``False`` until Spearman ≥ 0.80 on holdout is verified
  (see ``ops_scripts/ci/check_apps_qna_judge_spearman.py``).

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = False
GRADER_ID: str = "qna::interview_card_quality_judge::v1"

_LOGGER = logging.getLogger(__name__)
  # guardian: allow-hardcoded-secret -- P1 ADG burndown
_ANTHROPIC_API_KEY_VAR = "ANTHROPIC_API_KEY"  # guardian: allow-hardcoded-secret -- P1 ADG burndown
_ANTHROPIC_MODEL_VAR = "ANTHROPIC_MODEL"
_DEFAULT_MODEL = "claude-sonnet-4-6"
_JUDGE_TIMEOUT_SECONDS = 30

_RUBRIC_PROMPT = """\
You are an expert evaluator for AI-generated interview preparation content.

Given an interview question and a generated answer, score the answer quality on a scale from 0.0 to 1.0.

Evaluate on these criteria:
1. **Relevance** — Does the answer directly address the question asked?
2. **Completeness** — Does the answer cover the key concepts a candidate should know?
3. **Accuracy** — Is the content factually correct and technically sound?
4. **Clarity** — Is the answer clear, well-structured, and easy to follow?
5. **Actionability** — Does the answer give the candidate concrete talking points?

Interview Question:
{question}

Generated Answer:
{answer}

{context_section}

Respond ONLY with a JSON object in this exact format:
{{
  "score": <float between 0.0 and 1.0>,
  "reasoning": "<one sentence explanation>",
  "criteria_scores": {{
    "relevance": <0.0-1.0>,
    "completeness": <0.0-1.0>,
    "accuracy": <0.0-1.0>,
    "clarity": <0.0-1.0>,
    "actionability": <0.0-1.0>
  }}
}}
"""

_SCORE_RE = re.compile(r'"score"\s*:\s*([0-9]*\.?[0-9]+)')


def _get_api_key() -> str | None:
    return os.environ.get(_ANTHROPIC_API_KEY_VAR, "").strip() or None


def _get_model() -> str:
    return os.environ.get(_ANTHROPIC_MODEL_VAR, "").strip() or _DEFAULT_MODEL


def _get_output(run_context: Mapping[str, Any]) -> Mapping[str, Any]:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    return out if isinstance(out, Mapping) else {}


def _call_anthropic(question: str, answer: str, context: str | None) -> tuple[float, list[str]]:
    """Call Anthropic API synchronously and return (score, evidence_refs)."""
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "anthropic package not installed. Run: pip install anthropic"
        ) from exc

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    context_section = (
        f"Retrieved Context:\n{context[:2000]}\n" if context else "(No context provided)"
    )
    prompt = _RUBRIC_PROMPT.format(
        question=question[:500],
        answer=answer[:2000],
        context_section=context_section,
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=_get_model(),
        max_tokens=512,
        timeout=_JUDGE_TIMEOUT_SECONDS,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text if message.content else ""

    # Parse JSON response
    try:
        parsed = json.loads(raw)
        score = float(parsed["score"])
        score = max(0.0, min(1.0, score))
        reasoning = str(parsed.get("reasoning", ""))[:200]
        criteria = parsed.get("criteria_scores", {})
        evidence_refs = [
            f"interview_card_quality::v1::score={score:.2f}",
            f"interview_card_quality::v1::model={_get_model()}",
            f"interview_card_quality::v1::reasoning={reasoning}",
        ]
        for k, v in criteria.items():
            if isinstance(v, (int, float)):
                evidence_refs.append(f"interview_card_quality::v1::{k}={float(v):.2f}")
        return score, evidence_refs
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Fallback: extract score via regex if JSON parse fails
        m = _SCORE_RE.search(raw)
        if m:
            score = max(0.0, min(1.0, float(m.group(1))))
            return score, [
                f"interview_card_quality::v1::score={score:.2f}::regex_fallback",
                f"interview_card_quality::v1::model={_get_model()}",
            ]
        raise ValueError(f"Cannot parse LLM judge response: {raw[:200]!r}")


class InterviewCardQualityJudge:
    """LLM-as-judge for interview card answer quality (apps_qna).

    Uses Anthropic claude-sonnet-4-6 by default. Returns GRADER_UNKNOWN_SENTINEL
    gracefully when ANTHROPIC_API_KEY is unset or any API error occurs.
    IS_CALIBRATED=False until Spearman >= 0.80 on holdout is verified.
    """

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        # Check for pre-computed score first
        dim_scores = output.get("dim_scores")
        if isinstance(dim_scores, Mapping):
            val = dim_scores.get("interview_card_quality")
            if isinstance(val, (int, float)) and 0.0 <= float(val) <= 1.0:
                return float(val), [f"interview_card_quality::v1::precomputed={float(val):.2f}"]

        api_key = _get_api_key()
        if not api_key:
            _LOGGER.debug(
                "interview_card_quality_judge: ANTHROPIC_API_KEY not set — returning UNKNOWN"
            )
            return GRADER_UNKNOWN_SENTINEL, []

        question: str = output.get("question") or output.get("query") or ""
        answer: str = output.get("answer") or output.get("response") or ""

        if not question or not answer:
            return GRADER_UNKNOWN_SENTINEL, []

        context: str | None = None
        raw_ctx = output.get("context") or output.get("retrieved_context")
        if isinstance(raw_ctx, str):
            context = raw_ctx
        elif isinstance(raw_ctx, (list, tuple)):
            context = "\n\n".join(str(c) for c in raw_ctx)

        try:
            return _call_anthropic(question, answer, context)
        except Exception as exc:  # guardian: allow-broad-exception-catch -- fail-soft: LLM judge must never crash the eval pipeline; exceptions are logged and treated as UNKNOWN
            _LOGGER.warning(
                "interview_card_quality_judge: LLM call failed, returning UNKNOWN: %s",
                exc,
            )
            return GRADER_UNKNOWN_SENTINEL, []


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return InterviewCardQualityJudge().grade(dim, run_context)


__all__ = [
    "InterviewCardQualityJudge",
    "grade",
    "IS_STUB",
    "IS_CALIBRATED",
    "GRADER_ID",
]
