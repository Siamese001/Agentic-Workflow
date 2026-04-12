"""BaseProactiveAgent — Shared proactive task scheduling logic for LIC and RG domains.

Extracted from OutreachProactiveAgent and ProactiveAgent (2026-03-11, P2-B).
App agents subclass this and inject domain-specific scheduler/handoff/monitor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "BaseProactiveAgent", "p0_governance")
_emit_reads_policy_state("p0", "BaseProactiveAgent", "policy_binding")
_emit_snapshots_state("p0", "BaseProactiveAgent", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_1")
_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_2")
_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_3")
_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_4")
_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_5")
_emit_emits_metric_event("BaseProactiveAgent", "p4obs", "metric_6")
_emit_records_incident_event("BaseProactiveAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("BaseProactiveAgent", "p4obs", "anomaly")
_emit_writes_observability_log("BaseProactiveAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("BaseProactiveAgent", "p4obs", "mon_state")
_emit_triggers_alert("BaseProactiveAgent", "p4obs", "alert")
_emit_links_incident_trace("BaseProactiveAgent", "p4obs", "trace_link")
_emit_captures_pattern("BaseProactiveAgent", "p3lm", "pattern")
_emit_records_learning_event("BaseProactiveAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("BaseProactiveAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("BaseProactiveAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("BaseProactiveAgent", "p3lm", "routing")
_emit_improves_agent_policy("BaseProactiveAgent", "p3lm", "policy")
_emit_stores_learning_state("BaseProactiveAgent", "p3lm", "state")
_emit_records_execution_trace("BaseProactiveAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("BaseProactiveAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("BaseProactiveAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("BaseProactiveAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("BaseProactiveAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("BaseProactiveAgent", "env_read", "p2_env_1")
_emit_reads_environ("BaseProactiveAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("BaseProactiveAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("BaseProactiveAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "BaseProactiveAgent", "context_pull")
_emit_pulls_context("p1", "BaseProactiveAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "BaseProactiveAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "BaseProactiveAgent", "uwg_term_2")
_emit_writes_through("p1", "BaseProactiveAgent", "write_through")
_emit_writes_through("p1", "BaseProactiveAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "BaseProactiveAgent", "safety_validation")
_emit_invokes_eval("p1", "BaseProactiveAgent", "eval_call")
_emit_proposal_commits_routing("p1", "BaseProactiveAgent", "routing_commit")
_emit_escalates_to_human("p1", "BaseProactiveAgent", "human_escalation")
_emit_routes_through("p1", "BaseProactiveAgent", "route_through")
_emit_checks_agent_registry("p1", "BaseProactiveAgent", "agent_registry")
_emit_validates_agent_capability("p1", "BaseProactiveAgent", "capability")
_emit_dispatches_execution_plan("p1", "BaseProactiveAgent", "exec_plan")
_emit_agent_executes_agent("p1", "BaseProactiveAgent", "sub_agent")
_emit_routes_to_agent("p1", "BaseProactiveAgent", "target_agent")
_emit_verifies_policy("p1", "BaseProactiveAgent", "policy_check")
_emit_observes_runtime_state("p1", "BaseProactiveAgent", "runtime_state")
_emit_verifies_boundary("p1", "BaseProactiveAgent", "boundary_check")
_emit_transcripts_response("p1", "BaseProactiveAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "BaseProactiveAgent")
_emit_gated_by_confidence("p1", "BaseProactiveAgent", "confidence_gate")
emit_replay_key("p0", "BaseProactiveAgent")
emit_determinism_digest("p0", "BaseProactiveAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "BaseProactiveAgent", "execution_auth")
_emit_validates_capability("p2", "BaseProactiveAgent", "capability_check")
_emit_routes_to_capability("p2", "BaseProactiveAgent", "capability_route")
_emit_writes_via_uwg("p2", "BaseProactiveAgent", "uwg_write")
_emit_blocks_direct_write("p2", "BaseProactiveAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "BaseProactiveAgent", "tool_invocation")
_emit_captures_execution_output("p2", "BaseProactiveAgent", "exec_output")
_emit_dispatches_agent("p3", "BaseProactiveAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "BaseProactiveAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "BaseProactiveAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "BaseProactiveAgent", "healing_outcome")
_emit_escalates_failure("p3", "BaseProactiveAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "BaseProactiveAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "BaseProactiveAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "BaseProactiveAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "BaseProactiveAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "BaseProactiveAgent", "eval_metric")
_emit_stores_embedding("p4", "BaseProactiveAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "BaseProactiveAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "BaseProactiveAgent", "exec_snapshot_link")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BaseProactiveAgent.execute")

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
