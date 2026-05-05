"""apps_qna.engines.judges.context_precision_judge — deterministic RAG context-precision scorer.

Plan: ``.windsurf/plans/apps-qna-spine-deferred-e9c5b3.md`` D1.2

Scores retrieval signal-to-noise: what fraction of retrieved sources are
actually relevant (cited in the output answer).

Scoring model
-------------
Reads the following output keys (graceful fallback to empty on missing):

- ``output.retrieval_sources``    — list of all retrieved source IDs
- ``output.cited_sources``        — list of source IDs cited in the answer
- ``output.dim_scores.context_precision`` — pre-computed score (takes precedence)

When ``dim_scores.context_precision`` is present and numeric, returns it directly.
Otherwise computes: min(len(cited ∩ retrieved) / max(len(retrieved), 1), 1.0).
If ``cited_sources`` is absent, falls back to retrieval-count heuristic:
≤5 retrieved → 1.0 (tight retrieval implies high precision), >5 → 0.6.

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
GRADER_ID: str = "qna::context_precision_judge::v1"


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
    """Deterministic context-precision judge for apps_qna RAG evaluation."""

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        output = _get_output(run_context or {})

        pre = _precomputed_score(output)
        if pre is not None:
            return pre, [f"context_precision::v1::precomputed={pre:.2f}"]

        retrieved: list[str] = list(output.get("retrieval_sources") or [])
        cited: list[str] = list(output.get("cited_sources") or [])

        if not retrieved:
            return GRADER_UNKNOWN_SENTINEL, []

        score = _compute_precision(retrieved, cited)
        evidence_refs = [
            f"context_precision::v1::retrieved={len(retrieved)}",
            f"context_precision::v1::cited={len(cited)}",
            f"context_precision::v1::score={score:.2f}",
        ]
        return score, evidence_refs


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    """Module-level callable form of the judge interface."""
    return ContextPrecisionJudge().grade(dim, run_context)


__all__ = ["ContextPrecisionJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
