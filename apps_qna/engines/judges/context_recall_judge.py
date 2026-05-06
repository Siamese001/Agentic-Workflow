"""apps_qna.engines.judges.context_recall_judge — RAG context-recall scorer.

Plan: ``.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md`` E2.1

Scores retrieval completeness: what fraction of the needed evidence is
present in the retrieved context (``run_context["output"]["retrieval_sources"]``).

Scoring model (dual-path)
-------------------------
**LLM path** (preferred): When ``run_context["provider_context"]`` is present
and has a configured model, dispatches an LLM judge prompt asking the model
to evaluate context recall on a 0.0–1.0 scale. Parses score from response.

**Heuristic fallback**: When no provider is available, uses the deterministic
heuristic: overlap ratio or length-adequacy fallback.

Reads the following output keys (graceful fallback to empty on missing):

- ``output.retrieval_sources`` — list/tuple of source IDs retrieved
- ``output.required_sources``  — list/tuple of expected source IDs (optional)
- ``output.question``          — the interview question text
- ``output.dim_scores.context_recall`` — pre-computed score from producer (takes precedence)

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
GRADER_ID: str = "qna::context_recall_judge::v2"

_SCORE_RE = re.compile(r"\b([01]\.\d{1,2})\b|\b(1\.0|0\.0)\b")

_RECALL_PROMPT_TEMPLATE = """You are a RAG evaluation judge. Score context recall on a scale of 0.0 to 1.0.

Context recall measures: what fraction of the information needed to answer the question is present in the retrieved sources.

**Question**: {question}

**Retrieved sources**: {retrieved}

**Required sources** (if known): {required}

Score 1.0 = all needed evidence is present.
Score 0.0 = none of the needed evidence is present.

Respond with ONLY a JSON object: {{"score": <float 0.0-1.0>, "rationale": "<brief reason>"}}
"""


def _parse_llm_score(response: str) -> float | None:
    """Parse a 0.0-1.0 score from LLM response (JSON or bare float)."""
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
    val = dim_scores.get("context_recall")
    if isinstance(val, (int, float)) and 0.0 <= float(val) <= 1.0:
        return float(val)
    return None


def _compute_recall(
    retrieved: list[str],
    required: list[str],
) -> float:
    if required:
        overlap = len(set(retrieved) & set(required))
        return min(1.0, overlap / max(1, len(required)))
    n = len(retrieved)
    if n >= 3:
        return 1.0
    if n == 2:
        return 0.7
    if n == 1:
        return 0.4
    return 0.0


class ContextRecallJudge:
    """LLM-backed context-recall judge with heuristic fallback."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"context_recall::v2::precomputed={pre:.2f}"]

        retrieved: list[str] = list(output.get("retrieval_sources") or [])
        required: list[str] = list(output.get("required_sources") or [])

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
                prompt = _RECALL_PROMPT_TEMPLATE.format(
                    question=question,
                    retrieved=json.dumps(retrieved[:20]),
                    required=json.dumps(required[:20]) if required else "(not provided)",
                )
                response = provider_ctx.dispatch(prompt)
                llm_score = _parse_llm_score(response)
                if llm_score is not None:
                    return llm_score, [
                        f"context_recall::v2::llm_judge={llm_score:.2f}",
                        f"context_recall::v2::retrieved={len(retrieved)}",
                    ]

        # Heuristic fallback
        score = _compute_recall(retrieved, required)
        evidence_refs = [
            f"context_recall::v2::heuristic={score:.2f}",
            f"context_recall::v2::retrieved={len(retrieved)}",
            f"context_recall::v2::required={len(required)}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return ContextRecallJudge().grade(dim, run_context)


__all__ = ["ContextRecallJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
