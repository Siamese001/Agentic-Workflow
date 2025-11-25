"""L2 Safety Executor - Pure execution only."""

from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from runtime.observability import record_event, record_exception

class SafetyExecutor:
    """Pure safety execution - no planning logic."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
    
    def execute_safety(self, prompt: str) -> str:
        """Execute LLM call only - no planning, no orchestration."""
        try:
            model = self.routing_policy.select_model(
                task="safety_execution",
                complexity="medium",
                meta_profile=None,
            )
            
            record_event("safety_execution_start", {"task": "safety_execution"})
            
            result = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )
            
            record_event("safety_execution_success", {"result_length": len(result)})
            return result
            
        except Exception as exc:
            record_exception("safety_execution_failure", exc)
            raise
