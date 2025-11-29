"""
Shared drafting tool for resume and outreach engines.

Generic drafting capability that can be used across engines
without violating separation of concerns.
"""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from runtime.core.routing import RoutingPolicy
from runtime.core.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception


class DraftExecutor:
    """
    Shared drafting tool for generating content across engines.
    
    Provides generic drafting functionality that can be used by both
    resume and outreach engines without cross-engine dependencies.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def execute_draft(self, prompt: str) -> str:
        """
        Generates draft content using optimal model selection.

        Creates tailored content that emphasizes relevant information
        for the specific context (resume or outreach).
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





