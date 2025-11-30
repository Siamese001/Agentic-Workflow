"""Strategy Planning Module - Robust Implementation

Provides strategic planning capabilities for resume and outreach workflows.
This module re-exports robust implementations from the engine modules.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Core strategy planning classes
class StrategyType(str, Enum):
    """Strategy types for different workflow scenarios."""
    RESUME_OPTIMIZATION = "resume_optimization"
    OUTREACH_PERSONALIZED = "outreach_personalized"
    OUTREACH_BULK = "outreach_bulk"
    HYBRID_APPROACH = "hybrid_approach"

@dataclass
class StrategyConfig:
    """Configuration for strategy planning."""
    strategy_type: StrategyType
    reasoning_depth: int = 5
    enable_rag: bool = True
    safety_level: str = "standard"
    cost_budget_usd: float = 0.10
    latency_budget_ms: int = 3000
    custom_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}

class StrategyPlanner:
    """Robust strategy planning implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
    def plan_strategy(self, mission_type: str, context: Dict[str, Any]) -> StrategyConfig:
        """Plan strategy based on mission type and context."""
        if mission_type == "resume_generation":
            return StrategyConfig(
                strategy_type=StrategyType.RESUME_OPTIMIZATION,
                reasoning_depth=7,
                enable_rag=True,
                safety_level="strict"
            )
        elif mission_type == "personalized_outreach":
            return StrategyConfig(
                strategy_type=StrategyType.OUTREACH_PERSONALIZED,
                reasoning_depth=6,
                enable_rag=True,
                safety_level="standard"
            )
        elif mission_type == "bulk_outreach":
            return StrategyConfig(
                strategy_type=StrategyType.OUTREACH_BULK,
                reasoning_depth=3,
                enable_rag=False,
                cost_budget_usd=0.05,
                safety_level="relaxed"
            )
        else:
            return StrategyConfig(
                strategy_type=StrategyType.HYBRID_APPROACH,
                reasoning_depth=5,
                enable_rag=True
            )
    
    def validate_strategy(self, strategy: StrategyConfig) -> List[str]:
        """Validate strategy configuration."""
        issues = []
        if strategy.reasoning_depth < 1 or strategy.reasoning_depth > 10:
            issues.append("Reasoning depth must be between 1 and 10")
        if strategy.cost_budget_usd < 0:
            issues.append("Cost budget must be non-negative")
        if strategy.latency_budget_ms < 100:
            issues.append("Latency budget must be at least 100ms")
        return issues

# Global planner instance
_global_strategy_planner: Optional[StrategyPlanner] = None

def get_strategy_planner() -> StrategyPlanner:
    """Get the global strategy planner instance."""
    global _global_strategy_planner
    if _global_strategy_planner is None:
        _global_strategy_planner = StrategyPlanner()
    return _global_strategy_planner

def reset_strategy_planner() -> None:
    """Reset the global strategy planner instance (for testing)."""
    global _global_strategy_planner
    _global_strategy_planner = None

__all__ = [
    "StrategyType",
    "StrategyConfig", 
    "StrategyPlanner",
    "get_strategy_planner",
    "reset_strategy_planner",
]
