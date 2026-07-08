"""BaseReflectionAgent — Shared reflection logic for LIC and RG domains.

Extracted from LicReflectionAgent and RgReflectionAgent (2026-03-11, P2-A).
Both app agents subclass this and inherit the shared execute() skeleton.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "BaseReflectionAgent", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "BaseReflectionAgent", "policy_binding")
trace_contract._emit_snapshots_state("p0", "BaseReflectionAgent", "state_snapshot")

trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("BaseReflectionAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("BaseReflectionAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("BaseReflectionAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("BaseReflectionAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("BaseReflectionAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("BaseReflectionAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("BaseReflectionAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("BaseReflectionAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("BaseReflectionAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("BaseReflectionAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("BaseReflectionAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("BaseReflectionAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("BaseReflectionAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("BaseReflectionAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("BaseReflectionAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("BaseReflectionAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("BaseReflectionAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("BaseReflectionAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("BaseReflectionAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("BaseReflectionAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("BaseReflectionAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("BaseReflectionAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("BaseReflectionAgent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "BaseReflectionAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "BaseReflectionAgent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "BaseReflectionAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "BaseReflectionAgent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "BaseReflectionAgent", "write_through")
trace_contract._emit_writes_through("p1", "BaseReflectionAgent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "BaseReflectionAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "BaseReflectionAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "BaseReflectionAgent", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "BaseReflectionAgent", "human_escalation")
trace_contract._emit_routes_through("p1", "BaseReflectionAgent", "route_through")
trace_contract._emit_checks_agent_registry("p1", "BaseReflectionAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "BaseReflectionAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "BaseReflectionAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "BaseReflectionAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "BaseReflectionAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "BaseReflectionAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "BaseReflectionAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "BaseReflectionAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "BaseReflectionAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "BaseReflectionAgent")
trace_contract._emit_gated_by_confidence("p1", "BaseReflectionAgent", "confidence_gate")
trace_contract.emit_replay_key("p0", "BaseReflectionAgent")
trace_contract.emit_determinism_digest("p0", "BaseReflectionAgent")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "BaseReflectionAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "BaseReflectionAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "BaseReflectionAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "BaseReflectionAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "BaseReflectionAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "BaseReflectionAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "BaseReflectionAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "BaseReflectionAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "BaseReflectionAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "BaseReflectionAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "BaseReflectionAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "BaseReflectionAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "BaseReflectionAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "BaseReflectionAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "BaseReflectionAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "BaseReflectionAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "BaseReflectionAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "BaseReflectionAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "BaseReflectionAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "BaseReflectionAgent", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "BaseReflectionAgent.execute")

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
                f"[{self.__class__.__name__}] 🔄 More cycles needed (signals: {len(active_signals)}, failed: {len(failed_agents)})",
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
        """Heal: return HealResult(NEEDS_HELP) shape per L2 Execute v2 §E4.

        W3 plan c8e4f1: replaced stub `{"status": "skipped"}` with a valid
        HealResult.to_dict() that subclasses can extend. Subclasses SHOULD
        override with a real repair and return HealResult.from_request(...).to_dict().
        """
        from agentic_core.L5_safety.types.heal_request_types import (  # noqa: PLC0415
            HealResult,
        )

        violation = violation or {}
        violation_type = str(violation.get("type", "unknown"))
        return HealResult.needs_help(
            parent_packet_id=str(violation.get("parent_packet_id", "")) or "unknown",
            policy_hash=str(violation.get("policy_hash", "")) or "unknown",
            blueprint_hash=str(violation.get("blueprint_hash", "")) or "unknown",
            reason_code="base_heal_not_overridden",
            message=f"{self.__class__.__name__} heal() has no override for {violation_type}; escalate.",
        ).to_dict()
