"""L3 Strategy Orchestrator - Pure orchestration only."""

from typing import Any
from l1.strategy_planning import plan_strategy, StrategyPlan
from l2.strategy_executor import StrategyExecutor
from runtime.observability import record_event

class StrategyOrchestrator:
    """Pure orchestration - no planning, no execution logic."""
    
    def __init__(self, strategy_executor: StrategyExecutor):
        self.strategy_executor = strategy_executor
    
    def orchestrate_strategy(self, job: Any, resume: Any, config: Any) -> str:
        """Orchestrate strategy workflow - pure control flow only."""
        record_event("strategy_orchestration_start", {})
        
        # L1: Pure planning
        strategy_plan = plan_strategy(job, resume, config)
        
        # L2: Pure execution
        result = self.strategy_executor.execute_strategy(
            f"Execute strategy for: {strategy_plan.reasoning}"
        )
        
        record_event("strategy_orchestration_complete", {})
        return result
