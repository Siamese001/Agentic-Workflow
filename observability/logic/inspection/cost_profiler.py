"""
Cost profiler for observability.
Auto-hardened by WINDSURF v2
"""
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CostMetrics:
    """Cost metrics for operations."""
    operation: str
    cost: float
    tokens_used: int
    duration_ms: float
    timestamp: datetime

class CostProfiler:
    """Profiles and tracks costs for LLM operations."""
    
    def __init__(self):
        self.metrics: List[CostMetrics] = []
        self.cost_per_token = {
            'gpt-4': 0.00003,
            'gpt-3.5-turbo': 0.000002,
            'claude-3': 0.000015,
        }
    
    def track_operation(self, operation: str, model: str, tokens: int, duration: float) -> CostMetrics:
        """Track a cost operation."""
        cost = self.calculate_cost(model, tokens)
        metric = CostMetrics(
            operation=operation,
            cost=cost,
            tokens_used=tokens,
            duration_ms=duration * 1000,
            timestamp=datetime.now()
        )
        self.metrics.append(metric)
        logger.info(f"Tracked {operation}: ${cost:.6f} for {tokens} tokens")
        return metric
    
    def calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost based on model and tokens."""
        cost_per_token = self.cost_per_token.get(model, 0.00001)
        return tokens * cost_per_token
    
    def get_total_cost(self) -> float:
        """Get total cost across all operations."""
        return sum(m.cost for m in self.metrics)
    
    def get_cost_by_operation(self) -> Dict[str, float]:
        """Get costs grouped by operation type."""
        costs = {}
        for metric in self.metrics:
            costs[metric.operation] = costs.get(metric.operation, 0) + metric.cost
        return costs
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary statistics."""
        if not self.metrics:
            return {}
        
        return {
            'total_cost': self.get_total_cost(),
            'total_tokens': sum(m.tokens_used for m in self.metrics),
            'operation_costs': self.get_cost_by_operation(),
            'operation_count': len(self.metrics),
            'average_cost_per_operation': self.get_total_cost() / len(self.metrics)
        }
