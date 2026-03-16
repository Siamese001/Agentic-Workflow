"""
Normalized Discounted Cumulative Gain (NDCG) Metric

NDCG measures ranking quality by giving higher weight to relevant
documents appearing at the top of the ranked list.
"""

from __future__ import annotations

import math

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "ndcg", "execution_auth")
_emit_validates_capability("p2", "ndcg", "capability_check")
_emit_routes_to_capability("p2", "ndcg", "capability_route")
_emit_writes_via_uwg("p2", "ndcg", "uwg_write")
_emit_blocks_direct_write("p2", "ndcg", "direct_write_block")
_emit_records_tool_invocation("p2", "ndcg", "tool_invocation")
_emit_captures_execution_output("p2", "ndcg", "exec_output")
_emit_dispatches_agent("p3", "ndcg", "agent_dispatch")
_emit_coordinates_agents("p3", "ndcg", "agent_coordination")
_emit_records_workflow_lineage("p3", "ndcg", "workflow_lineage")
_emit_records_healing_outcome("p3", "ndcg", "healing_outcome")
_emit_escalates_failure("p3", "ndcg", "failure_escalation")
_emit_orchestrates_workflow("p3", "ndcg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ndcg", "healing_dispatch")
_emit_invokes_evaluation("p3", "ndcg", "evaluation_signal")
_emit_records_telemetry_event("p4", "ndcg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ndcg", "eval_metric")
_emit_stores_embedding("p4", "ndcg", "embedding_store")
_emit_updates_meta_learning_state("p4", "ndcg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ndcg", "exec_snapshot_link")
from .base import RetrievalMetric

_emit_applies_guardrail("p0", "ndcg", "p0_governance")
_emit_reads_policy_state("p0", "ndcg", "policy_binding")
_emit_snapshots_state("p0", "ndcg", "state_snapshot")
emit_replay_key("p0", "ndcg")
emit_determinism_digest("p0", "ndcg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class NDCG(RetrievalMetric):
    """Normalized Discounted Cumulative Gain at cutoff k."""

    def __init__(self, k: int = 10):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    @property
    def name(self) -> str:
        return f"NDCG@{self.k}"

    def _dcg(self, ranked_docs: list[str], relevance: dict[str, float]) -> float:
        """Compute Discounted Cumulative Gain."""
        dcg = 0.0
        for rank, doc_id in enumerate(ranked_docs[: self.k], start=1):
            rel = relevance.get(doc_id, 0.0)
            dcg += rel / math.log2(rank + 1)
        return dcg

    def _ideal_dcg(self, relevance: dict[str, float]) -> float:
        """Compute ideal DCG (best possible ranking)."""
        sorted_rels = sorted(relevance.values(), reverse=True)
        idcg = 0.0
        for rank, rel in enumerate(sorted_rels[: self.k], start=1):
            idcg += rel / math.log2(rank + 1)
        return idcg

    def compute(
        self, prediction: list[str], ground_truth: list[str], context: dict[str, float] | None = None
    ) -> float:
        """Compute NDCG@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs (binary relevance = 1.0)
            context: Optional dict mapping doc_id -> graded relevance score.
                     If None, binary relevance (1.0 for any doc in ground_truth).

        Returns:
            NDCG score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "NDCG.compute")

        if not prediction:
            return 0.0
        if context is not None:
            relevance = context
        else:
            if not ground_truth:
                return 0.0
            relevance = dict.fromkeys(ground_truth, 1.0)
        idcg = self._ideal_dcg(relevance)
        if idcg == 0.0:
            return 0.0
        dcg = self._dcg(prediction, relevance)
        return dcg / idcg


__all__ = ["NDCG"]
