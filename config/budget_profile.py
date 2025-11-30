"""
Budget Profile Configuration

Defines budget and cost management parameters for agentic operations
across the L1-L5 architecture.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class BudgetType(str, Enum):
    """Budget enforcement types."""
    TIME_BASED = "time_based"
    TOKEN_BASED = "token_based"
    COST_BASED = "cost_based"
    UNLIMITED = "unlimited"


@dataclass
class BudgetProfile:
    """Configuration for budget parameters."""
    name: str
    budget_type: BudgetType = BudgetType.TOKEN_BASED
    max_tokens: int = 100000
    max_cost_usd: float = 10.0
    max_execution_time_seconds: int = 300
    cost_per_token: float = 0.0001
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    warning_threshold: float = 0.8
    hard_limit_threshold: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

        # Set defaults based on budget type
        if self.budget_type == BudgetType.UNLIMITED:
            self.max_tokens = float('inf')
            self.max_cost_usd = float('inf')
            self.max_execution_time_seconds = float('inf')
        elif self.budget_type == BudgetType.TIME_BASED:
            self.max_tokens = 50000  # Conservative token limit for time-based
        elif self.budget_type == BudgetType.COST_BASED:
            self.max_tokens = int(self.max_cost_usd / self.cost_per_token)

    def is_within_budget(self, current_usage: Dict[str, float]) -> bool:
        """Check if current usage is within budget limits."""
        if self.budget_type == BudgetType.UNLIMITED:
            return True

        tokens_used = current_usage.get('tokens', 0)
        cost_incurred = current_usage.get('cost', 0.0)
        time_elapsed = current_usage.get('time', 0)

        return (tokens_used <= self.max_tokens and
                cost_incurred <= self.max_cost_usd and
                time_elapsed <= self.max_execution_time_seconds)

    def get_warning_threshold_reached(self, current_usage: Dict[str, float]) -> bool:
        """Check if usage has reached warning threshold."""
        if self.budget_type == BudgetType.UNLIMITED:
            return False

        tokens_used = current_usage.get('tokens', 0)
        cost_incurred = current_usage.get('cost', 0.0)
        time_elapsed = current_usage.get('time', 0)

        token_ratio = tokens_used / max(self.max_tokens, 1)
        cost_ratio = cost_incurred / max(self.max_cost_usd, 1)
        time_ratio = time_elapsed / max(self.max_execution_time_seconds, 1)

        max_ratio = max(token_ratio, cost_ratio, time_ratio)
        return max_ratio >= self.warning_threshold


# Default budget profiles
DEFAULT_BUDGET_PROFILE = BudgetProfile(
    name="default",
    budget_type=BudgetType.TOKEN_BASED,
    max_tokens=100000,
    max_cost_usd=10.0
)

STRICT_BUDGET_PROFILE = BudgetProfile(
    name="strict",
    budget_type=BudgetType.COST_BASED,
    max_cost_usd=5.0,
    warning_threshold=0.7
)

UNLIMITED_BUDGET_PROFILE = BudgetProfile(
    name="unlimited",
    budget_type=BudgetType.UNLIMITED
)

__all__ = [
    "BudgetProfile",
    "BudgetType",
    "DEFAULT_BUDGET_PROFILE",
    "STRICT_BUDGET_PROFILE",
    "UNLIMITED_BUDGET_PROFILE",
]
