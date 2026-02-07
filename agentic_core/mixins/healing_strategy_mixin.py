"""
HealingStrategyMixin - Unified Healing Access for Agents

[PHASE 5 MIGRATION] Provides single interface to healing operations.
"""

try:
    from agentic_core.L5_safety.types.healing_orchestration_suite_types_validator import (
        HealingSovereignOrchestrator,
        get_healing_orchestrator,
    )
except ImportError:
    # Stub for healing resilience when orchestrator module is missing
    class HealingSovereignOrchestrator:
        """Stub orchestrator when real module is unavailable."""

        pass

    def get_healing_orchestrator():
        return None


class HealingStrategyMixin:
    """
    Mixin providing unified healing orchestrator access.

    Usage:
        class MyAgent(HealingStrategyMixin, SovereignBaseAgent):
            async def fix_issue(self, violation: dict):
                return await self.orchestrator_heal(violation)
    """

    _healing_orchestrator: HealingSovereignOrchestrator | None = None

    @property
    def healing_orchestrator(self) -> HealingSovereignOrchestrator:
        """Lazy-load healing orchestrator singleton."""
        if self._healing_orchestrator is None:
            self._healing_orchestrator = get_healing_orchestrator()
        return self._healing_orchestrator

    async def orchestrator_heal(self, violation: dict, context: dict = None) -> dict:
        """Execute healing through orchestrator."""
        return await self.healing_orchestrator.heal(violation, context)
