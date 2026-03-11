"""BaseProactiveAgent — Shared proactive task scheduling logic for LIC and RG domains.

Extracted from OutreachProactiveAgent and ProactiveAgent (2026-03-11, P2-B).
App agents subclass this and inject domain-specific scheduler/handoff/monitor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        Logger.debug(f"[{self.__class__.__name__}] Running proactive analysis...")

        tasks = self.scheduler.identify_tasks()
        Logger.debug(f"[{self.__class__.__name__}] Identified {len(tasks)} proactive tasks")

        handoff_kwargs = self._get_handoff_kwargs(tasks)
        handoff = self.handoff.predict_handoff_need(
            agent_name=self.name,
            confidence=0.8,
            **handoff_kwargs,
        )

        if handoff:
            Logger.debug(f"[{self.__class__.__name__}] ⚠️ Handoff recommended: {handoff.reason.value}")
            self.add_signal("HANDOFF_RECOMMENDED")

        auto_tasks = self.scheduler.get_auto_executable_tasks()
        for task in auto_tasks:
            Logger.debug(f"[{self.__class__.__name__}] Auto-executing: {task.name}")
            self.scheduler.mark_executed(task.task_id)
            self._record_task_execution(task)

        self.record_result(
            True,
            f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending",
        )
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
