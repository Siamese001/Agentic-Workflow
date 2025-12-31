"""
AdaptiveExecutionMixin – Enables dynamic mode selection based on context
"""
import logging
from typing import Dict, Any


class AdaptiveExecutionMixin:
    _execution_modes = ["standard", "conservative", "aggressive", "minimal"]
    _current_mode: str = "standard"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{self.__class__.__name__}.Adaptive")

    async def select_execution_mode(self, context: Dict[str, Any]) -> str:
        load = context.get("system_load", 0.0)
        if load > 0.8:
            return "minimal"

        failure_rate = await self._get_recent_failure_rate()
        if failure_rate > 0.3:
            return "conservative"

        if context.get("urgent", False):
            return "aggressive"

        return "standard"

    async def _get_recent_failure_rate(self) -> float:
        return 0.0  # Override in agents with history

    async def execute(self, ctx: Any = None) -> Any:
        context = await self._build_context(ctx) if hasattr(self, "_build_context") else {}
        self._current_mode = await self.select_execution_mode(context)
        self.logger.info(f"Executing in {self._current_mode} mode")

        if self._current_mode == "conservative":
            return await self._execute_conservative(ctx)
        elif self._current_mode == "aggressive":
            return await self._execute_aggressive(ctx)
        elif self._current_mode == "minimal":
            return await self._execute_minimal(ctx)
        return await self._execute_standard(ctx)

    async def _execute_standard(self, ctx): raise NotImplementedError
    async def _execute_conservative(self, ctx): return await self._execute_standard(ctx)
    async def _execute_aggressive(self, ctx): return await self._execute_standard(ctx)
    async def _execute_minimal(self, ctx): return {"minimal": True, "result": "skipped_non_essential"}
