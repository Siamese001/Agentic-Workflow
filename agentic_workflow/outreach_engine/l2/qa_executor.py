"""
L2 quality assurance execution for resume validation workflows.

Executes comprehensive QA analysis to ensure resume accuracy
and job alignment for better applications.
"""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class QAExecutor:
    """
    Executes resume quality assurance validation with optimal model selection.

    Ensures accuracy, relevance, and professional standards for comprehensive
    resume improvement and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_qa(self, prompt: str) -> str:
        """
        Executes resume quality assurance analysis using LLM models.

        Validates resume content for accuracy, clarity, and
        job alignment effectiveness for better applications.
        """
        try:
            model = self.routing_policy.select_model(
                task="qa_execution",
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
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
