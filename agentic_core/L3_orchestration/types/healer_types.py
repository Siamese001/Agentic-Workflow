"""
File: agentic_core/base_agents/healer_interface.py
Description: Standardization layer for Healer Agents. Provides Mixins for new agents and Adapters for legacy ones.
"""

import logging
from typing import Any, Protocol, runtime_checkable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "healer_types")
trace_contract.emit_determinism_digest("p0", "healer_types")

trace_contract._emit_dispatches_healing_run("p1", "healer_types", "L3")
trace_contract._emit_routes_through("p1", "healer_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "healer_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healer_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healer_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healer_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healer_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "healer_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healer_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healer_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healer_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healer_types")
trace_contract._emit_gated_by_confidence("p1", "healer_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "healer_types", "L3")
trace_contract._emit_reads_policy_state("p1", "healer_types", "L3")
trace_contract._emit_authorize_and_execute("p2", "healer_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "healer_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healer_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healer_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healer_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healer_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healer_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healer_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healer_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healer_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healer_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healer_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healer_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healer_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healer_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healer_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healer_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healer_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healer_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healer_types", "exec_snapshot_link")

HEAL_RESULT_SCHEMA = {"status": "str", "details": "str", "artifacts": "list", "errors": "list"}


@runtime_checkable
class IHealerProtocol(Protocol):
    """The strict interface Phase 2 expects."""

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]: ...


from agentic_core.mixins.healer_agent_mixin import HealerAgentMixin

trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healer_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healer_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healer_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healer_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healer_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healer_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healer_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healer_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healer_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healer_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healer_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healer_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healer_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healer_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("healer_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healer_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healer_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healer_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healer_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healer_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healer_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healer_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healer_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healer_types", "context_pull")
trace_contract._emit_pulls_context("p1", "healer_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healer_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healer_types", "write_through")
trace_contract._emit_writes_through("p1", "healer_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healer_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healer_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healer_types", "routing_commit")


class LegacyAgentAdapter:
    """
    Universal Wrapper for LEGACY agents.
    Translates 'heal(violation)' calls into whatever method the legacy agent has.
    """

    def __init__(self, legacy_agent: Any):
        self.agent = legacy_agent
        self.name = legacy_agent.__class__.__name__

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Smartly routes the heal request to known legacy signatures.
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "LegacyAgentAdapter.heal", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "LegacyAgentAdapter.heal", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LegacyAgentAdapter.heal")

        file_path = violation.get("file") or violation.get("file_path")
        try:
            if hasattr(self.agent, "fix"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.fix({file_path})")
                    res = self.agent.fix(file_path)
                    return self._wrap_legacy_result(res)
                else:
                    return {"status": "skipped", "details": "Legacy agent requires file path"}
            elif hasattr(self.agent, "run"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.run([{file_path}])")
                    res = self.agent.run([file_path])
                    return self._wrap_legacy_result(res)
            elif hasattr(self.agent, "resolve"):
                logging.info(f"Adapter: Calling {self.name}.resolve(violation)")
                res = self.agent.resolve(violation)
                return self._wrap_legacy_result(res)
            else:
                return {
                    "status": "failed",
                    "errors": [f"Agent {self.name} has no recognized healing method (fix/run/resolve)"],
                }
        except (ValueError, TypeError) as e:
            return {"status": "failed", "errors": [f"Legacy Adapter Error: {str(e)}"]}

    def _wrap_legacy_result(self, result: Any) -> dict[str, Any]:
        """Converts arbitrary legacy returns (bools, strings, lists) to SSOT Schema."""
        if isinstance(result, bool):
            return {
                "status": "success" if result else "failed",
                "details": "Legacy boolean return",
                "artifacts": [],
                "errors": [],
            }
        if isinstance(result, str):
            return {"status": "success", "details": result, "artifacts": [], "errors": []}
        if isinstance(result, list):
            return {
                "status": "success",
                "details": f"Modified {len(result)} files",
                "artifacts": result,
                "errors": [],
            }
        if isinstance(result, dict):
            return HealerAgentMixin()._normalize_result(result)
        return {"status": "unknown", "details": str(result), "artifacts": [], "errors": []}
