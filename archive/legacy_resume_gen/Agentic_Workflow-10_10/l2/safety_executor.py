"""
L2 safety execution for résumé compliance and protection workflows.

Executes comprehensive safety validation to ensure résumé content meets security standards.
"""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class SafetyExecutor:
    """
    Executes résumé safety validation with optimal model selection.
    
    Protects user data and ensures compliance for reliable résumé processing workflows.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_safety(self, prompt: str) -> str:
        """
        Executes résumé safety validation using LLM models.
        
        Ensures content compliance and protection for secure résumé improvement processes.
        """
        try:
            model = self.routing_policy.select_model(
                task="safety_execution",
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
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
