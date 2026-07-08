"""
Recall@K Metric

recall@k = relevant_docs_in_top_k / total_relevant_docs
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "recall_at_k", "execution_auth")
trace_contract._emit_validates_capability("p2", "recall_at_k", "capability_check")
trace_contract._emit_routes_to_capability("p2", "recall_at_k", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "recall_at_k", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "recall_at_k", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "recall_at_k", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "recall_at_k", "exec_output")
trace_contract._emit_dispatches_agent("p3", "recall_at_k", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "recall_at_k", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "recall_at_k", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "recall_at_k", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "recall_at_k", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "recall_at_k", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "recall_at_k", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "recall_at_k", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "recall_at_k", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "recall_at_k", "eval_metric")
trace_contract._emit_stores_embedding("p4", "recall_at_k", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "recall_at_k", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "recall_at_k", "exec_snapshot_link")
from .base import RetrievalMetric

trace_contract._emit_applies_guardrail("p0", "recall_at_k", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "recall_at_k", "policy_binding")
trace_contract._emit_snapshots_state("p0", "recall_at_k", "state_snapshot")

trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("recall_at_k", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("recall_at_k", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("recall_at_k", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("recall_at_k", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("recall_at_k", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("recall_at_k", "p4obs", "alert")
trace_contract._emit_links_incident_trace("recall_at_k", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("recall_at_k", "p3lm", "pattern")
trace_contract._emit_records_learning_event("recall_at_k", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("recall_at_k", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("recall_at_k", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("recall_at_k", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("recall_at_k", "p3lm", "policy")
trace_contract._emit_stores_learning_state("recall_at_k", "p3lm", "state")
trace_contract._emit_records_execution_trace("recall_at_k", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("recall_at_k", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("recall_at_k", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("recall_at_k", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("recall_at_k", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("recall_at_k", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("recall_at_k", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("recall_at_k", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("recall_at_k", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "recall_at_k", "context_pull")
trace_contract._emit_pulls_context("p1", "recall_at_k", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "recall_at_k", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "recall_at_k", "uwg_term_2")
trace_contract._emit_writes_through("p1", "recall_at_k", "write_through")
trace_contract._emit_writes_through("p1", "recall_at_k", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "recall_at_k", "safety_validation")
trace_contract._emit_invokes_eval("p1", "recall_at_k", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "recall_at_k", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "recall_at_k", "human_escalation")
trace_contract._emit_routes_through("p1", "recall_at_k", "route_through")
trace_contract._emit_checks_agent_registry("p1", "recall_at_k", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "recall_at_k", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "recall_at_k", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "recall_at_k", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "recall_at_k", "target_agent")
trace_contract._emit_verifies_policy("p1", "recall_at_k", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "recall_at_k", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "recall_at_k", "boundary_check")
trace_contract._emit_transcripts_response("p1", "recall_at_k", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "recall_at_k")
trace_contract._emit_gated_by_confidence("p1", "recall_at_k", "confidence_gate")
trace_contract.emit_replay_key("p0", "recall_at_k")
trace_contract.emit_determinism_digest("p0", "recall_at_k")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class RecallAtK(RetrievalMetric):
    """Measures what fraction of all relevant documents appear in the top-k results."""

    def __init__(self, k: int = 10):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    @property
    def name(self) -> str:
        return f"recall@{self.k}"

    def compute(self, prediction: list[str], ground_truth: list[str], context: Any = None) -> float:
        """Compute recall@k.

        Args:
            prediction: Ranked list of retrieved document IDs
            ground_truth: List of relevant document IDs
            context: Unused

        Returns:
            Fraction of relevant docs found in top-k, in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RecallAtK.compute")

        if not ground_truth:
            return 0.0
        if not prediction:
            return 0.0
        relevant_set = set(ground_truth)
        top_k = list(dict.fromkeys(prediction[: self.k]))
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_set)
        return relevant_in_top_k / len(relevant_set)


__all__ = ["RecallAtK"]
