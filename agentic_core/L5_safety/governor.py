"""Cost Governor for tracking and limiting mission costs.

Tracks token usage and halts execution if cost exceeds threshold.
"""

import logging
import time
from typing import Dict, Optional

LOGGER = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when the cost budget is exceeded."""
    def __init__(self, message: str, current_spend: float = None, limit: float = None):
        super().__init__(message)
        self.current_spend = current_spend
        self.limit = limit


class CostGovernor:
    """Governor that tracks costs and enforces budget limits."""
    
    def __init__(self, limit_usd: float = 5.00):
        """Initialize the cost governor.
        
        Args:
            limit_usd: Maximum allowed cost in USD
        """
        self.limit = limit_usd
        self.spend = 0.0
        self.start_time = time.time()
        self.action_count = 0
        
        # Estimated cost per 1k tokens (input + output)
        self.rates = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
            "gemini-pro": 0.0005,
        }
        
        # Track usage by model
        self.usage_by_model: Dict[str, Dict[str, int]] = {}
        
        LOGGER.info(f"CostGovernor initialized with budget limit: ${limit_usd:.2f}")
    
    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track token usage and check budget.
        
        Args:
            model: Model name used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost of this interaction
            
        Raises:
            BudgetExceededError: If budget limit is exceeded
        """
        rate = self.rates.get(model, 0.01)  # Default rate for unknown models
        cost = ((input_tokens + output_tokens) / 1000) * rate
        
        # Update spend
        self.spend += cost
        self.action_count += 1
        
        # Track by model
        if model not in self.usage_by_model:
            self.usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        
        self.usage_by_model[model]["input_tokens"] += input_tokens
        self.usage_by_model[model]["output_tokens"] += output_tokens
        self.usage_by_model[model]["cost"] += cost
        
        # Check budget
        if self.spend > self.limit:
            LOGGER.warning(f"Budget exceeded! Current: ${self.spend:.2f}, Limit: ${self.limit:.2f}")
            raise BudgetExceededError(
                f"Budget limit ${self.limit:.2f} exceeded (Current: ${self.spend:.2f})",
                current_spend=self.spend,
                limit=self.limit
            )
        
        # Log warning at 80% of budget
        if self.spend > self.limit * 0.8:
            LOGGER.warning(f"Approaching budget limit: ${self.spend:.2f} / ${self.limit:.2f}")
        
        LOGGER.debug(f"Tracked cost: ${cost:.4f} for {model} (Total: ${self.spend:.2f})")
        return cost
    
    def check_action_cost(self, estimated_tokens: int, model: str = "gpt-3.5-turbo") -> bool:
        """Check if an estimated action would exceed budget.
        
        Args:
            estimated_tokens: Estimated tokens for the action
            model: Model to be used
            
        Returns:
            True if action is within budget, False otherwise
        """
        rate = self.rates.get(model, 0.01)
        estimated_cost = (estimated_tokens / 1000) * rate
        
        if self.spend + estimated_cost > self.limit:
            LOGGER.warning(f"Action would exceed budget: +${estimated_cost:.4f}")
            return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Get cost and usage statistics.
        
        Returns:
            Dictionary with cost statistics
        """
        runtime = time.time() - self.start_time
        
        return {
            "total_spend": self.spend,
            "budget_limit": self.limit,
            "budget_remaining": self.limit - self.spend,
            "budget_used_percent": (self.spend / self.limit) * 100,
            "total_actions": self.action_count,
            "runtime_seconds": runtime,
            "usage_by_model": self.usage_by_model,
            "average_cost_per_action": self.spend / max(self.action_count, 1)
        }
    
    def reset(self):
        """Reset the governor state."""
        self.spend = 0.0
        self.start_time = time.time()
        self.action_count = 0
        self.usage_by_model = {}
        LOGGER.info("CostGovernor reset")
    
    def set_limit(self, new_limit: float):
        """Update the budget limit.
        
        Args:
            new_limit: New budget limit in USD
        """
        old_limit = self.limit
        self.limit = new_limit
        LOGGER.info(f"Budget limit updated: ${old_limit:.2f} -> ${new_limit:.2f}")


def create_cost_governor(limit_usd: float = 5.00) -> CostGovernor:
    """Factory function to create cost governor instance.
    
    Args:
        limit_usd: Budget limit in USD
        
    Returns:
        CostGovernor instance
    """
    return CostGovernor(limit_usd)
