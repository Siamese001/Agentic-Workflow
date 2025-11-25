"""L2 Strategy Executor - Pure execution only."""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class StrategyExecutor:
    """Pure strategy execution - no planning logic."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_strategy(self, prompt: str) -> str:
        """Execute LLM call only - no planning, no orchestration."""
        try:
            model = self.routing_policy.select_model(
                task="strategy_execution",
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
            )
            
            record_event("strategy_execution_start", {"task": "strategy_execution"})
            
            result = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )
            
            record_event("strategy_execution_success", {"result_length": len(result)})
            return result
            
        except Exception as exc:
            record_exception("strategy_execution_failure", exc)
            raise
