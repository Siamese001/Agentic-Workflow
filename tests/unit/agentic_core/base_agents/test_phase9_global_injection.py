"""
Phase 9 Global Injection Verification Tests
Ensures SovereignBaseAgent natively possesses all Phase 4-6 capabilities.
"""

from dataclasses import dataclass


def test_global_injection_capabilities():
    """Verify SovereignBaseAgent natively possesses all Phase 4-6 capabilities."""
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.config.SovereignConfigManager import SovereignConfigManager

    @dataclass
    class ConcreteAgent(SovereignBaseAgent):
        def execute(self):
            pass

    agent = ConcreteAgent()

    # 1. Check ConfigMixin
    assert hasattr(agent, "config"), "Agent missing config property"
    assert isinstance(agent.config, SovereignConfigManager), (
        "config should be SovereignConfigManager"
    )

    # 2. Check LLMProviderMixin
    assert hasattr(agent, "llm_generate"), "Agent missing llm_generate method"
    assert hasattr(agent, "llm_gateway"), "Agent missing llm_gateway property"

    # 3. Check EmbeddingMixin
    assert hasattr(agent, "get_embedding"), "Agent missing get_embedding method"

    # 4. Check HealingStrategyMixin
    assert hasattr(agent, "orchestrator_heal"), "Agent missing orchestrator_heal method"

    # 5. Check ValidatorMixin
    assert hasattr(agent, "orchestrator_validate"), "Agent missing orchestrator_validate method"


def test_no_circular_imports():
    """Verify that importing BaseAgent doesn't crash due to Gateway cycles."""
    # Import in specific order to test for circular dependencies
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

    # If we got here, imports worked.
    assert SovereignLLMGateway is not None
    assert SovereignBaseAgent is not None


def test_mixin_resolution():
    """Verify methods resolve to correct mixins."""
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    # Check inheritance
    assert issubclass(SovereignBaseAgent, LLMProviderMixin), (
        "SovereignBaseAgent must inherit LLMProviderMixin"
    )
    assert issubclass(SovereignBaseAgent, ConfigMixin), (
        "SovereignBaseAgent must inherit ConfigMixin"
    )


def test_sovereign_initialization():
    """Verify sovereign agent initializes correctly with all mixins."""
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    @dataclass
    class TestAgent(SovereignBaseAgent):
        def execute(self):
            return "executed"

    agent = TestAgent()

    # Check sovereign initialization sentinel
    assert hasattr(agent, "_sovereign_initialized"), "Missing _sovereign_initialized sentinel"
    assert agent._sovereign_initialized is True, "_sovereign_initialized should be True"

    # Check state management
    agent.set_state("test_key", "test_value")
    assert agent.get_state("test_key") == "test_value", "State management failed"

    # Check authority level
    assert agent.get_authority_level() == "standard", "Default authority should be 'standard'"
