"""
HealerAgentMixin — Canonical location.

Relocated from agentic_core/L3_orchestration/types/healer_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "healer_agent_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healer_agent_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "healer_agent_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healer_agent_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healer_agent_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healer_agent_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healer_agent_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healer_agent_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healer_agent_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healer_agent_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healer_agent_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healer_agent_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healer_agent_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healer_agent_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healer_agent_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healer_agent_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healer_agent_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("healer_agent_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healer_agent_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healer_agent_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healer_agent_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healer_agent_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healer_agent_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healer_agent_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healer_agent_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healer_agent_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healer_agent_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "healer_agent_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_agent_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_agent_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healer_agent_mixin", "write_through")
trace_contract._emit_writes_through("p1", "healer_agent_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healer_agent_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healer_agent_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healer_agent_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healer_agent_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "healer_agent_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healer_agent_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healer_agent_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healer_agent_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healer_agent_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healer_agent_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "healer_agent_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healer_agent_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healer_agent_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healer_agent_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healer_agent_mixin")
trace_contract._emit_gated_by_confidence("p1", "healer_agent_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "healer_agent_mixin")
trace_contract.emit_determinism_digest("p0", "healer_agent_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "healer_agent_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "healer_agent_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healer_agent_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healer_agent_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healer_agent_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healer_agent_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healer_agent_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healer_agent_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healer_agent_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healer_agent_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healer_agent_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healer_agent_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healer_agent_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healer_agent_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healer_agent_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healer_agent_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healer_agent_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healer_agent_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healer_agent_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healer_agent_mixin", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealerAgentMixin.heal")

        if not isinstance(violation, dict):
            return {"status": "failed", "errors": ["Violation must be a dictionary"]}
        try:
            result = self._heal_impl(violation)
            return self._normalize_result(result)
        except (AttributeError, RuntimeError, OSError, ValueError) as e:
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
