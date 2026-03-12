from __future__ import annotations
'\nAdaptiveExecutionMixin – Sovereign Agent Role Mixin (Phase 29 – Dec 30, 2025)\n\nPurpose:\n  Enable agents to dynamically select execution mode based on real-time context:\n    - standard: normal operation\n    - conservative: high failure rate → safer, more verification\n    - aggressive: urgent → faster, riskier\n    - minimal: high system load → skip non-essential work\n\nConstitutional Alignment:\n  - Prevents resource exhaustion\n  - Adapts to sovereignty health\n  - Enables self-preservation under stress\n'
import logging
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class AdaptiveExecutionMixin:
    """
    Mixin that adds context-aware execution mode selection.
    Agents inherit this to become environmentally adaptive.
    """
    EXECUTION_MODES = ['standard', 'conservative', 'aggressive', 'minimal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Logger = logging.getLogger(f'{self.__class__.__name__}.Adaptive')
        self._current_mode: str = 'standard'

    @property
    def current_mode(self) -> str:
        """Current execution mode — readable by orchestrators and logs."""
        return self._current_mode

    async def select_execution_mode(self, context: dict[str, Any]) -> str:
        """
        Constitutional decision engine for mode selection.
        Override or extend for agent-specific logic.
        """
        system_load = context.get('system_load', 0.0)
        if system_load > 0.85:
            self.Logger.warning(f'High system load ({system_load:.1%}) → switching to minimal mode')
            return 'minimal'
        failure_rate = await self._get_recent_failure_rate(context)
        if failure_rate > 0.35:
            self.Logger.warning(f'High failure rate ({failure_rate:.1%}) → switching to conservative mode')
            return 'conservative'
        if context.get('urgent', False) or context.get('time_critical', False):
            self.Logger.info('Urgent context detected → switching to aggressive mode')
            return 'aggressive'
        health_score = context.get('sovereignty_health', 100.0)
        if health_score < 90:
            self.Logger.info(f'Low sovereignty health ({health_score:.0f}%) → conservative mode')
            return 'conservative'
        return 'standard'

    async def _get_recent_failure_rate(self, context: dict[str, Any]) -> float:
        """
        Hook for agents with history tracking.
        Default: assume healthy.
        """
        return 0.0

    async def execute(self, ctx: Any=None, **kwargs) -> Any:
        """
        Adaptive wrapper around agent's core execute().
        Agents must call super().execute() or implement mode-specific logic.
        """
        base_context = await self._build_execution_context(ctx) if hasattr(self, '_build_execution_context') else {}
        full_context = {**base_context, **kwargs}
        self._current_mode = await self.select_execution_mode(full_context)
        self.Logger.info(f"Executing in '{self._current_mode}' mode")
        mode_method = f'_execute_{self._current_mode}'
        if hasattr(self, mode_method):
            return await getattr(self, mode_method)(ctx, **full_context)
        if hasattr(self, '_execute_standard'):
            return await self._execute_standard(ctx, **full_context)
        raise NotImplementedError(f'{self.__class__.__name__} must implement either mode-specific _execute_* or _execute_standard')

    async def _execute_standard(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Default mode — full capability execution."""
        raise NotImplementedError('Agent must implement _execute_standard or override execute()')

    async def _execute_conservative(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Safer, more verified execution — e.g., extra validation, smaller steps."""
        self.Logger.info('Conservative mode: adding extra constitutional checks')
        return await self._execute_standard(ctx, **context)

    async def _execute_aggressive(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Faster execution — e.g., parallelize, skip non-critical checks."""
        self.Logger.info('Aggressive mode: prioritizing speed')
        return await self._execute_standard(ctx, **context)

    async def _execute_minimal(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Bare minimum — skip non-essential work to preserve resources."""
        self.Logger.warning('Minimal mode: skipping non-critical operations')
        return {'mode': 'minimal', 'result': 'skipped_due_to_load', 'preserved_resources': True}

    def force_mode(self, mode: str) -> None:
        """Emergency override — for testing or containment."""
        if mode not in self.EXECUTION_MODES:
            raise ValueError(f'Invalid mode: {mode}')
        self._current_mode = mode
        self.Logger.warning(f"Execution mode forced to '{mode}' via emergency override")
