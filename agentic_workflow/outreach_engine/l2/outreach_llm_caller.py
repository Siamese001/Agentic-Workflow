"""
Outreach-specific LLM caller with budget-aware model routing.

Provides intelligent model selection for outreach workflows based on stage,
archetype, and budget constraints using the ModelRoutingPolicy.
"""

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
            selected_model = self.routing_policy.select_model(
                stage=stage,
                archetype=self.archetype,
                budget_manager=self.budget_manager
            )
            
            # Determine routing reason for telemetry
            if stage == "safety":
                routing_reason = "safety_invariance_heavy_model"
            else:
                # Check budget state to determine reason
                try:
                    usage = self.budget_manager.current_usage()
                    tokens_remaining = usage.get("tokens_remaining", 0)
                    tokens_used = usage.get("tokens_used", 0)
                    tokens_total = tokens_remaining + tokens_used
                    
                    if tokens_total == 0:
                        routing_reason = "archetype_based_selection"
                    else:
                        remaining_percentage = tokens_remaining / tokens_total
                        if remaining_percentage < 0.2:
                            routing_reason = "budget_constraint_light_model"
                        elif remaining_percentage < 0.5:
                            routing_reason = "budget_constraint_downgraded_model"
                        else:
                            routing_reason = "archetype_based_selection"
                except Exception:
                    routing_reason = "fallback_selection"
            
            # Emit telemetry with required fields
            record_event("outreach_model_selected", {
                "stage": stage,
                "archetype": self.archetype.value,
                "selected_model": selected_model,
                "routing_reason": routing_reason
            })
            
            # Execute the LLM call
            result = invoke_model(model=selected_model, prompt=prompt, sandbox=self.sandbox)
            
            record_event("outreach_llm_call_success", {
                "stage": stage,
                "archetype": self.archetype.value,
                "selected_model": selected_model,
                "routing_reason": routing_reason
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
