"""
Agent Factory – L3 Orchestration Layer (Phase 9A & 11 – Dec 26, 2025)
Wires L1 Cognition agents with L2 Execution implementations via DIP.

DDD Compliance:
- L3 orchestrates the wiring between L1 and L2
- L1 never directly imports L2
- All dependencies injected at runtime

Phase 11: Configurable Implementation Factory
- Supports multiple implementation modes: real, mock, aggressive
- Enables zero-cost unit testing with mock implementations
- Allows runtime switching of agent behavior
"""
from typing import Optional, Any
from apps_shared.base_agents.canon_base_agent_interface import CanonBaseAgentInterface
from agentic_core.L2_execution.base_agents.canon_base_agent_impl import CanonBaseAgent
from agentic_core.L2_execution.base_agents.mock_canon_agent import MockCanonBaseAgent
from agentic_core.config.blueprint_sovereign.sovereign_config import config

# Import L1 Agent Classes
from agentic_core.L1_cognition.thought_engine.canon_agents_core import (
    SystemArchitect, HealerAgent, GenerativeGuard
)
from agentic_core.L1_cognition.thought_engine.canon_agents_syntax import (
    CodeJanitor, DependencySentinel
)
from agentic_core.L1_cognition.thought_engine.canon_agents_quality import SafetyInspector
from agentic_core.L1_cognition.thought_engine.canon_agents_pattern import PatternEnforcer


class AgentFactory:
    """
    Centralized factory for sovereign agent injection.
    
    Phase 9A DDD Compliance:
    - Only L3 knows how to instantiate L2 concrete implementations
    - L1 agents receive implementations via dependency injection
    - Maintains separation of concerns across layers
    """
    
    @staticmethod
    def _create_impl(ctx: Optional[Any] = None) -> CanonBaseAgentInterface:
        """
        Create base agent implementation with configurable mode support.
        
        Phase 11: Advanced Factory Pattern
        - Respects global AGENT_IMPLEMENTATION_MODE configuration
        - Supports "real" (standard), "mock" (testing), "aggressive" (fast-healing)
        - Only L3 knows how to instantiate the L2 concrete implementation
        
        Args:
            ctx: Optional context object to pass to the agent implementation
            
        Returns:
            CanonBaseAgentInterface: Concrete implementation based on configured mode
        """
        mode = config.AGENT_IMPLEMENTATION_MODE
        
        if mode == "mock":
            # Zero-cost mock for unit testing without LLM calls
            return MockCanonBaseAgent(ctx=ctx)
        
        elif mode == "aggressive":
            # Real implementation with aggressive healing enabled
            impl = CanonBaseAgent(ctx=ctx)
            # Custom L2 capability for fast recovery
            if hasattr(impl, "enable_aggressive_mode"):
                impl.enable_aggressive_mode()
            return impl
        
        # Default "real" mode - standard production implementation
        return CanonBaseAgent(ctx=ctx)
    
    @staticmethod
    def create_system_architect(ctx: Optional[Any] = None) -> SystemArchitect:
        """
        Create SystemArchitect with injected L2 implementation.
        Injects L2 execution capabilities into L1 strategic architecture reasoning.
        """
        return SystemArchitect(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_healer_agent(ctx: Optional[Any] = None) -> HealerAgent:
        """
        Create HealerAgent with injected L2 implementation.
        
        Injects L2 repair logic into L1 strategic healing.
        """
        return HealerAgent(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_generative_guard(ctx: Optional[Any] = None) -> GenerativeGuard:
        """
        Create GenerativeGuard with injected L2 implementation.
        
        Injects L2 validation capabilities into L1 generative oversight.
        """
        return GenerativeGuard(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_code_janitor(ctx: Optional[Any] = None) -> CodeJanitor:
        """
        Create CodeJanitor with injected L2 implementation.
        
        Injects L2 action into L1 syntax reasoning.
        """
        return CodeJanitor(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_dependency_sentinel(ctx: Optional[Any] = None) -> DependencySentinel:
        """
        Create DependencySentinel with injected L2 implementation.
        
        Injects L2 import management into L1 dependency reasoning.
        """
        return DependencySentinel(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_safety_inspector(ctx: Optional[Any] = None) -> SafetyInspector:
        """
        Create SafetyInspector with injected L2 implementation.
        
        Injects L2 security checks into L1 safety reasoning.
        """
        return SafetyInspector(AgentFactory._create_impl(ctx))
    
    @staticmethod
    def create_pattern_enforcer(ctx: Optional[Any] = None) -> PatternEnforcer:
        """
        Create PatternEnforcer with injected L2 implementation.
        
        Injects L2 pattern detection into L1 quality reasoning.
        """
        return PatternEnforcer(AgentFactory._create_impl(ctx))


# Convenience function for creating all agents at once
def create_all_agents(ctx: Optional[Any] = None) -> dict:
    """
    Create all L1 agents with injected L2 implementations.
    
    Args:
        ctx: Optional context object to pass to all agents
        
    Returns:
        dict: Dictionary of agent name to agent instance
    """
    return {
        "system_architect": AgentFactory.create_system_architect(ctx),
        "healer_agent": AgentFactory.create_healer_agent(ctx),
        "generative_guard": AgentFactory.create_generative_guard(ctx),
        "code_janitor": AgentFactory.create_code_janitor(ctx),
        "dependency_sentinel": AgentFactory.create_dependency_sentinel(ctx),
        "safety_inspector": AgentFactory.create_safety_inspector(ctx),
        "pattern_enforcer": AgentFactory.create_pattern_enforcer(ctx),
    }
