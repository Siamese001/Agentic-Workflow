"""
L2 execution layer for resume draft generation.

Executes model calls to create compelling resume content
aligned with job requirements for better applications.
"""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class DraftExecutor:
    """
    Executes resume draft generation with optimal model selection.

    Ensures consistent quality and proper formatting for professional
    resume improvement and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_draft(self, prompt: str) -> str:
        """
        Generates resume draft content using optimal model.

        Creates tailored resume sections that emphasize relevant skills
        and accomplishments for better job alignment.
        """
        record_event("draft_execution_start", {})
        
        try:
            model = self.routing_policy.select_model(
                task="draft_generation",
                complexity=ComplexityLevel.MEDIUM,
                meta_profile=self.meta_profile,
            )
            result = invoke_model(model=model, prompt=prompt, sandbox=self.sandbox)
            record_event("draft_execution_success", {})
            return result
        except Exception as exc:
            record_exception("draft_execution_error", exc)
            raise
