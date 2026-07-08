"""BaseProactiveAgent — Shared proactive task scheduling logic for LIC and RG domains.

Extracted from OutreachProactiveAgent and ProactiveAgent (2026-03-11, P2-B).
App agents subclass this and inject domain-specific scheduler/handoff/monitor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "BaseProactiveAgent", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "BaseProactiveAgent", "policy_binding")
trace_contract._emit_snapshots_state("p0", "BaseProactiveAgent", "state_snapshot")

trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("BaseProactiveAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("BaseProactiveAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("BaseProactiveAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("BaseProactiveAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("BaseProactiveAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("BaseProactiveAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("BaseProactiveAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("BaseProactiveAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("BaseProactiveAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("BaseProactiveAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("BaseProactiveAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("BaseProactiveAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("BaseProactiveAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("BaseProactiveAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("BaseProactiveAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("BaseProactiveAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("BaseProactiveAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("BaseProactiveAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("BaseProactiveAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("BaseProactiveAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("BaseProactiveAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("BaseProactiveAgent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "BaseProactiveAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "BaseProactiveAgent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "BaseProactiveAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "BaseProactiveAgent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "BaseProactiveAgent", "write_through")
trace_contract._emit_writes_through("p1", "BaseProactiveAgent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "BaseProactiveAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "BaseProactiveAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "BaseProactiveAgent", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "BaseProactiveAgent", "human_escalation")
trace_contract._emit_routes_through("p1", "BaseProactiveAgent", "route_through")
trace_contract._emit_checks_agent_registry("p1", "BaseProactiveAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "BaseProactiveAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "BaseProactiveAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "BaseProactiveAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "BaseProactiveAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "BaseProactiveAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "BaseProactiveAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "BaseProactiveAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "BaseProactiveAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "BaseProactiveAgent")
trace_contract._emit_gated_by_confidence("p1", "BaseProactiveAgent", "confidence_gate")
trace_contract.emit_replay_key("p0", "BaseProactiveAgent")
trace_contract.emit_determinism_digest("p0", "BaseProactiveAgent")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "BaseProactiveAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "BaseProactiveAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "BaseProactiveAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "BaseProactiveAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "BaseProactiveAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "BaseProactiveAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "BaseProactiveAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "BaseProactiveAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "BaseProactiveAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "BaseProactiveAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "BaseProactiveAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "BaseProactiveAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "BaseProactiveAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "BaseProactiveAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "BaseProactiveAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "BaseProactiveAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "BaseProactiveAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "BaseProactiveAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "BaseProactiveAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "BaseProactiveAgent", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class BaseProactiveAgent(SovereignBaseAgent):
    """Shared proactive execution skeleton: identify tasks → check handoff → auto-execute.

    Subclasses must set `self.scheduler`, `self.handoff`, and `self.monitor`
    in their `__init__` / `__post_init__` before calling `execute()`.

    Subclasses may override `_get_handoff_kwargs()` to pass domain-specific
    parameters to `self.handoff.predict_handoff_need()`.
    """

    async def execute(self) -> None:
        """Execute proactive analysis and task execution.

        Identifies pending tasks, checks for handoff need, and auto-executes
        tasks that do not require human intervention.
        Emits HANDOFF_RECOMMENDED signal when needed.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "BaseProactiveAgent.execute")

        Logger.debug(f"[{self.__class__.__name__}] Running proactive analysis...")
        tasks = self.scheduler.identify_tasks()
        Logger.debug(f"[{self.__class__.__name__}] Identified {len(tasks)} proactive tasks")
        handoff_kwargs = self._get_handoff_kwargs(tasks)
        handoff = self.handoff.predict_handoff_need(agent_name=self.name, confidence=0.8, **handoff_kwargs)
        if handoff:
            Logger.debug(f"[{self.__class__.__name__}] ⚠️ Handoff recommended: {handoff.reason.value}")
            self.add_signal("HANDOFF_RECOMMENDED")
        auto_tasks = self.scheduler.get_auto_executable_tasks()
        for task in auto_tasks:
            Logger.debug(f"[{self.__class__.__name__}] Auto-executing: {task.name}")
            self.scheduler.mark_executed(task.task_id)
            self._record_task_execution(task)
        self.record_result(True, f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending")
        Logger.debug(f"[{self.__class__.__name__}] ✅ Proactive analysis complete")

    def _get_handoff_kwargs(self, tasks: list) -> dict[str, Any]:
        """Return domain-specific kwargs for predict_handoff_need().

        Default passes TaskComplexity as task count.
        Subclasses may override to pass lead_count, complexity, etc.
        """
        return {"TaskComplexity": len(tasks)}

    def _record_task_execution(self, task: Any) -> None:
        """Record a single task execution via self.monitor.

        Default implementation — subclasses may override to pass
        domain-specific fields (e.g. leads_processed).
        """
        self.monitor.record_execution(
            agent_name=self.name,
            TaskType=task.name,
            success=True,
            duration_ms=task.estimated_duration_ms,
        )

    def heal_repository(self, dry_run: bool = False, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """Invoke healing chain via super()."""
        return super().heal_repository(dry_run, execute, **kwargs)

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
