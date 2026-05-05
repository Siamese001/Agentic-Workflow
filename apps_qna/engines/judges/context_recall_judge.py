"""apps_qna.engines.judges.context_recall_judge — deterministic RAG context-recall scorer.

Plan: ``.windsurf/plans/apps-qna-spine-deferred-e9c5b3.md`` D1.2

Scores retrieval completeness: what fraction of the needed evidence is
present in the retrieved context (``run_context["output"]["retrieval_sources"]``).

Scoring model
-------------
Reads the following output keys (graceful fallback to empty on missing):

- ``output.retrieval_sources`` — list/tuple of source IDs retrieved
- ``output.required_sources``  — list/tuple of expected source IDs (optional)
- ``output.dim_scores.context_recall`` — pre-computed score from producer (takes precedence)

When ``dim_scores.context_recall`` is present and numeric, returns it directly.
Otherwise computes: min(len(retrieved ∩ required) / max(len(required), 1), 1.0).
If ``required_sources`` is absent or empty, falls back to a length-adequacy
heuristic: ≥3 sources → 1.0, 2 → 0.7, 1 → 0.4, 0 → 0.0.

Integration contract
--------------------
    def grade(dim, run_context) -> tuple[float | int, list[str]]
"""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "qna::context_recall_judge::v1"


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
    """Deterministic context-recall judge for apps_qna RAG evaluation."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"context_recall::v1::precomputed={pre:.2f}"]

        retrieved: list[str] = list(output.get("retrieval_sources") or [])
        required: list[str] = list(output.get("required_sources") or [])

        if not retrieved:
            return GRADER_UNKNOWN_SENTINEL, []

        score = _compute_recall(retrieved, required)
        evidence_refs = [
            f"context_recall::v1::retrieved={len(retrieved)}",
            f"context_recall::v1::required={len(required)}",
            f"context_recall::v1::score={score:.2f}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return ContextRecallJudge().grade(dim, run_context)


__all__ = ["ContextRecallJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
