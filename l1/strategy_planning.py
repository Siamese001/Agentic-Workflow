"""L1 Strategy Planning - Pure reasoning only."""

from dataclasses import dataclass
from typing import Any, List

@dataclass
class StrategyPlan:
    """Pure strategy planning data structure."""
    target_role: str
    key_points: List[str]
    complexity: str
    reasoning: str

def plan_strategy(job: Any, resume: Any, config: Any) -> StrategyPlan:
    """Pure strategy planning function - no execution, no I/O."""
    return StrategyPlan(
        target_role="stub_role",
        key_points=["stub_point_1", "stub_point_2"],
        complexity="medium",
        reasoning="stub_reasoning"
    )
