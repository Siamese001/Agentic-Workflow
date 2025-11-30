"""
Cost and Performance Tracker Implementation

Provides comprehensive cost tracking and performance monitoring for
agentic workflows across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from collections import defaultdict
import json

from ..tracing.tracer import get_tracer, Span


class CostType(str, Enum):
    """Types of costs to track."""
    LLM_TOKENS = "llm_tokens"
    LLM_REQUESTS = "llm_requests"
    VECTOR_SEARCH = "vector_search"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"
    API_CALLS = "api_calls"


@dataclass
class CostRecord:
    """Individual cost tracking record."""
    operation_id: str
    operation_name: str
    cost_type: CostType
    amount: float
    currency: str = "USD"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_id": self.operation_id,
            "operation_name": self.operation_name,
            "cost_type": self.cost_type.value,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class CostBudget:
    """Budget configuration for cost control."""
    budget_id: str
    name: str
    total_budget: float
    period: str  # "daily", "weekly", "monthly"
    cost_type_limits: Dict[CostType, float] = field(default_factory=dict)
    alert_threshold: float = 0.8  # Alert when 80% of budget used
    current_spend: float = 0.0
    start_time: float = field(default_factory=time.time)
    
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        return self.current_spend > self.total_budget
    
    def get_usage_percentage(self) -> float:
        """Get current usage as percentage."""
        return (self.current_spend / self.total_budget) * 100 if self.total_budget > 0 else 0
    
    def should_alert(self) -> bool:
        """Check if should send alert."""
        return self.get_usage_percentage() >= (self.alert_threshold * 100)


class CostTracker:
    """Comprehensive cost tracking for agentic workflows."""
    
    def __init__(self, service_name: str = "agentic-workflow"):
        self.service_name = service_name
        self.records: List[CostRecord] = []
        self.budgets: Dict[str, CostBudget] = {}
        self.operation_costs: Dict[str, float] = defaultdict(float)
        self.cost_type_totals: Dict[CostType, float] = defaultdict(float)
        
        # Performance metrics
        self.operation_latencies: Dict[str, List[float]] = defaultdict(list)
        self.operation_success_rates: Dict[str, List[bool]] = defaultdict(list)
        
        # Cost calculation rates (USD per unit)
        self.cost_rates = {
            CostType.LLM_TOKENS: 0.00001,  # $0.00001 per token
            CostType.LLM_REQUESTS: 0.001,  # $0.001 per request
            CostType.VECTOR_SEARCH: 0.0001,  # $0.0001 per search
            CostType.STORAGE: 0.0000001,  # $0.0000001 per byte
            CostType.COMPUTE: 0.0001,  # $0.0001 per second
            CostType.NETWORK: 0.00001,  # $0.00001 per byte
            CostType.API_CALLS: 0.01,  # $0.01 per API call
        }
    
    def set_cost_rate(self, cost_type: CostType, rate: float) -> None:
        """Set cost rate for a specific cost type."""
        self.cost_rates[cost_type] = rate
    
    def track_cost(self, operation: str, cost_type: CostType, amount: float, 
                   metadata: Optional[Dict[str, Any]] = None, 
                   operation_id: Optional[str] = None) -> CostRecord:
        """Track a cost record."""
        if operation_id is None:
            operation_id = f"{operation}_{int(time.time() * 1000)}"
        
        # Get current trace context
        tracer = get_tracer()
        current_span = tracer.get_current_span()
        
        record = CostRecord(
            operation_id=operation_id,
            operation_name=operation,
            cost_type=cost_type,
            amount=amount,
            metadata=metadata or {},
            trace_id=current_span.trace_id if current_span else None,
            span_id=current_span.span_id if current_span else None,
        )
        
        self.records.append(record)
        self.operation_costs[operation] += amount
        self.cost_type_totals[cost_type] += amount
        
        # Update budgets
        for budget in self.budgets.values():
            if cost_type in budget.cost_type_limits or budget.cost_type_limits == {}:
                budget.current_spend += amount
        
        return record
    
    def track_llm_cost(self, operation: str, input_tokens: int, output_tokens: int,
                      model: str = "default", metadata: Optional[Dict[str, Any]] = None) -> CostRecord:
        """Track LLM usage cost."""
        total_tokens = input_tokens + output_tokens
        cost = total_tokens * self.cost_rates[CostType.LLM_TOKENS]
        
        enhanced_metadata = {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }
        if metadata:
            enhanced_metadata.update(metadata)
        
        return self.track_cost(
            operation=operation,
            cost_type=CostType.LLM_TOKENS,
            amount=cost,
            metadata=enhanced_metadata,
        )
    
    def track_vector_search_cost(self, operation: str, search_count: int,
                                vector_dimension: int, metadata: Optional[Dict[str, Any]] = None) -> CostRecord:
        """Track vector search cost."""
        cost = search_count * vector_dimension * self.cost_rates[CostType.VECTOR_SEARCH]
        
        enhanced_metadata = {
            "search_count": search_count,
            "vector_dimension": vector_dimension,
        }
        if metadata:
            enhanced_metadata.update(metadata)
        
        return self.track_cost(
            operation=operation,
            cost_type=CostType.VECTOR_SEARCH,
            amount=cost,
            metadata=enhanced_metadata,
        )
    
    def track_performance(self, operation: str, latency_ms: float, success: bool) -> None:
        """Track performance metrics."""
        self.operation_latencies[operation].append(latency_ms)
        self.operation_success_rates[operation].append(success)
    
    def create_budget(self, budget_id: str, name: str, total_budget: float, period: str,
                     cost_type_limits: Optional[Dict[CostType, float]] = None,
                     alert_threshold: float = 0.8) -> CostBudget:
        """Create a new cost budget."""
        budget = CostBudget(
            budget_id=budget_id,
            name=name,
            total_budget=total_budget,
            period=period,
            cost_type_limits=cost_type_limits or {},
            alert_threshold=alert_threshold,
        )
        self.budgets[budget_id] = budget
        return budget
    
    def get_operation_cost(self, operation: str) -> float:
        """Get total cost for an operation."""
        return self.operation_costs.get(operation, 0.0)
    
    def get_cost_type_total(self, cost_type: CostType) -> float:
        """Get total cost for a cost type."""
        return self.cost_type_totals.get(cost_type, 0.0)
    
    def get_total_cost(self) -> float:
        """Get total cost across all operations."""
        return sum(self.cost_type_totals.values())
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by type."""
        return {cost_type.value: total for cost_type, total in self.cost_type_totals.items()}
    
    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for an operation."""
        latencies = self.operation_latencies.get(operation, [])
        success_rates = self.operation_success_rates.get(operation, [])
        
        if not latencies:
            return {}
        
        return {
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "success_rate": sum(success_rates) / len(success_rates) if success_rates else 0.0,
            "total_operations": len(latencies),
        }
    
    def get_budget_status(self, budget_id: str) -> Dict[str, Any]:
        """Get budget status."""
        budget = self.budgets.get(budget_id)
        if not budget:
            return {"error": "Budget not found"}
        
        return {
            "budget_id": budget.budget_id,
            "name": budget.name,
            "total_budget": budget.total_budget,
            "current_spend": budget.current_spend,
            "remaining": budget.total_budget - budget.current_spend,
            "usage_percentage": budget.get_usage_percentage(),
            "is_exceeded": budget.is_exceeded(),
            "should_alert": budget.should_alert(),
        }
    
    def get_cost_projection(self, days: int = 7) -> Dict[str, float]:
        """Project costs for the next N days based on current usage."""
        if not self.records:
            return {"projected_daily_cost": 0.0, "projected_total_cost": 0.0}
        
        # Calculate daily average from last 24 hours
        now = time.time()
        day_ago = now - 86400
        recent_records = [r for r in self.records if r.timestamp >= day_ago]
        
        if not recent_records:
            return {"projected_daily_cost": 0.0, "projected_total_cost": 0.0}
        
        daily_cost = sum(r.amount for r in recent_records)
        projected_total = daily_cost * days
        
        return {
            "projected_daily_cost": daily_cost,
            "projected_total_cost": projected_total,
            "projection_days": days,
        }
    
    def export_costs(self, format: str = "json") -> str:
        """Export cost records in specified format."""
        if format.lower() == "json":
            return json.dumps([record.to_dict() for record in self.records], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset_costs(self) -> None:
        """Reset all cost tracking data."""
        self.records.clear()
        self.operation_costs.clear()
        self.cost_type_totals.clear()
        self.operation_latencies.clear()
        self.operation_success_rates.clear()
        
        # Reset budgets
        for budget in self.budgets.values():
            budget.current_spend = 0.0
            budget.start_time = time.time()
    
    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get comprehensive summary metrics."""
        return {
            "total_cost": self.get_total_cost(),
            "total_operations": len(self.operation_costs),
            "cost_breakdown": self.get_cost_breakdown(),
            "active_budgets": len(self.budgets),
            "exceeded_budgets": len([b for b in self.budgets.values() if b.is_exceeded()]),
            "alerting_budgets": len([b for b in self.budgets.values() if b.should_alert()]),
            "cost_projection": self.get_cost_projection(),
            "total_records": len(self.records),
        }


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


def init_cost_tracker(service_name: str) -> CostTracker:
    """Initialize the global cost tracker."""
    global _cost_tracker
    _cost_tracker = CostTracker(service_name=service_name)
    return _cost_tracker


# Convenience functions
def track_cost(operation: str, cost_type: CostType, amount: float, 
               metadata: Optional[Dict[str, Any]] = None) -> CostRecord:
    """Track cost using global tracker."""
    return get_cost_tracker().track_cost(operation, cost_type, amount, metadata)


def track_llm_cost(operation: str, input_tokens: int, output_tokens: int,
                   model: str = "default", metadata: Optional[Dict[str, Any]] = None) -> CostRecord:
    """Track LLM cost using global tracker."""
    return get_cost_tracker().track_llm_cost(operation, input_tokens, output_tokens, model, metadata)


__all__ = [
    "CostTracker",
    "CostRecord",
    "CostBudget",
    "CostType",
    "get_cost_tracker",
    "init_cost_tracker",
    "track_cost",
    "track_llm_cost",
]
