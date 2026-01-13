from agentic_core.utils.core_extensions.rate_limit_mixin import RateLimitMixin
from agentic_core.utils.core_extensions.state_validation_mixin import StateValidationMixin
from agentic_core.utils.core_extensions.event_emission_mixin import EventEmissionMixin
from agentic_core.utils.core_extensions.context_propagation_mixin import ContextPropagationMixin

class PilotOrchestrator(RateLimitMixin, StateValidationMixin, EventEmissionMixin, ContextPropagationMixin):
    """
    Pilot L3 Agent demonstrating the fully hardened stack.
    - Limits orchestration rate (4.1)
    - Validates plan state (4.2)
    - Emits observable events (4.3)
    - Propagates distributed traces (4.7)
    """

    _rate_limits = {"orchestrate": {"rate": 10, "per": 60, "burst": 10}}

    @ContextPropagationMixin.trace_context
    @StateValidationMixin.validate_state(pre=lambda s: s.is_ready())
    @RateLimitMixin.rate_limit("orchestrate")
    @EventEmissionMixin.observe_execution("orchestration_flow")
    async def run_pilot(self, goal: str, executor_agent):
        """Standardizes a delegation flow with full hardening."""
        self.emit_event("goal.received", {"goal": goal})

        # The trace_id from @trace_context automatically flows into the executor
        result = await executor_agent.execute_task(goal)

        return result

    def is_ready(self) -> bool:
        return True  # Placeholder for actual health check
