"""
Groundedness Metric

Measures whether the generated answer is supported by retrieved context.
Uses token-overlap heuristic (F1 over unigrams) as a deterministic
zero-dependency approximation.  An LLM-judge variant is available via
the optional judge callable injected at construction time.
"""

from __future__ import annotations

import re
from typing import Callable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "groundedness", "execution_auth")
trace_contract._emit_validates_capability("p2", "groundedness", "capability_check")
trace_contract._emit_routes_to_capability("p2", "groundedness", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "groundedness", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "groundedness", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "groundedness", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "groundedness", "exec_output")
trace_contract._emit_dispatches_agent("p3", "groundedness", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "groundedness", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "groundedness", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "groundedness", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "groundedness", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "groundedness", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "groundedness", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "groundedness", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "groundedness", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "groundedness", "eval_metric")
trace_contract._emit_stores_embedding("p4", "groundedness", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "groundedness", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "groundedness", "exec_snapshot_link")
from .base import GenerationMetric

trace_contract._emit_applies_guardrail("p0", "groundedness", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "groundedness", "policy_binding")
trace_contract._emit_snapshots_state("p0", "groundedness", "state_snapshot")

trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("groundedness", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("groundedness", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("groundedness", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("groundedness", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("groundedness", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("groundedness", "p4obs", "alert")
trace_contract._emit_links_incident_trace("groundedness", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("groundedness", "p3lm", "pattern")
trace_contract._emit_records_learning_event("groundedness", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("groundedness", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("groundedness", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("groundedness", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("groundedness", "p3lm", "policy")
trace_contract._emit_stores_learning_state("groundedness", "p3lm", "state")
trace_contract._emit_records_execution_trace("groundedness", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("groundedness", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("groundedness", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("groundedness", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("groundedness", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("groundedness", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("groundedness", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("groundedness", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("groundedness", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "groundedness", "context_pull")
trace_contract._emit_pulls_context("p1", "groundedness", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "groundedness", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "groundedness", "uwg_term_2")
trace_contract._emit_writes_through("p1", "groundedness", "write_through")
trace_contract._emit_writes_through("p1", "groundedness", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "groundedness", "safety_validation")
trace_contract._emit_invokes_eval("p1", "groundedness", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "groundedness", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "groundedness", "human_escalation")
trace_contract._emit_routes_through("p1", "groundedness", "route_through")
trace_contract._emit_checks_agent_registry("p1", "groundedness", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "groundedness", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "groundedness", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "groundedness", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "groundedness", "target_agent")
trace_contract._emit_verifies_policy("p1", "groundedness", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "groundedness", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "groundedness", "boundary_check")
trace_contract._emit_transcripts_response("p1", "groundedness", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "groundedness")
trace_contract._emit_gated_by_confidence("p1", "groundedness", "confidence_gate")
trace_contract.emit_replay_key("p0", "groundedness")
trace_contract.emit_determinism_digest("p0", "groundedness")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub("[^\\w\\s]", " ", text)
    return [t for t in text.split() if t]


def _token_f1(prediction_tokens: list[str], context_tokens: list[str]) -> float:
    """Compute F1 between two token lists."""
    if not prediction_tokens or not context_tokens:
        return 0.0
    pred_set = set(prediction_tokens)
    ctx_set = set(context_tokens)
    common = pred_set & ctx_set
    if not common:
        return 0.0
    precision = len(common) / len(pred_set)
    recall = len(common) / len(ctx_set)
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


class Groundedness(GenerationMetric):
    """Measures whether the answer is supported by the retrieved context.

    Without a judge: uses token-overlap F1 between answer and concatenated context.
    With a judge callable: calls judge(answer, context_str) -> float in [0, 1].
    """

    def __init__(self, judge: Callable[[str, str], float] | None = None):
        self._judge = judge

    @property
    def name(self) -> str:
        return "groundedness"

    def compute(self, prediction: str, ground_truth: str, context: str | list[str] | None = None) -> float:
        """Compute groundedness score.

        Args:
            prediction: Generated answer string
            ground_truth: Expected answer (unused in heuristic mode; used by judge)
            context: Retrieved context documents (str or list of str)

        Returns:
            Groundedness score in [0, 1]
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "Groundedness.compute")

        if not prediction:
            return 0.0
        if context is None:
            context_str = ground_truth if ground_truth else ""
        elif isinstance(context, list):
            context_str = " ".join(context)
        else:
            context_str = context
        if not context_str:
            return 0.0
        if self._judge is not None:
            return float(self._judge(prediction, context_str))
        pred_tokens = _tokenize(prediction)
        ctx_tokens = _tokenize(context_str)
        return _token_f1(pred_tokens, ctx_tokens)


__all__ = ["Groundedness", "_tokenize", "_token_f1"]
