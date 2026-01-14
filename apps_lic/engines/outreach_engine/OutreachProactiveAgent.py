from dataclasses import dataclass
"""
OutreachProactiveAgent - Extracted for one-class-per-file pattern.

Originally from: OutreachCapabilityMonitorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@dataclass
class OutreachProactiveAgent(OutreachAgent, MCPHardenedMixin):
    """
    Agent that proactively identifies and executes outreach tasks.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        super().__init__(ctx)
        self.name = "OutreachProactiveAgent"
        self.scheduler = OutreachProactiveScheduler(ctx)
        self.handoff = OutreachPredictiveHandoff(ctx)
        self.monitor = OutreachCapabilityMonitorAgent(ctx)

    async def execute(self) -> None:
        """Execute execute operation."""
        print(f"   [{self.name}] Running proactive analysis...")

        # Identify tasks
        tasks = self.scheduler.identify_tasks()
        print(f"   [{self.name}] Identified {len(tasks)} proactive tasks")

        # Check for handoff needs
        handoff = self.handoff.predict_handoff_need(
            agent_name=self.name,
            lead_count=len(self.ctx.leads),
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
                leads_processed=len(self.ctx.leads),
            )

        self.record_result(True, f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending")
        print(f"   [{self.name}] ✅ Proactive analysis complete")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
