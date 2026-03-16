"""
Mean Reciprocal Rank (MRR) Metric

MRR = 1 / rank_of_first_relevant_doc
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .base import RetrievalMetric

_emit_applies_guardrail("p0", "mrr", "p0_governance")
_emit_reads_policy_state("p0", "mrr", "policy_binding")
_emit_snapshots_state("p0", "mrr", "state_snapshot")
emit_replay_key("p0", "mrr")
emit_determinism_digest("p0", "mrr")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class MeanReciprocalRank(RetrievalMetric):
    """MRR measures the rank position of the first relevant document."""

    @property
    def name(self) -> str:
        return "MRR"

    def compute(self, prediction: list[str], ground_truth: list[str], context: Any = None) -> float:
        """Compute MRR for a single query.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Reciprocal rank of first relevant doc, 0.0 if none found
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MeanReciprocalRank.compute")

        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0
        relevant_set = set(ground_truth)
        for rank, doc_id in enumerate(prediction, start=1):
            if doc_id in relevant_set:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def mean(scores: list[float]) -> float:
        """Compute mean MRR across multiple queries.

        Args:
            scores: Per-query MRR scores

        Returns:
            Mean reciprocal rank
        """
        if not scores:
            return 0.0
        return sum(scores) / len(scores)


__all__ = ["MeanReciprocalRank"]
