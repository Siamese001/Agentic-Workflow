"""
Outreach-specific LLM caller with budget-aware model routing.

Provides intelligent model selection for outreach workflows based on stage,
archetype, and budget constraints using the ModelRoutingPolicy.
"""

from typing import Optional
from l1.outreach_dataclasses import ArchetypeType
from runtime.runtime_utils import invoke_model, SandboxConfig
from infra.model_routing.policies import ModelRoutingPolicy
from runtime.execution_budget_manager import ExecutionBudgetManager
from runtime.observability import record_event, record_exception


class OutreachLLMCaller:
    """Executes LLM calls with budget-aware routing for outreach workflows."""
    
    def __init__(
        self,
        routing_policy: ModelRoutingPolicy,
        sandbox: SandboxConfig,
        archetype: ArchetypeType,
        budget_manager: ExecutionBudgetManager
    ):
        """Initialize caller with routing policy, archetype, and budget manager."""
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.archetype = archetype
        self.budget_manager = budget_manager
    
    def call_llm(self, prompt: str, stage: str = "message_generation") -> str:
        """
        Execute LLM call with budget-aware model routing.
        
        Args:
            prompt: The prompt to send to the LLM
            stage: Workflow stage (message_generation, research, safety, etc.)
            
        Returns:
            Generated response from the selected model
        """
        record_event("outreach_llm_call_start", {"stage": stage, "archetype": self.archetype.value})
        
        try:
            # Select model based on stage, archetype, and budget
            model = self.routing_policy.select_model(
                stage=stage,
                archetype=self.archetype,
                budget_manager=self.budget_manager
            )
            
            record_event("outreach_model_selected", {
                "stage": stage,
                "archetype": self.archetype.value,
                "model": model
            })
            
            # Execute the LLM call
            result = invoke_model(model=model, prompt=prompt, sandbox=self.sandbox)
            
            record_event("outreach_llm_call_success", {
                "stage": stage,
                "archetype": self.archetype.value,
                "model": model
            })
            
            return result
            
        except Exception as exc:
            record_exception("outreach_llm_call_error", exc)
            raise
    
    def update_archetype(self, archetype: ArchetypeType) -> None:
        """Update the target archetype for subsequent calls."""
        self.archetype = archetype
        record_event("outreach_archetype_updated", {"archetype": archetype.value})
    
    def update_budget_manager(self, budget_manager: ExecutionBudgetManager) -> None:
        """Update the budget manager for subsequent calls."""
        self.budget_manager = budget_manager
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using message generation routing.
        
        Provides interface compatibility with MessageGenerationExecutor by
        calling call_llm with stage="message_generation".
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated response from the selected model
        """
        return self.call_llm(prompt=prompt, stage="message_generation")
