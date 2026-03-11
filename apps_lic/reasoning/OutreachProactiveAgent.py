"""OutreachProactiveAgent — LIC domain proactive task agent.

Originally from: OutreachCapabilityMonitorAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-B) — now subclasses BaseProactiveAgent.
"""

from dataclasses import dataclass
from typing import Any

from apps_shared.reasoning.BaseProactiveAgent import BaseProactiveAgent


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# OutreachEngineContext stub
class OutreachEngineContext:
    def __init__(self, *args, **kwargs):
        pass


# STUB: OutreachAgent base class (deprecated)
# RETIRED: OutreachAgent removed from active agent pool (2026-02-08)


@dataclass
class OutreachProactiveAgent(BaseProactiveAgent):
    """Proactively identifies and executes outreach tasks with predictive handoff.

    Inherits execute() skeleton from BaseProactiveAgent.
    Overrides _get_handoff_kwargs() to pass outreach-specific lead_count.
    Overrides _record_task_execution() to pass leads_processed to monitor.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        """Initialize the proactive outreach agent."""
        super().__init__(ctx)
        self.name = "OutreachProactiveAgent"
        self.scheduler = OutreachProactiveScheduler(ctx)
        self.handoff = OutreachPredictiveHandoff(ctx)
        self.monitor = OutreachCapabilityMonitorAgent(ctx)

    def _get_handoff_kwargs(self, tasks: list) -> dict[str, Any]:
        """Pass outreach-specific lead_count to predict_handoff_need."""
        return {"lead_count": len(self.ctx.leads)}

    def _record_task_execution(self, task: Any) -> None:
        """Record execution with outreach-specific leads_processed field."""
        self.monitor.record_execution(
            agent_name=self.name,
            TaskType=task.name,
            success=True,
            duration_ms=task.estimated_duration_ms,
            leads_processed=len(self.ctx.leads),
        )
