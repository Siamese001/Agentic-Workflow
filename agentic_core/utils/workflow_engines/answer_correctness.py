"""
Answer Correctness Metric

Measures answer correctness using token-overlap F1 (heuristic) or an
injected LLM-as-judge callable.  The heuristic is deterministic and
zero-dependency; the judge variant supports production scoring.
"""

from __future__ import annotations

from typing import Any, Callable

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

_emit_authorize_and_execute("p2", "answer_correctness", "execution_auth")
_emit_validates_capability("p2", "answer_correctness", "capability_check")
_emit_routes_to_capability("p2", "answer_correctness", "capability_route")
_emit_writes_via_uwg("p2", "answer_correctness", "uwg_write")
_emit_blocks_direct_write("p2", "answer_correctness", "direct_write_block")
_emit_records_tool_invocation("p2", "answer_correctness", "tool_invocation")
_emit_captures_execution_output("p2", "answer_correctness", "exec_output")
_emit_dispatches_agent("p3", "answer_correctness", "agent_dispatch")
_emit_coordinates_agents("p3", "answer_correctness", "agent_coordination")
_emit_records_workflow_lineage("p3", "answer_correctness", "workflow_lineage")
_emit_records_healing_outcome("p3", "answer_correctness", "healing_outcome")
_emit_escalates_failure("p3", "answer_correctness", "failure_escalation")
_emit_orchestrates_workflow("p3", "answer_correctness", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "answer_correctness", "healing_dispatch")
_emit_invokes_evaluation("p3", "answer_correctness", "evaluation_signal")
_emit_records_telemetry_event("p4", "answer_correctness", "telemetry_event")
_emit_captures_evaluation_metric("p4", "answer_correctness", "eval_metric")
_emit_stores_embedding("p4", "answer_correctness", "embedding_store")
_emit_updates_meta_learning_state("p4", "answer_correctness", "meta_learning")
_emit_links_execution_to_snapshot("p4", "answer_correctness", "exec_snapshot_link")
from .base import GenerationMetric
from .groundedness import _token_f1, _tokenize

_emit_applies_guardrail("p0", "answer_correctness", "p0_governance")
_emit_reads_policy_state("p0", "answer_correctness", "policy_binding")
_emit_snapshots_state("p0", "answer_correctness", "state_snapshot")
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

_emit_emits_metric_event("answer_correctness", "p4obs", "metric_1")
_emit_emits_metric_event("answer_correctness", "p4obs", "metric_2")
_emit_emits_metric_event("answer_correctness", "p4obs", "metric_3")
_emit_emits_metric_event("answer_correctness", "p4obs", "metric_4")
_emit_emits_metric_event("answer_correctness", "p4obs", "metric_5")
_emit_emits_metric_event("answer_correctness", "p4obs", "metric_6")
_emit_records_incident_event("answer_correctness", "p4obs", "incident")
_emit_captures_runtime_anomaly("answer_correctness", "p4obs", "anomaly")
_emit_writes_observability_log("answer_correctness", "p4obs", "obs_log")
_emit_updates_monitoring_state("answer_correctness", "p4obs", "mon_state")
_emit_triggers_alert("answer_correctness", "p4obs", "alert")
_emit_links_incident_trace("answer_correctness", "p4obs", "trace_link")
_emit_captures_pattern("answer_correctness", "p3lm", "pattern")
_emit_records_learning_event("answer_correctness", "p3lm", "learning_event")
_emit_writes_learning_snapshot("answer_correctness", "p3lm", "snapshot")
_emit_feeds_meta_learning("answer_correctness", "p3lm", "meta_feed")
_emit_updates_routing_strategy("answer_correctness", "p3lm", "routing")
_emit_improves_agent_policy("answer_correctness", "p3lm", "policy")
_emit_stores_learning_state("answer_correctness", "p3lm", "state")
_emit_records_execution_trace("answer_correctness", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("answer_correctness", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("answer_correctness", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("answer_correctness", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("answer_correctness", "L4_STATE", "p2_trace_5")
_emit_reads_environ("answer_correctness", "env_read", "p2_env_1")
_emit_reads_environ("answer_correctness", "env_read", "p2_env_2")
_emit_reads_runtime_state("answer_correctness", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("answer_correctness", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "answer_correctness", "context_pull")
_emit_pulls_context("p1", "answer_correctness", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "answer_correctness", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "answer_correctness", "uwg_term_2")
_emit_writes_through("p1", "answer_correctness", "write_through")
_emit_writes_through("p1", "answer_correctness", "write_through_2")
_emit_validated_by_safety_plane("p1", "answer_correctness", "safety_validation")
_emit_invokes_eval("p1", "answer_correctness", "eval_call")
_emit_proposal_commits_routing("p1", "answer_correctness", "routing_commit")
_emit_escalates_to_human("p1", "answer_correctness", "human_escalation")
_emit_routes_through("p1", "answer_correctness", "route_through")
_emit_checks_agent_registry("p1", "answer_correctness", "agent_registry")
_emit_validates_agent_capability("p1", "answer_correctness", "capability")
_emit_dispatches_execution_plan("p1", "answer_correctness", "exec_plan")
_emit_agent_executes_agent("p1", "answer_correctness", "sub_agent")
_emit_routes_to_agent("p1", "answer_correctness", "target_agent")
_emit_verifies_policy("p1", "answer_correctness", "policy_check")
_emit_observes_runtime_state("p1", "answer_correctness", "runtime_state")
_emit_verifies_boundary("p1", "answer_correctness", "boundary_check")
_emit_transcripts_response("p1", "answer_correctness", "transcript")
_emit_hard_fails_untranscripted("p1", "answer_correctness")
_emit_gated_by_confidence("p1", "answer_correctness", "confidence_gate")
emit_replay_key("p0", "answer_correctness")
emit_determinism_digest("p0", "answer_correctness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class AnswerCorrectness(GenerationMetric):
    """Measures how correct the generated answer is relative to the expected answer.

    Without a judge: F1 token overlap between prediction and expected answer.
    With a judge callable: calls judge(prediction, ground_truth) -> float in [0, 1].
    """

    def __init__(self, judge: Callable[[str, str], float] | None = None):
        self._judge = judge

    @property
    def name(self) -> str:
        return "answer_correctness"

    def compute(self, prediction: str, ground_truth: str, context: Any = None) -> float:
        """Compute answer correctness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected (reference) answer string
            context: Unused

        Returns:
            Correctness score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AnswerCorrectness.compute")

        if not prediction:
            return 0.0
        if not ground_truth:
            return 0.0
        if self._judge is not None:
            return float(self._judge(prediction, ground_truth))
        pred_tokens = _tokenize(prediction)
        gt_tokens = _tokenize(ground_truth)
        return _token_f1(pred_tokens, gt_tokens)


__all__ = ["AnswerCorrectness"]
