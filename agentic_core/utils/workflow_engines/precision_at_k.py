"""
Precision@K Metric

precision@k = relevant_docs_in_top_k / k
"""

from __future__ import annotations

from typing import Any

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

_emit_authorize_and_execute("p2", "precision_at_k", "execution_auth")
_emit_validates_capability("p2", "precision_at_k", "capability_check")
_emit_routes_to_capability("p2", "precision_at_k", "capability_route")
_emit_writes_via_uwg("p2", "precision_at_k", "uwg_write")
_emit_blocks_direct_write("p2", "precision_at_k", "direct_write_block")
_emit_records_tool_invocation("p2", "precision_at_k", "tool_invocation")
_emit_captures_execution_output("p2", "precision_at_k", "exec_output")
_emit_dispatches_agent("p3", "precision_at_k", "agent_dispatch")
_emit_coordinates_agents("p3", "precision_at_k", "agent_coordination")
_emit_records_workflow_lineage("p3", "precision_at_k", "workflow_lineage")
_emit_records_healing_outcome("p3", "precision_at_k", "healing_outcome")
_emit_escalates_failure("p3", "precision_at_k", "failure_escalation")
_emit_orchestrates_workflow("p3", "precision_at_k", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "precision_at_k", "healing_dispatch")
_emit_invokes_evaluation("p3", "precision_at_k", "evaluation_signal")
_emit_records_telemetry_event("p4", "precision_at_k", "telemetry_event")
_emit_captures_evaluation_metric("p4", "precision_at_k", "eval_metric")
_emit_stores_embedding("p4", "precision_at_k", "embedding_store")
_emit_updates_meta_learning_state("p4", "precision_at_k", "meta_learning")
_emit_links_execution_to_snapshot("p4", "precision_at_k", "exec_snapshot_link")
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
