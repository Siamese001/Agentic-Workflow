"""Cost Governor Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.cost_governor_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.cost_governor_util import (
    CostGovernor as _CostGovernor,
    track_cost as _track_cost,
    BudgetExceededError,
)


class CostGovernorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Cost Governor Agent - now delegates to cost_governor_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.cost_governor_util directly.
    """

    def __init__(self, budget_limit: float = 10.0):
        """Initialize CostGovernorAgent (deprecated, use cost_governor_util instead)."""
        super().__init__(name="CostGovernorAgent", layer="L5")

        warnings.warn(
            "CostGovernorAgent is deprecated. Use agentic_core.L5_safety.utils.cost_governor_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._governor = _CostGovernor(budget_limit=budget_limit)

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track LLM usage cost."""
        return self._governor.track(model, input_tokens, output_tokens)

    def get_total_cost(self) -> float:
        """Get total tracked cost."""
        return self._governor.get_total_cost()

    def is_budget_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self._governor.is_budget_exceeded()
