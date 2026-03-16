"""
Precision@K Metric

precision@k = relevant_docs_in_top_k / k
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

_emit_applies_guardrail("p0", "precision_at_k", "p0_governance")
_emit_reads_policy_state("p0", "precision_at_k", "policy_binding")
_emit_snapshots_state("p0", "precision_at_k", "state_snapshot")
emit_replay_key("p0", "precision_at_k")
emit_determinism_digest("p0", "precision_at_k")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class PrecisionAtK(RetrievalMetric):
    """Measures what fraction of the top-k retrieved documents are relevant."""

    def __init__(self, k: int = 5):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    @property
    def name(self) -> str:
        return f"precision@{self.k}"

    def compute(self, prediction: list[str], ground_truth: list[str], context: Any = None) -> float:
        """Compute precision@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Fraction of top-k retrieved docs that are relevant, in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PrecisionAtK.compute")

        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0
        relevant_set = set(ground_truth)
        top_k = prediction[: self.k]
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_set)
        return relevant_in_top_k / self.k


__all__ = ["PrecisionAtK"]
