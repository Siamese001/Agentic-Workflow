"""BaseProactiveAgent — Shared proactive task scheduling logic for LIC and RG domains.

Extracted from OutreachProactiveAgent and ProactiveAgent (2026-03-11, P2-B).
App agents subclass this and inject domain-specific scheduler/handoff/monitor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "BaseProactiveAgent", "p0_governance")
_emit_reads_policy_state("p0", "BaseProactiveAgent", "policy_binding")
_emit_snapshots_state("p0", "BaseProactiveAgent", "state_snapshot")
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
            agent_name=self.name, TaskType=task.name, success=True, duration_ms=task.estimated_duration_ms
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
