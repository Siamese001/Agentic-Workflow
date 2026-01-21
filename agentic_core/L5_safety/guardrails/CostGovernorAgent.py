"""Cost Governor Agent - L5 Safety financial guardrail for LLM spend tracking.

This module provides a financial guardrail agent that tracks and limits
spending across LLM models and tools. It enforces budget constraints
and raises exceptions when limits are exceeded.

Typical usage:
    agent = CostGovernorAgent(config={"budget_limit": 10.0})
    cost = agent.track(model="gpt-4", input_tokens=100, output_tokens=50)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


class BudgetExceededError(Exception):
    """Raised when LLM spending exceeds the configured budget limit."""

    pass


@dataclass
class CostGovernorAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """L5 Safety agent that tracks and limits LLM spend across models and tools.

    This financial guardrail monitors API costs and enforces budget constraints.
    It calculates costs based on token usage and raises BudgetExceededError
    when the configured limit is exceeded.

    Attributes:
        config: Configuration dictionary with budget settings.
        limit: Maximum allowed spend in dollars.
        spend: Current accumulated spend in dollars.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the cost governor with budget configuration.

        Args:
            config: Configuration dictionary containing:
                - budget_limit: Maximum allowed spend in dollars (default: 10.0)
        """
        self.config: dict[str, Any] = config
        self.limit: float = config.get("budget_limit", 10.0)
        self.spend: float = 0.0

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate and record the cost of an LLM call.

        Args:
            model: Name of the LLM model used.
            input_tokens: Number of input tokens in the request.
            output_tokens: Number of output tokens in the response.

        Returns:
            Cost of this call in dollars.

        Raises:
            BudgetExceededError: If total spend exceeds the configured limit.
        """
        cost: float = (input_tokens + output_tokens) * 2e-05
        self.spend += cost
        logging.info(f"Governor: Current Spend ${self.spend:.4f} / Limit ${self.limit:.2f}")
        if self.spend > self.limit:
            raise BudgetExceededError(
                f"BUDGET EXCEEDED: ${self.spend:.2f} exceeds limit of ${self.limit:.2f}"
            )
        return cost

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
