"""
Legacy agents wrapper for resume processing workflow execution.

Provides backward compatibility by delegating operations to atomic
L1-L5 architecture for resume enhancement and job alignment.
"""

from typing import Any, Optional, TYPE_CHECKING
from core.models.models import (
    AgentCard,
    AgentRole,
)
from core.routing import RoutingPolicy
from runtime.runtime_utils import SandboxConfig
from config.meta_profile import MetaProfileSnapshot

# Placeholder for missing record_event function
def record_event(event_name: str, data: dict) -> None:
    """Placeholder function for resume processing event recording."""
    pass

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from atomic_integration_bridge import (
        AtomicStrategyAgent,
        AtomicDraftingAgent,
        AtomicQAAgent,
        AtomicSafetyAgent,
    )

# Legacy agent classes that delegate to atomic layers
class StrategyLLMAgent:
    """
    Legacy strategy agent wrapper for resume processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive resume
    enhancement strategy execution and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Lazy import to avoid circular dependency
        from atomic_integration_bridge import AtomicStrategyAgent
        self._atomic_agent = AtomicStrategyAgent(routing_policy, sandbox, meta_profile)
    
    def __getattr__(self, name):
        """Delegates method calls to atomic resume processing agent."""
        return getattr(self._atomic_agent, name)

class DraftingGuild:
    """
    Legacy drafting agent wrapper for resume processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive resume
    content generation and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Lazy import to avoid circular dependency
        from atomic_integration_bridge import AtomicDraftingAgent
        self._atomic_agent = AtomicDraftingAgent(routing_policy, sandbox, meta_profile)
    
    def __getattr__(self, name):
        """Delegates method calls to atomic resume processing agent."""
        return getattr(self._atomic_agent, name)

class SemanticQAAgent:
    """
    Legacy QA agent wrapper for resume processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive resume
    quality assurance and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Lazy import to avoid circular dependency
        from atomic_integration_bridge import AtomicQAAgent
        self._atomic_agent = AtomicQAAgent(routing_policy, sandbox, meta_profile)
    
    def __getattr__(self, name):
        """Delegates method calls to atomic resume processing agent."""
        return getattr(self._atomic_agent, name)

class ConstitutionalSafetyAgent:
    """
    Legacy safety agent wrapper for resume processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive resume
    safety validation and job alignment compliance.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Lazy import to avoid circular dependency
        from atomic_integration_bridge import AtomicSafetyAgent
        self._atomic_agent = AtomicSafetyAgent(routing_policy, sandbox, meta_profile)
    
    def __getattr__(self, name):
        """Delegates method calls to atomic resume processing agent."""
        return getattr(self._atomic_agent, name)

class HYDEQueryAgent:
    """
    Legacy HYDE query agent for resume processing retrieval enhancement.

    Delegates to atomic L1-L5 layers for optimized resume
    search query generation and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    async def run_hyde_query(self, rag_plan: Any, ctx: Any) -> str:
        """
        Generates HYDE queries for resume processing retrieval enhancement.

        Delegates to atomic execution for optimized resume search
        query generation and job alignment.
        """
        # Delegate to L2 LLM caller for pure execution
        from l2.llm_caller import LLMCaller
        llm_caller = LLMCaller(self.routing_policy, self.sandbox)
        
        job = getattr(ctx, "job", None)
        resume = getattr(ctx, "resume", None)
        
        job_title = getattr(job, "title", "") if job else ""
        
        # Use L1 prompt builder for pure planning
        from l1.prompt_builder import PromptBuilder
        prompt = PromptBuilder.build_strategy_prompt(
            {"target_role": job_title, "reasoning": "HYDE query generation"},
            job,
            resume,
            {}
        )
        
        # Use L2 execution
        result = llm_caller.call_llm(prompt, "hyde_generation")
        return result.strip()

class QACouncilAgent:
    """
    Legacy QA council agent wrapper for resume processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive resume
    quality assurance with council oversight and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        # Lazy import to avoid circular dependency
        from atomic_integration_bridge import AtomicQAAgent
        self._atomic_agent = AtomicQAAgent(routing_policy, sandbox, meta_profile)
    
    def __getattr__(self, name):
        """Delegates method calls to atomic resume processing agent."""
        return getattr(self._atomic_agent, name)

# Legacy LLMBaseAgent for backward compatibility
class LLMBaseAgent:
    """
    Legacy base agent class for resume processing workflow compatibility.

    Delegates to atomic architecture for comprehensive resume
    enhancement operations and job alignment.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None, agent_card: Optional[AgentCard] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
        self.agent_card = agent_card or AgentCard(
            name="LegacyAgent",
            role=AgentRole.META,
            capabilities=["legacy_compatibility"],
            version="1.0.0",
            description="Legacy wrapper for atomic architecture",
        )
    
    def _call_llm(self, prompt: Any) -> str:
        """Legacy LLM call for resume processing - delegates to atomic L2."""
        from l2.llm_caller import LLMCaller
        llm_caller = LLMCaller(self.routing_policy, self.sandbox)
        return llm_caller.call_llm(prompt, self.agent_card.role.value)







