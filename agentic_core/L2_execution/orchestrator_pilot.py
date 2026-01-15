from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin
from agentic_core.utils.core_extensions.state_validation_mixin import StateValidationMixin
from agentic_core.utils.core_extensions.event_emission_mixin import EventEmissionMixin
from agentic_core.utils.core_extensions.context_propagation_mixin import ContextPropagationMixin

class PilotExecutor(RateLimitMixin, StateValidationMixin, EventEmissionMixin, ContextPropagationMixin):
    """Pilot L2 agent used by PilotOrchestrator to demonstrate trace/span propagation."""

    _rate_limits = {"execute": {"rate": 30, "per": 60, "burst": 30}}

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", self.__class__.__name__)
        super().__init__(**kwargs)

    @ContextPropagationMixin.trace_context
    @StateValidationMixin.validate_state(pre=lambda s: s.is_ready())
    @RateLimitMixin.rate_limit("execute")
    @EventEmissionMixin.observe_execution("execution_flow")
    async def execute_task(self, goal: str):
        self.emit_event("task.received", {"goal": goal})
        return {"status": "ok", "goal": goal}

    def is_ready(self) -> bool:
        return True  # Placeholder for actual health check
