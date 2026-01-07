"""
ProactiveAgent - Extracted for one-class-per-file pattern.

Originally from: CapabilityMonitorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class ProactiveAgent(ResumeAgent):
    """
    Agent that proactively identifies and executes tasks.
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        super().__init__(ctx)
        self.name = "ProactiveAgent"
        self.scheduler = ProactiveScheduler(ctx)
        self.handoff = PredictiveHandoff(ctx)
        self.monitor = CapabilityMonitorAgent(ctx)

    def record_result(self, passed: bool, details: str = ""):
        """Record the agent's result."""
        self.ctx.record_result(self.name, passed, details)

    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.ctx.add_signal(signal)
        print(f"   [{self.name}] 📡 Signal: {signal}")

    async def execute(self) -> None:
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

        self.record_result(True, f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending")
        print(f"   [{self.name}] ✅ Proactive analysis complete")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
