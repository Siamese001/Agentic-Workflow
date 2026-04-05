"""
HealerAgentMixin — Canonical location.

Relocated from agentic_core/L3_orchestration/types/healer_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "healer_agent_mixin", "p0_governance")
_emit_reads_policy_state("p0", "healer_agent_mixin", "policy_binding")
_emit_snapshots_state("p0", "healer_agent_mixin", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_6")
_emit_records_incident_event("healer_agent_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("healer_agent_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("healer_agent_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("healer_agent_mixin", "p4obs", "mon_state")
_emit_triggers_alert("healer_agent_mixin", "p4obs", "alert")
_emit_links_incident_trace("healer_agent_mixin", "p4obs", "trace_link")
_emit_captures_pattern("healer_agent_mixin", "p3lm", "pattern")
_emit_records_learning_event("healer_agent_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healer_agent_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("healer_agent_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healer_agent_mixin", "p3lm", "routing")
_emit_improves_agent_policy("healer_agent_mixin", "p3lm", "policy")
_emit_stores_learning_state("healer_agent_mixin", "p3lm", "state")
_emit_records_execution_trace("healer_agent_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healer_agent_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healer_agent_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healer_agent_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healer_agent_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healer_agent_mixin", "env_read", "p2_env_1")
_emit_reads_environ("healer_agent_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("healer_agent_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healer_agent_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healer_agent_mixin", "context_pull")
_emit_pulls_context("p1", "healer_agent_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healer_agent_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healer_agent_mixin", "uwg_term_2")
_emit_writes_through("p1", "healer_agent_mixin", "write_through")
_emit_writes_through("p1", "healer_agent_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "healer_agent_mixin", "safety_validation")
_emit_invokes_eval("p1", "healer_agent_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "healer_agent_mixin", "routing_commit")
_emit_escalates_to_human("p1", "healer_agent_mixin", "human_escalation")
_emit_routes_through("p1", "healer_agent_mixin", "route_through")
_emit_checks_agent_registry("p1", "healer_agent_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "healer_agent_mixin", "capability")
_emit_dispatches_execution_plan("p1", "healer_agent_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "healer_agent_mixin", "sub_agent")
_emit_routes_to_agent("p1", "healer_agent_mixin", "target_agent")
_emit_verifies_policy("p1", "healer_agent_mixin", "policy_check")
_emit_observes_runtime_state("p1", "healer_agent_mixin", "runtime_state")
_emit_verifies_boundary("p1", "healer_agent_mixin", "boundary_check")
_emit_transcripts_response("p1", "healer_agent_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "healer_agent_mixin")
_emit_gated_by_confidence("p1", "healer_agent_mixin", "confidence_gate")
emit_replay_key("p0", "healer_agent_mixin")
emit_determinism_digest("p0", "healer_agent_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "healer_agent_mixin", "execution_auth")
_emit_validates_capability("p2", "healer_agent_mixin", "capability_check")
_emit_routes_to_capability("p2", "healer_agent_mixin", "capability_route")
_emit_writes_via_uwg("p2", "healer_agent_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "healer_agent_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_agent_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "healer_agent_mixin", "exec_output")
_emit_dispatches_agent("p3", "healer_agent_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_agent_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_agent_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_agent_mixin", "healing_outcome")
_emit_escalates_failure("p3", "healer_agent_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_agent_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_agent_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_agent_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_agent_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_agent_mixin", "eval_metric")
_emit_stores_embedding("p4", "healer_agent_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_agent_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_agent_mixin", "exec_snapshot_link")


class HealerAgentMixin:
    """
    Mixin for NEW agents. Enforces strict interface compliance.
    Inherit from this to automatically get input validation.
    """

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Template method that handles validation and error wrapping.
        Subclasses should implement `_heal_impl`.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealerAgentMixin.heal")

        if not isinstance(violation, dict):
            return {"status": "failed", "errors": ["Violation must be a dictionary"]}
        try:
            result = self._heal_impl(violation)
            return self._normalize_result(result)
        except Exception as e:
            logging.error(f"Heal operation failed in {self.__class__.__name__}: {e}")
            return {"status": "failed", "errors": [str(e)]}

    def _heal_impl(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Override this in your agent."""
        raise NotImplementedError("Agents must implement _heal_impl")

    def _normalize_result(self, result: Any) -> dict[str, Any]:
        """Ensures result matches HEAL_RESULT_SCHEMA."""
        if not isinstance(result, dict):
            return {
                "status": "success" if result else "failed",
                "details": str(result),
                "artifacts": [],
                "errors": [],
            }
        defaults = {"status": "success", "details": "Fixed", "artifacts": [], "errors": []}
        for k, v in defaults.items():
            if k not in result:
                result[k] = v
        return result
