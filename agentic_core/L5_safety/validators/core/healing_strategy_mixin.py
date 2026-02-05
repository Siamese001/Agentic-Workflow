"""
HealingStrategyMixin - Unified Healing Access for Agents

[PHASE 5 MIGRATION] Provides single interface to healing operations.
"""

from agentic_core.L5_safety.validators.core.healing_sovereign_orchestrator_types import (
    HealingSovereignOrchestrator,
    get_healing_orchestrator,
)


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
