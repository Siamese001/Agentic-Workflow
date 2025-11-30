# execution_budget_manager - Runtime execution budget management
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class BudgetLimits:
    """Budget limit configuration"""
    max_tokens: int = 1000
    max_cost: float = 1.0
    max_execution_time: float = 30.0
    
    def __post_init__(self):
        if self.max_tokens <= 0:
            self.max_tokens = 1000
        if self.max_cost <= 0:
            self.max_cost = 1.0
        if self.max_execution_time <= 0:
            self.max_execution_time = 30.0

@dataclass
class BudgetUsage:
    """Current budget usage tracking"""
    tokens_used: int = 0
    cost_incurred: float = 0.0
    execution_time: float = 0.0
    
    def reset(self) -> None:
        """Reset all usage counters"""
        self.tokens_used = 0
        self.cost_incurred = 0.0
        self.execution_time = 0.0

class ExecutionBudgetManager:
    """Manages execution budgets for operations"""
    
    def __init__(self, limits: Optional[BudgetLimits] = None):
        self.limits = limits or BudgetLimits()
        self.usage = BudgetUsage()
        self.enabled = True
    
    def check_budget(self, tokens_required: int = 0, estimated_cost: float = 0.0, estimated_time: float = 0.0) -> bool:
        """Check if operation fits within remaining budget"""
        if not self.enabled:
            return True
        
        remaining_tokens = self.limits.max_tokens - self.usage.tokens_used
        remaining_cost = self.limits.max_cost - self.usage.cost_incurred
        remaining_time = self.limits.max_execution_time - self.usage.execution_time
        
        return (
            tokens_required <= remaining_tokens and
            estimated_cost <= remaining_cost and
            estimated_time <= remaining_time
        )
    
    def consume_budget(self, tokens: int = 0, cost: float = 0.0, time: float = 0.0) -> bool:
        """Consume budget for operation"""
        if not self.check_budget(tokens, cost, time):
            return False
        
        self.usage.tokens_used += tokens
        self.usage.cost_incurred += cost
        self.usage.execution_time += time
        return True
    
    def get_remaining_budget(self) -> Dict[str, float]:
        """Get remaining budget amounts"""
        return {
            "tokens": self.limits.max_tokens - self.usage.tokens_used,
            "cost": self.limits.max_cost - self.usage.cost_incurred,
            "time": self.limits.max_execution_time - self.usage.execution_time
        }
    
    def reset_budget(self) -> None:
        """Reset budget usage"""
        self.usage.reset()
    
    def enable(self) -> None:
        """Enable budget enforcement"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable budget enforcement"""
        self.enabled = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get budget manager status"""
        return {
            "enabled": self.enabled,
            "limits": {
                "max_tokens": self.limits.max_tokens,
                "max_cost": self.limits.max_cost,
                "max_execution_time": self.limits.max_execution_time
            },
            "usage": {
                "tokens_used": self.usage.tokens_used,
                "cost_incurred": self.usage.cost_incurred,
                "execution_time": self.usage.execution_time
            },
            "remaining": self.get_remaining_budget()
        }

# Global budget manager instance
_global_budget_manager: Optional[ExecutionBudgetManager] = None

def get_budget_manager() -> ExecutionBudgetManager:
    """Get the global budget manager instance"""
    global _global_budget_manager
    if _global_budget_manager is None:
        _global_budget_manager = ExecutionBudgetManager()
    return _global_budget_manager

def reset_budget_manager() -> None:
    """Reset the global budget manager (for testing)"""
    global _global_budget_manager
    _global_budget_manager = None
