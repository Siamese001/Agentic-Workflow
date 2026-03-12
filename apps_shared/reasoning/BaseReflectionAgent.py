"""BaseReflectionAgent — Shared reflection logic for LIC and RG domains.

Extracted from LicReflectionAgent and RgReflectionAgent (2026-03-11, P2-A).
Both app agents subclass this and inherit the shared execute() skeleton.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

@dataclass
class BaseReflectionAgent(SovereignBaseAgent):
    """Shared reflection skeleton: count results, check convergence, record outcome.

    Subclasses may override `_post_reflect()` for domain-specific follow-up
    (e.g. RG quality scoring and meta-learning cache writes).
    """

    async def execute(self) -> None:
        """Execute reflection on execution cycle.

        Analyzes passed/failed agents and active signals.
        Calls `_post_reflect(passed, failed, converged)` for domain hooks.
        """
        Logger.debug(f'[{self.__class__.__name__}] Reflecting on execution...')
        passed_agents: list[str] = []
        failed_agents: list[str] = []
        for agent_name, result in self.ctx.results.items():
            if result.get('passed', False):
                passed_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)
        active_signals: list[str] = list(self.ctx.signals)
        converged: bool = not (active_signals or failed_agents)
        if converged:
            Logger.debug(f'[{self.__class__.__name__}] ✅ Converged successfully')
        else:
            Logger.debug(f'[{self.__class__.__name__}] 🔄 More cycles needed (signals: {len(active_signals)}, failed: {len(failed_agents)})')
        self._post_reflect(passed_agents, failed_agents, converged)
        self.record_result(True, f'Passed: {len(passed_agents)}, Failed: {len(failed_agents)}')

    def _post_reflect(self, passed_agents: list[str], failed_agents: list[str], converged: bool) -> None:
        """Hook for domain-specific post-reflection logic.

        Default: no-op. Subclasses override to add quality scoring,
        meta-learning cache writes, etc.
        """

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations — not yet implemented at base level."""
        violation_type = violation.get('type', 'unknown')
        try:
            return {'status': 'skipped', 'details': f'{self.__class__.__name__} heal() not yet implemented for {violation_type}', 'artifacts': [], 'errors': []}
        except Exception as e:
            return {'status': 'failed', 'details': f'{self.__class__.__name__} heal() failed: {str(e)}', 'artifacts': [], 'errors': [str(e)]}
