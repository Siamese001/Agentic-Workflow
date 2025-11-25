"""L2 LLM Caller - Pure LLM execution only."""

from typing import Any
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from runtime.observability import record_event, record_exception

class LLMCaller:
    """Pure LLM execution - no planning, no orchestration logic."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
    
    def call_llm(self, prompt: str, task_type: str = "default") -> str:
        """Execute LLM call only - pure execution logic."""
        try:
            model = self.routing_policy.select_model(
                task=task_type,
                complexity="medium",
                meta_profile=None,
            )
            
            record_event("llm_call_start", {"task": task_type})
            
            result = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )
            
            record_event("llm_call_success", {"result_length": len(result)})
            return result
            
        except Exception as exc:
            record_exception("llm_call_failure", exc)
            raise
