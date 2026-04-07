"""
Normalized Discounted Cumulative Gain (NDCG) Metric

NDCG measures ranking quality by giving higher weight to relevant
documents appearing at the top of the ranked list.
"""

from __future__ import annotations

import math

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("ndcg", "p4obs", "metric_1")
_emit_emits_metric_event("ndcg", "p4obs", "metric_2")
_emit_emits_metric_event("ndcg", "p4obs", "metric_3")
_emit_emits_metric_event("ndcg", "p4obs", "metric_4")
_emit_emits_metric_event("ndcg", "p4obs", "metric_5")
_emit_emits_metric_event("ndcg", "p4obs", "metric_6")
_emit_records_incident_event("ndcg", "p4obs", "incident")
_emit_captures_runtime_anomaly("ndcg", "p4obs", "anomaly")
_emit_writes_observability_log("ndcg", "p4obs", "obs_log")
_emit_updates_monitoring_state("ndcg", "p4obs", "mon_state")
_emit_triggers_alert("ndcg", "p4obs", "alert")
_emit_links_incident_trace("ndcg", "p4obs", "trace_link")
_emit_captures_pattern("ndcg", "p3lm", "pattern")
_emit_records_learning_event("ndcg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ndcg", "p3lm", "snapshot")
_emit_feeds_meta_learning("ndcg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ndcg", "p3lm", "routing")
_emit_improves_agent_policy("ndcg", "p3lm", "policy")
_emit_stores_learning_state("ndcg", "p3lm", "state")
_emit_records_execution_trace("ndcg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ndcg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ndcg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ndcg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ndcg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ndcg", "env_read", "p2_env_1")
_emit_reads_environ("ndcg", "env_read", "p2_env_2")
_emit_reads_runtime_state("ndcg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ndcg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ndcg", "context_pull")
_emit_pulls_context("p1", "ndcg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ndcg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ndcg", "uwg_term_2")
_emit_writes_through("p1", "ndcg", "write_through")
_emit_writes_through("p1", "ndcg", "write_through_2")
_emit_validated_by_safety_plane("p1", "ndcg", "safety_validation")
_emit_invokes_eval("p1", "ndcg", "eval_call")
_emit_proposal_commits_routing("p1", "ndcg", "routing_commit")
_emit_escalates_to_human("p1", "ndcg", "human_escalation")
_emit_routes_through("p1", "ndcg", "route_through")
_emit_checks_agent_registry("p1", "ndcg", "agent_registry")
_emit_validates_agent_capability("p1", "ndcg", "capability")
_emit_dispatches_execution_plan("p1", "ndcg", "exec_plan")
_emit_agent_executes_agent("p1", "ndcg", "sub_agent")
_emit_routes_to_agent("p1", "ndcg", "target_agent")
_emit_verifies_policy("p1", "ndcg", "policy_check")
_emit_observes_runtime_state("p1", "ndcg", "runtime_state")
_emit_verifies_boundary("p1", "ndcg", "boundary_check")
_emit_transcripts_response("p1", "ndcg", "transcript")
_emit_hard_fails_untranscripted("p1", "ndcg")
_emit_gated_by_confidence("p1", "ndcg", "confidence_gate")
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
        self, prediction: list[str], ground_truth: list[str], context: dict[str, float] | None = None,
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
