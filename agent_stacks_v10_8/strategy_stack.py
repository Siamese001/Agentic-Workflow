"""Strategy stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict, Optional

from stacks_v10_7.strategy import QueryComplexityClassifier, ToTStrategistAgent


class StrategyStackV10_8:
    """Layer-pure facade around the v10.7 strategy agents."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._complexity_classifier = QueryComplexityClassifier(context, debug_mode)
        self._strategist = ToTStrategistAgent(context, debug_mode)

    async def classify_complexity_async(
        self, job_description: str, workflow_id: str
    ) -> str:
        """Delegate complexity classification to the v10.7 classifier."""

        return await self._complexity_classifier.run_async(job_description, workflow_id)

    async def plan_strategy_async(
        self,
        job_context: Dict[str, Any],
        workflow_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delegate strategy planning to the v10.7 Tree-of-Thought strategist."""

        return await self._strategist.run_async(job_context, workflow_id, state)
