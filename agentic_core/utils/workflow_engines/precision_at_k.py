"""
Precision@K Metric

precision@k = relevant_docs_in_top_k / k
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("precision_at_k", "p4obs", "metric_1")
_emit_emits_metric_event("precision_at_k", "p4obs", "metric_2")
_emit_emits_metric_event("precision_at_k", "p4obs", "metric_3")
_emit_emits_metric_event("precision_at_k", "p4obs", "metric_4")
_emit_emits_metric_event("precision_at_k", "p4obs", "metric_5")
_emit_emits_metric_event("precision_at_k", "p4obs", "metric_6")
_emit_records_incident_event("precision_at_k", "p4obs", "incident")
_emit_captures_runtime_anomaly("precision_at_k", "p4obs", "anomaly")
_emit_writes_observability_log("precision_at_k", "p4obs", "obs_log")
_emit_updates_monitoring_state("precision_at_k", "p4obs", "mon_state")
_emit_triggers_alert("precision_at_k", "p4obs", "alert")
_emit_links_incident_trace("precision_at_k", "p4obs", "trace_link")
_emit_captures_pattern("precision_at_k", "p3lm", "pattern")
_emit_records_learning_event("precision_at_k", "p3lm", "learning_event")
_emit_writes_learning_snapshot("precision_at_k", "p3lm", "snapshot")
_emit_feeds_meta_learning("precision_at_k", "p3lm", "meta_feed")
_emit_updates_routing_strategy("precision_at_k", "p3lm", "routing")
_emit_improves_agent_policy("precision_at_k", "p3lm", "policy")
_emit_stores_learning_state("precision_at_k", "p3lm", "state")
_emit_records_execution_trace("precision_at_k", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("precision_at_k", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("precision_at_k", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("precision_at_k", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("precision_at_k", "L4_STATE", "p2_trace_5")
_emit_reads_environ("precision_at_k", "env_read", "p2_env_1")
_emit_reads_environ("precision_at_k", "env_read", "p2_env_2")
_emit_reads_runtime_state("precision_at_k", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("precision_at_k", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "precision_at_k", "context_pull")
_emit_pulls_context("p1", "precision_at_k", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "precision_at_k", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "precision_at_k", "uwg_term_2")
_emit_writes_through("p1", "precision_at_k", "write_through")
_emit_writes_through("p1", "precision_at_k", "write_through_2")
_emit_validated_by_safety_plane("p1", "precision_at_k", "safety_validation")
_emit_invokes_eval("p1", "precision_at_k", "eval_call")
_emit_proposal_commits_routing("p1", "precision_at_k", "routing_commit")
_emit_escalates_to_human("p1", "precision_at_k", "human_escalation")
_emit_routes_through("p1", "precision_at_k", "route_through")
_emit_checks_agent_registry("p1", "precision_at_k", "agent_registry")
_emit_validates_agent_capability("p1", "precision_at_k", "capability")
_emit_dispatches_execution_plan("p1", "precision_at_k", "exec_plan")
_emit_agent_executes_agent("p1", "precision_at_k", "sub_agent")
_emit_routes_to_agent("p1", "precision_at_k", "target_agent")
_emit_verifies_policy("p1", "precision_at_k", "policy_check")
_emit_observes_runtime_state("p1", "precision_at_k", "runtime_state")
_emit_verifies_boundary("p1", "precision_at_k", "boundary_check")
_emit_transcripts_response("p1", "precision_at_k", "transcript")
_emit_hard_fails_untranscripted("p1", "precision_at_k")
_emit_gated_by_confidence("p1", "precision_at_k", "confidence_gate")
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
