"""
L3 strategy orchestrator for resume job alignment workflows.

Coordinates strategy planning and execution for resume enhancement.
"""

from typing import Any
from l1.strategy_planning import plan_strategy
from l2.strategy_executor import StrategyExecutor
from runtime.observability import record_event

class StrategyOrchestrator:
    """Pure orchestration for resume strategy job alignment workflows."""
    
    def __init__(self, strategy_executor: StrategyExecutor):
        self.strategy_executor = strategy_executor
    
    def orchestrate_strategy(self, job: Any, resume: Any, config: Any) -> str:
        """Orchestrates resume strategy workflow for job alignment processing."""
        record_event("strategy_orchestration_start", {})
        
        # L1: Pure planning
        strategy_plan = plan_strategy(job, resume, config)
        
        # L2: Pure execution
        result = self.strategy_executor.execute_strategy(
            f"Execute strategy for: {strategy_plan.reasoning}"
        )
        
        record_event("strategy_orchestration_complete", {})
        return result
