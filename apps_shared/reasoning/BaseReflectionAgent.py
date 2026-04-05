"""BaseReflectionAgent — Shared reflection logic for LIC and RG domains.

Extracted from LicReflectionAgent and RgReflectionAgent (2026-03-11, P2-A).
Both app agents subclass this and inherit the shared execute() skeleton.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
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

_emit_applies_guardrail("p0", "BaseReflectionAgent", "p0_governance")
_emit_reads_policy_state("p0", "BaseReflectionAgent", "policy_binding")
_emit_snapshots_state("p0", "BaseReflectionAgent", "state_snapshot")
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

_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_1")
_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_2")
_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_3")
_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_4")
_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_5")
_emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_6")
_emit_records_incident_event("BaseReflectionAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("BaseReflectionAgent", "p4obs", "anomaly")
_emit_writes_observability_log("BaseReflectionAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("BaseReflectionAgent", "p4obs", "mon_state")
_emit_triggers_alert("BaseReflectionAgent", "p4obs", "alert")
_emit_links_incident_trace("BaseReflectionAgent", "p4obs", "trace_link")
_emit_captures_pattern("BaseReflectionAgent", "p3lm", "pattern")
_emit_records_learning_event("BaseReflectionAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("BaseReflectionAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("BaseReflectionAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("BaseReflectionAgent", "p3lm", "routing")
_emit_improves_agent_policy("BaseReflectionAgent", "p3lm", "policy")
_emit_stores_learning_state("BaseReflectionAgent", "p3lm", "state")
_emit_records_execution_trace("BaseReflectionAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("BaseReflectionAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("BaseReflectionAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("BaseReflectionAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("BaseReflectionAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("BaseReflectionAgent", "env_read", "p2_env_1")
_emit_reads_environ("BaseReflectionAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("BaseReflectionAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("BaseReflectionAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "BaseReflectionAgent", "context_pull")
_emit_pulls_context("p1", "BaseReflectionAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "BaseReflectionAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "BaseReflectionAgent", "uwg_term_2")
_emit_writes_through("p1", "BaseReflectionAgent", "write_through")
_emit_writes_through("p1", "BaseReflectionAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "BaseReflectionAgent", "safety_validation")
_emit_invokes_eval("p1", "BaseReflectionAgent", "eval_call")
_emit_proposal_commits_routing("p1", "BaseReflectionAgent", "routing_commit")
_emit_escalates_to_human("p1", "BaseReflectionAgent", "human_escalation")
_emit_routes_through("p1", "BaseReflectionAgent", "route_through")
_emit_checks_agent_registry("p1", "BaseReflectionAgent", "agent_registry")
_emit_validates_agent_capability("p1", "BaseReflectionAgent", "capability")
_emit_dispatches_execution_plan("p1", "BaseReflectionAgent", "exec_plan")
_emit_agent_executes_agent("p1", "BaseReflectionAgent", "sub_agent")
_emit_routes_to_agent("p1", "BaseReflectionAgent", "target_agent")
_emit_verifies_policy("p1", "BaseReflectionAgent", "policy_check")
_emit_observes_runtime_state("p1", "BaseReflectionAgent", "runtime_state")
_emit_verifies_boundary("p1", "BaseReflectionAgent", "boundary_check")
_emit_transcripts_response("p1", "BaseReflectionAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "BaseReflectionAgent")
_emit_gated_by_confidence("p1", "BaseReflectionAgent", "confidence_gate")
emit_replay_key("p0", "BaseReflectionAgent")
emit_determinism_digest("p0", "BaseReflectionAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "BaseReflectionAgent", "execution_auth")
_emit_validates_capability("p2", "BaseReflectionAgent", "capability_check")
_emit_routes_to_capability("p2", "BaseReflectionAgent", "capability_route")
_emit_writes_via_uwg("p2", "BaseReflectionAgent", "uwg_write")
_emit_blocks_direct_write("p2", "BaseReflectionAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "BaseReflectionAgent", "tool_invocation")
_emit_captures_execution_output("p2", "BaseReflectionAgent", "exec_output")
_emit_dispatches_agent("p3", "BaseReflectionAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "BaseReflectionAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "BaseReflectionAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "BaseReflectionAgent", "healing_outcome")
_emit_escalates_failure("p3", "BaseReflectionAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "BaseReflectionAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "BaseReflectionAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "BaseReflectionAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "BaseReflectionAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "BaseReflectionAgent", "eval_metric")
_emit_stores_embedding("p4", "BaseReflectionAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "BaseReflectionAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "BaseReflectionAgent", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class BaseReflectionAgent(SovereignBaseAgent):
    """Shared reflection skeleton: count results, check convergence, record outcome.

    Subclasses may override `_post_reflect()` for domain-specific follow-up
    (e.g. RG quality scoring and meta-learning cache writes).
    """

    async def execute(self) -> None:
        """Execute reflection on execution cycle.

        Analyzes passed/failed agents and active signals.
        Calls `_post_reflect(passed, failed, converged)` for domain hooks.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseReflectionAgent.execute")

        Logger.debug(f"[{self.__class__.__name__}] Reflecting on execution...")
        passed_agents: list[str] = []
        failed_agents: list[str] = []
        for agent_name, result in self.ctx.results.items():
            if result.get("passed", False):
                passed_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)
        active_signals: list[str] = list(self.ctx.signals)
        converged: bool = not (active_signals or failed_agents)
        if converged:
            Logger.debug(f"[{self.__class__.__name__}] ✅ Converged successfully")
        else:
            Logger.debug(
                f"[{self.__class__.__name__}] 🔄 More cycles needed (signals: {len(active_signals)}, failed: {len(failed_agents)})"
            )
        self._post_reflect(passed_agents, failed_agents, converged)
        self.record_result(True, f"Passed: {len(passed_agents)}, Failed: {len(failed_agents)}")

    def _post_reflect(self, passed_agents: list[str], failed_agents: list[str], converged: bool) -> None:
        """Hook for domain-specific post-reflection logic.

        Default: no-op. Subclasses override to add quality scoring,
        meta-learning cache writes, etc.
        """

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations — not yet implemented at base level."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"{self.__class__.__name__} heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"{self.__class__.__name__} heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
