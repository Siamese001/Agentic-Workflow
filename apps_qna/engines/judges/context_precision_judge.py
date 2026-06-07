"""apps_qna.engines.judges.context_precision_judge — RAG context-precision scorer.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-qna-deferred-e5-f7a2b1.md`` E2.2

Scores retrieval signal-to-noise: what fraction of retrieved sources are
actually relevant to answering the question.

Scoring model (dual-path)
-------------------------
**LLM path** (preferred): When ``run_context["provider_context"]`` is present
and has a configured model, dispatches an LLM judge prompt.

**Heuristic fallback**: Deterministic overlap or count-based heuristic.

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
GRADER_ID: str = "qna::context_precision_judge::v2"

_SCORE_RE = re.compile(r"\b([01]\.\d{1,2})\b|\b(1\.0|0\.0)\b")

_PRECISION_PROMPT_TEMPLATE = """You are a RAG evaluation judge. Score context precision on a scale of 0.0 to 1.0.

Context precision measures: what fraction of the retrieved sources are actually relevant to answering the question (signal-to-noise ratio).

**Question**: {question}

**Retrieved sources**: {retrieved}

**Answer produced**: {answer}

Score 1.0 = all retrieved sources are relevant (no noise).
Score 0.0 = none of the retrieved sources are relevant.

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


def _get_output(run_context: Mapping[str, Any]) -> Mapping[str, Any]:
    out = run_context.get("output") if isinstance(run_context, Mapping) else None
    return out if isinstance(out, Mapping) else {}


def _precomputed_score(output: Mapping[str, Any]) -> float | None:
    dim_scores = output.get("dim_scores")
    if not isinstance(dim_scores, Mapping):
        return None
    val = dim_scores.get("context_precision")
    if isinstance(val, (int, float)) and 0.0 <= float(val) <= 1.0:
        return float(val)
    return None


def _compute_precision(
    retrieved: list[str],
    cited: list[str],
) -> float:
    if not retrieved:
        return 0.0
    if cited:
        relevant = len(set(cited) & set(retrieved))
        return min(1.0, relevant / max(1, len(retrieved)))
    return 1.0 if len(retrieved) <= 5 else 0.6


class ContextPrecisionJudge:
    """LLM-backed context-precision judge with heuristic fallback."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"context_precision::v2::precomputed={pre:.2f}"]

        retrieved: list[str] = list(output.get("retrieval_sources") or [])
        cited: list[str] = list(output.get("cited_sources") or [])

        if not retrieved:
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
                question = output.get("question") or output.get("query") or ""
                answer = output.get("answer") or output.get("response") or ""
                prompt = _PRECISION_PROMPT_TEMPLATE.format(
                    question=question,
                    retrieved=json.dumps(retrieved[:20]),
                    answer=answer[:500] if answer else "(not provided)",
                )
                response = provider_ctx.dispatch(prompt)
                llm_score = _parse_llm_score(response)
                if llm_score is not None:
                    return llm_score, [
                        f"context_precision::v2::llm_judge={llm_score:.2f}",
                        f"context_precision::v2::retrieved={len(retrieved)}",
                    ]

        # Heuristic fallback
        score = _compute_precision(retrieved, cited)
        evidence_refs = [
            f"context_precision::v2::heuristic={score:.2f}",
            f"context_precision::v2::retrieved={len(retrieved)}",
            f"context_precision::v2::cited={len(cited)}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return ContextPrecisionJudge().grade(dim, run_context)


__all__ = ["ContextPrecisionJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
