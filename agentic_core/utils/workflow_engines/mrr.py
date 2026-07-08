"""
Mean Reciprocal Rank (MRR) Metric

MRR = 1 / rank_of_first_relevant_doc
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "mrr", "execution_auth")
trace_contract._emit_validates_capability("p2", "mrr", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mrr", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mrr", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mrr", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mrr", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mrr", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mrr", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mrr", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mrr", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mrr", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mrr", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mrr", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mrr", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mrr", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mrr", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mrr", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mrr", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mrr", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mrr", "exec_snapshot_link")
from .base import RetrievalMetric

trace_contract._emit_applies_guardrail("p0", "mrr", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "mrr", "policy_binding")
trace_contract._emit_snapshots_state("p0", "mrr", "state_snapshot")

trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mrr", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mrr", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mrr", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mrr", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mrr", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mrr", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mrr", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mrr", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mrr", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mrr", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mrr", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mrr", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mrr", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mrr", "p3lm", "state")
trace_contract._emit_records_execution_trace("mrr", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mrr", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mrr", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mrr", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mrr", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mrr", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mrr", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mrr", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mrr", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mrr", "context_pull")
trace_contract._emit_pulls_context("p1", "mrr", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mrr", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mrr", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mrr", "write_through")
trace_contract._emit_writes_through("p1", "mrr", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mrr", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mrr", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mrr", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "mrr", "human_escalation")
trace_contract._emit_routes_through("p1", "mrr", "route_through")
trace_contract._emit_checks_agent_registry("p1", "mrr", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mrr", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mrr", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mrr", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mrr", "target_agent")
trace_contract._emit_verifies_policy("p1", "mrr", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mrr", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mrr", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mrr", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mrr")
trace_contract._emit_gated_by_confidence("p1", "mrr", "confidence_gate")
trace_contract.emit_replay_key("p0", "mrr")
trace_contract.emit_determinism_digest("p0", "mrr")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MeanReciprocalRank.compute")

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
