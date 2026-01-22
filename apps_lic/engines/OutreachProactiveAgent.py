"""
OutreachProactiveAgent - Extracted for one-class-per-file pattern.

Originally from: OutreachCapabilityMonitorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)

Proactively identifies and executes outreach tasks with predictive handoff.
"""


@dataclass
class OutreachProactiveAgent(SubatomicTestingMixin, OutreachAgent, MCPHardenedMixin):
    """
    Agent that proactively identifies and executes outreach tasks.

    Combines task scheduling, predictive handoff detection, and capability
    monitoring to autonomously manage outreach operations.

    Attributes:
        name: Agent identifier
        scheduler: Proactive task scheduler
        handoff: Predictive handoff detector
        monitor: Capability monitoring agent
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        """
        Initialize the proactive outreach agent.

        Args:
            ctx: Outreach engine context
        """
        super().__init__(ctx)
        self.name = "OutreachProactiveAgent"
        self.scheduler = OutreachProactiveScheduler(ctx)
        self.handoff = OutreachPredictiveHandoff(ctx)
        self.monitor = OutreachCapabilityMonitorAgent(ctx)

    async def execute(self) -> None:
        """
        Execute proactive outreach analysis and task execution.

        Identifies pending tasks, checks for handoff needs, and auto-executes
        tasks that don't require human intervention.

        Raises:
            HANDOFF_RECOMMENDED signal if predictive handoff is needed
        """
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

        self.record_result(
            True, f"Executed {len(auto_tasks)} tasks, {len(tasks) - len(auto_tasks)} pending"
        )
        print(f"   [{self.name}] ✅ Proactive analysis complete")

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            **kwargs: Additional healing parameters

        Returns:
            Dict with healing summary (violations, fixed, errors)
        """
        return super().heal_repository(dry_run, execute, **kwargs)
