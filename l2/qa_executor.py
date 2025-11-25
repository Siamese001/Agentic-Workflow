"""L2 QA Executor - Pure execution only."""

from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from runtime.observability import record_event, record_exception

class QAExecutor:
    """Pure QA execution - no planning logic."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
    
    def execute_qa(self, prompt: str) -> str:
        """Execute LLM call only - no planning, no orchestration."""
        try:
            model = self.routing_policy.select_model(
                task="qa_execution",
                complexity="medium",
                meta_profile=None,
            )
            
            record_event("qa_execution_start", {"task": "qa_execution"})
            
            result = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )
            
            record_event("qa_execution_success", {"result_length": len(result)})
            return result
            
        except Exception as exc:
            record_exception("qa_execution_failure", exc)
            raise
