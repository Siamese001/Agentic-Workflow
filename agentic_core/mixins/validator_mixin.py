"""
ValidatorMixin - Unified Validation Access for Agents

[PHASE 5 MIGRATION] Provides single interface to validation operations.
"""

from typing import Any

try:
    from agentic_core.L5_safety.types.healing_orchestration_suite_types import (
        ValidatorOrchestrator,
        get_validator_orchestrator,
    )
except ImportError:

    class ValidatorOrchestrator:
        """Stub orchestrator when real module is unavailable."""

        pass

    def get_validator_orchestrator():
        return None


class ValidatorMixin:
    """
    Mixin providing unified validator orchestrator access.
    """

    _validator_orchestrator: ValidatorOrchestrator | None = None

    @property
    def validator_orchestrator(self) -> ValidatorOrchestrator:
        """Lazy-load validator orchestrator singleton."""
        if self._validator_orchestrator is None:
            self._validator_orchestrator = get_validator_orchestrator()
        return self._validator_orchestrator

    async def orchestrator_validate(self, content: Any, validator_name: str, context: dict = None) -> dict:
        """Execute validation through orchestrator."""
        return await self.validator_orchestrator.validate(content, validator_name, context)
