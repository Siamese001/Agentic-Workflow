#!/usr/bin/env python3
"""
Cost Tracker
Section 13: Agent Ops - Cost tracking for operations
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CostType(str, Enum):
    """Cost type enumeration"""
    API_CALL = "api_call"
    COMPUTATION = "computation"
    STORAGE = "storage"
    NETWORK = "network"

@dataclass
class OperationMetrics:
    """Operation metrics for cost tracking"""
    operation_id: str
    cost_type: CostType
    cost_amount: float
    currency: str = "USD"
    timestamp: str = ""

class CostTracker:
    """Tracks costs for agentic operations"""
    
    def __init__(self):
        self.metrics: List[OperationMetrics] = []
        self.total_cost: float = 0.0
    
    def track_cost(self, operation_id: str, cost_type: CostType, amount: float) -> None:
        """Track operation cost"""
        metric = OperationMetrics(
            operation_id=operation_id,
            cost_type=cost_type,
            cost_amount=amount
        )
        self.metrics.append(metric)
        self.total_cost += amount
    
    def get_total_cost(self) -> float:
        """Get total tracked cost"""
        return self.total_cost

# Re-export components
__all__ = [
    'CostTracker', 'OperationMetrics', 'CostType'
]
