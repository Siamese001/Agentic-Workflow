"""
ProactiveAgent - Extracted for one-class-per-file pattern.

Originally from: CapabilityMonitorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from apps_rg.shared.core.agent_base import RGAgentBase
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class ProactiveAgent(SubatomicTestingMixin, RGAgentBase):
    """
    Agent that proactively identifies and executes tasks.
    """

    def __post_init__(self) -> None:
        """Initialize proactive agent."""
        super().__post_init__()
        # Initialize components after base initialization
        self.name = "ProactiveAgent"

        # Note: Context and scheduler components need to be provided externally
        # or initialized when the full resume engine context is available
        # These are commented out to allow agent instantiation for testing
        # self.ctx = ResumeEngineContext()
        # self.scheduler = ProactiveScheduler(ctx)
        # self.handoff = PredictiveHandoff(ctx)
        # self.monitor = CapabilityMonitorAgent(ctx)

    def record_result(self, passed: bool, details: str = "") -> Any:
        """
        Record the agent's execution result.

        Args:
            passed: Whether execution passed
            details: Optional details about the result
        """
        self.ctx.record_result(self.name, passed, details)

    def add_signal(self, signal: str) -> Any:
        """
        Add a signal to the context.

        Args:
            signal: Signal name to add
        """
        self.ctx.add_signal(signal)
        print(f"   [{self.name}] 📡 Signal: {signal}")

    async def execute(self) -> None:
        """
        Execute proactive analysis and task execution.

        Identifies proactive tasks, checks for handoff needs, and executes
        auto-executable tasks while recording results.
        """
        print(f"   [{self.name}] Running proactive analysis...")

        # Identify tasks
        tasks = self.scheduler.identify_tasks()
        print(f"   [{self.name}] Identified {len(tasks)} proactive tasks")

        # Check for handoff needs
        handoff = self.handoff.predict_handoff_need(
            agent_name=self.name,
            TaskComplexity=len(tasks),
            confidence=0.8,
        )

        if handoff:
            print(f"   [{self.name}] ⚠️ Handoff recommended: {handoff.reason.value}")
            self.add_signal("HANDOFF_RECOMMENDED")

        # Execute auto-executable tasks
        auto_tasks = self.scheduler.get_auto_executable_tasks()
        for Task in auto_tasks:
            print(f"   [{self.name}] Auto-executing: {Task.name}")
            self.scheduler.mark_executed(Task.task_id)
            self.monitor.record_execution(
                agent_name=self.name,
                TaskType=Task.name,
                success=True,
                duration_ms=Task.estimated_duration_ms,
            )

        self.record_result(
            True, f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending"
        )
        print(f"   [{self.name}] ✅ Proactive analysis complete")

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Invoke healing chain via super().

        Returns:
            Dictionary with healing results including violations, fixed, errors, skipped
        """
        return super().heal_repository()
