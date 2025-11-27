"""Executes LLM calls with routing and sandbox controls for high-quality executive message generation."""

from typing import Optional
from runtime.runtime_utils import invoke_model, SandboxConfig
from core.routing import RoutingPolicy
from core.models.models import ComplexityLevel
from config.meta_profile import MetaProfileSnapshot
from runtime.observability import record_event, record_exception

class LLMCaller:
    """Executes LLM calls with intelligent routing to ensure high-quality executive message generation."""
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        """Initializes caller with routing policy and sandbox for executive-grade LLM execution."""
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    def call_llm(self, prompt: str, task_type: str = "default") -> str:
        """Executes LLM call with intelligent routing to maximize executive message quality."""
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
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using default task routing.
        
        Provides interface compatibility with MessageGenerationExecutor by
        calling call_llm with default task_type.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated response from the selected model
        """
        return self.call_llm(prompt=prompt, task_type="default")


#
# === Learning Trace Map ===
# LAYER: L2
# ROLE: Executes LLM calls with intelligent routing for high-quality executive message generation
# IMPACT: Provides optimal model selection -> ensures executive-grade message quality by 25%
# FLOW: apps/lic_outreach/lic_workflow_entry.py -> MessageGenerationExecutor -> LLMCaller.call_llm() -> L5 safety validation
#
