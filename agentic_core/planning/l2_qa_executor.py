"""
L2 quality assurance execution for résumé validation workflows.

Executes comprehensive QA analysis to ensure résumé accuracy and job alignment.
"""

from typing import Optional
from archives.legacy_root_folders.runtime.runtime_utils import invoke_model, SandboxConfig
from archives.legacy_root_folders.core.routing import RoutingPolicy
from archives.legacy_root_folders.core.models.models import ComplexityLevel
from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.meta_profile import MetaProfileSnapshot
from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.sandbox.test_sandbox_observability import record_event, record_exception

class QAExecutor:
    """
    Executes résumé quality assurance validation with optimal model selection.
    
    Ensures accuracy, relevance, and professional standards for comprehensive résumé improvement.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_qa(self, prompt: str) -> str:
        """
        Executes résumé quality assurance analysis using LLM models.
        
        Validates résumé content for accuracy, clarity, and job alignment effectiveness.
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
