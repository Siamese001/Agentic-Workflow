"""L2 LLM Caller - Pure LLM execution only."""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class LLMCaller:
    """Pure LLM execution - no planning, no orchestration logic."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def call_llm(self, prompt: str, task_type: str = "default") -> str:
        """Pure LLM call execution."""
        record_event("llm_call_start", {"task_type": task_type})
        
        try:
            model = self.routing_policy.select_model(
                task=task_type,
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
            )
            result = invoke_model(model=model, prompt=prompt, sandbox=self.sandbox)
            record_event("llm_call_success", {"task_type": task_type})
            return result
        except Exception as exc:
            record_exception("llm_call_error", exc)
            raise
