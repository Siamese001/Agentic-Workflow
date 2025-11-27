"""
Outreach Factory - Phase 10 Model Routing Integration

Factory functions for creating outreach components with conditional model routing
based on configuration settings.
"""

from typing import Optional, Any
from l1.outreach_archetype_planning import OutreachArchetypePlanner
from l1.research_planning import ResearchRefinementPlanner
from l1.message_planning import MessagePlanner
from l1.outreach_dataclasses import ArchetypeType
from l2.company_research_executor import CompanyResearchExecutor
from l2.contact_research_executor import ContactResearchExecutor
from l2.message_generation_executor import MessageGenerationExecutor
from l2.outreach_llm_caller import OutreachLLMCaller
from infra.model_routing.policies import ModelRoutingPolicy
from runtime.execution_budget_manager import get_budget_manager
from runtime.runtime_utils import SandboxConfig
from l5.safety_validator import SafetyValidator
from config.LIC.lic_profile import get_lic_profile


def create_message_executor_with_routing(
    archetype: ArchetypeType = ArchetypeType.C_LEVEL,
    safety_validator: Optional[SafetyValidator] = None,
    budget_manager: Optional[Any] = None
) -> MessageGenerationExecutor:
    """
    Create MessageGenerationExecutor with conditional model routing.
    
    Args:
        archetype: Target archetype for routing decisions
        safety_validator: Optional safety validator
        budget_manager: Optional budget manager for routing
        
    Returns:
        MessageGenerationExecutor configured with or without routing
    """
    # Get configuration
    lic_profile = get_lic_profile()
    
    # Initialize budget manager
    budget_manager = budget_manager or get_budget_manager()
    
    # Always use OutreachLLMCaller but vary the routing behavior
    sandbox_config = SandboxConfig()
    
    if lic_profile.use_model_routing:
        # Create with full routing enabled (ModelRoutingPolicy with archetype + budget awareness)
        routing_policy = ModelRoutingPolicy()
        
        routed_caller = OutreachLLMCaller(
            routing_policy=routing_policy,
            sandbox=sandbox_config,
            archetype=archetype,
            budget_manager=budget_manager
        )
        
        return MessageGenerationExecutor(
            llm_client=routed_caller,
            safety_validator=safety_validator
        )
    else:
        # Create with basic routing (ModelRoutingPolicy but without budget constraints)
        # Use a simple routing policy that ignores budget for backward compatibility
        basic_routing_policy = ModelRoutingPolicy()
        
        standard_caller = OutreachLLMCaller(
            routing_policy=basic_routing_policy,
            sandbox=sandbox_config,
            archetype=archetype,
            budget_manager=budget_manager
        )
        
        return MessageGenerationExecutor(
            llm_client=standard_caller,
            safety_validator=safety_validator
        )


def create_outreach_orchestrator_with_routing(
    archetype_planner: OutreachArchetypePlanner,
    research_planner: ResearchRefinementPlanner,
    message_planner: MessagePlanner,
    company_executor: CompanyResearchExecutor,
    contact_executor: ContactResearchExecutor,
    state_manager: Any,
    safety_validator: SafetyValidator,
    budget_manager: Optional[Any] = None,
    archetype: ArchetypeType = ArchetypeType.C_LEVEL
) -> Any:  # Returns OutreachOrchestrator instance
    """
    Create OutreachOrchestrator with conditional routing in message executor.
    
    Args:
        archetype_planner: L1 archetype planner
        research_planner: L1 research planner
        message_planner: L1 message planner
        company_executor: L2 company research executor
        contact_executor: L2 contact research executor
        state_manager: State manager instance
        safety_validator: L5 safety validator
        budget_manager: Optional budget manager
        archetype: Target archetype for routing
        
    Returns:
        OutreachOrchestrator with message executor configured based on routing flag
    """
    from l3.outreach_orchestrator import OutreachOrchestrator
    
    # Create message executor with conditional routing
    message_executor = create_message_executor_with_routing(
        archetype=archetype,
        safety_validator=safety_validator,
        budget_manager=budget_manager
    )
    
    # Create orchestrator with the configured message executor
    return OutreachOrchestrator(
        archetype_planner=archetype_planner,
        research_planner=research_planner,
        message_planner=message_planner,
        company_executor=company_executor,
        contact_executor=contact_executor,
        message_executor=message_executor,
        state_manager=state_manager,
        safety_validator=safety_validator,
        budget_manager=budget_manager
    )
