"""Compute Budget Manager.

Token and compute budget allocation for cost-aware retrieval decisions.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class BudgetResult:
    """Result of budget allocation."""
    allowed_tokens: int
    estimated_cost: float
    remaining_budget: int
    budget_exceeded: bool
    recommendations: list = field(default_factory=list)


class ComputeBudgetManager:
    """Manages compute budgets for retrieval operations.

    The ComputeBudgetManager tracks token usage and makes cost-aware
    decisions to optimize resource utilization.
    """

    def __init__(
        self,
        daily_budget: int = 100000,  # tokens per day
        query_budget_limit: int = 5000,  # max per query
    ):
        """Initialize the compute budget manager.

        Args:
            daily_budget: Total daily token budget
            query_budget_limit: Maximum tokens per single query
        """
        self.daily_budget = daily_budget
        self.query_budget_limit = query_budget_limit
        self._used_today = 0

        log.info(f"ComputeBudgetManager initialized (daily={daily_budget})")

    def allocate_budget(
        self,
        query_id: str,
        requested_tokens: int,
        priority: int = 5,
    ) -> BudgetResult:
        """Allocate budget for a query.

        Args:
            query_id: Query identifier
            requested_tokens: Tokens requested
            priority: Priority level (1-10)

        Returns:
            BudgetResult with allocation decision
        """
        trace_id = f"budget_{query_id}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "ComputeBudgetManager.allocate_budget"
        )

        # Check remaining budget
        remaining = self.daily_budget - self._used_today

        # Adjust by priority
        priority_multiplier = priority / 5.0
        adjusted_request = int(requested_tokens * priority_multiplier)

        # Check limits
        if adjusted_request > self.query_budget_limit:
            allowed = self.query_budget_limit
            recommendations = ["Reduce query complexity", "Split into sub-queries"]
        elif adjusted_request > remaining:
            allowed = remaining
            recommendations = ["Budget nearly exhausted", "Defer non-urgent queries"]
        else:
            allowed = adjusted_request
            recommendations = []

        # Calculate cost (simplified: $0.002 per 1K tokens)
        estimated_cost = (allowed / 1000) * 0.002

        result = BudgetResult(
            allowed_tokens=allowed,
            estimated_cost=estimated_cost,
            remaining_budget=remaining - allowed,
            budget_exceeded=allowed < requested_tokens,
            recommendations=recommendations,
        )

        # Track usage
        self._used_today += allowed

        log.debug(f"Allocated {allowed} tokens for {query_id}")
        return result

    def get_budget_status(self) -> dict[str, Any]:
        """Get current budget status.

        Returns:
            Dictionary with budget statistics
        """
        return {
            "daily_budget": self.daily_budget,
            "used_today": self._used_today,
            "remaining": self.daily_budget - self._used_today,
            "utilization": self._used_today / self.daily_budget if self.daily_budget > 0 else 0,
        }

    def reset_daily_budget(self) -> None:
        """Reset the daily usage counter."""
        self._used_today = 0
        log.info("Daily budget reset")


# Global instance
_global_budget_manager: ComputeBudgetManager | None = None


def get_compute_budget_manager() -> ComputeBudgetManager:
    """Get or create the global compute budget manager."""
    global _global_budget_manager
    if _global_budget_manager is None:
        _global_budget_manager = ComputeBudgetManager()
    return _global_budget_manager


def allocate_query_budget(
    query_id: str,
    requested_tokens: int,
    priority: int = 5,
) -> BudgetResult:
    """Convenience function to allocate budget."""
    return get_compute_budget_manager().allocate_budget(query_id, requested_tokens, priority)
