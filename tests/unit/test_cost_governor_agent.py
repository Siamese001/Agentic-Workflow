# New file: tests/unit/test_cost_governor_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import patch
import logging

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.CostGovernorAgent import CostGovernorAgent


@pytest.fixture
def default_config():
    """Default configuration for CostGovernorAgent."""
    return {
        "budget_limit": 10.0
    }


@pytest.fixture
def cost_governor_agent(default_config):
    """Fixture for fresh CostGovernorAgent instance."""
    return CostGovernorAgent(default_config)


def test_instantiation(cost_governor_agent, default_config):
    """Smoke test: agent instantiates without error."""
    assert cost_governor_agent is not None
    assert hasattr(cost_governor_agent, "track")
    assert hasattr(cost_governor_agent, "config")
    assert cost_governor_agent.config == default_config
    assert cost_governor_agent.limit == 10.0
    assert cost_governor_agent.spend == 0.0


def test_initialization_custom_limit():
    """Test agent initialization with custom budget limit."""
    custom_config = {"budget_limit": 25.0}
    agent = CostGovernorAgent(custom_config)
    
    assert agent.limit == 25.0
    assert agent.spend == 0.0


def test_initialization_default_limit():
    """Test agent initialization without budget limit (uses default)."""
    empty_config = {}
    agent = CostGovernorAgent(empty_config)
    
    assert agent.limit == 10.0  # Default value
    assert agent.spend == 0.0


def test_track_basic_usage(cost_governor_agent):
    """Test basic token tracking without exceeding limit."""
    # Track a small usage: 100 input + 50 output tokens
    cost = cost_governor_agent.track("gpt-4", 100, 50)
    
    # Cost calculation: (100 + 50) * 2e-05 = 150 * 0.00002 = 0.003
    expected_cost = 150 * 2e-05
    assert cost == expected_cost
    assert cost_governor_agent.spend == expected_cost


def test_track_multiple_calls(cost_governor_agent):
    """Test multiple tracking calls accumulate spend correctly."""
    # First call
    cost1 = cost_governor_agent.track("gpt-4", 100, 50)  # 0.003
    assert cost_governor_agent.spend == cost1
    
    # Second call
    cost2 = cost_governor_agent.track("gpt-3.5", 200, 100)  # 0.006
    expected_total = cost1 + cost2
    assert cost_governor_agent.spend == expected_total
    assert cost_governor_agent.spend == (150 + 300) * 2e-05


def test_track_budget_exceeded():
    """Test that budget limit triggers exception when exceeded."""
    # Create agent with very low limit
    low_limit_config = {"budget_limit": 0.001}  # $0.001 limit
    agent = CostGovernorAgent(low_limit_config)
    
    # This should exceed the limit: (50000) * 2e-05 = 1.0 > 0.001
    with pytest.raises(Exception) as exc_info:
        agent.track("gpt-4", 25000, 25000)
    
    assert "BUDGET EXCEEDED" in str(exc_info.value)
    assert "exceeds limit" in str(exc_info.value)


def test_track_exactly_at_limit():
    """Test tracking exactly at the budget limit."""
    # Create agent with limit that will be exactly reached
    limit = 0.01  # $0.01
    config = {"budget_limit": limit}
    agent = CostGovernorAgent(config)
    
    # Calculate tokens needed to reach exactly the limit
    # limit = tokens * 2e-05, so tokens = limit / 2e-05
    tokens_for_limit = int(limit / 2e-05)
    
    # This should be exactly at limit (no exception)
    cost = agent.track("gpt-4", tokens_for_limit // 2, tokens_for_limit // 2)
    assert agent.spend <= limit


def test_track_logging(cost_governor_agent, caplog):
    """Test that tracking logs spend information."""
    with caplog.at_level(logging.INFO):
        cost_governor_agent.track("gpt-4", 100, 50)
    
    assert "Governor: Current Spend" in caplog.text
    assert "Limit" in caplog.text
    assert "$" in caplog.text


def test_track_different_models(cost_governor_agent):
    """Test tracking with different model names (cost calculation same)."""
    cost1 = cost_governor_agent.track("gpt-4", 100, 50)
    cost2 = cost_governor_agent.track("gpt-3.5-turbo", 100, 50)  
    cost3 = cost_governor_agent.track("claude", 100, 50)
    
    # All should have same cost since model name doesn't affect calculation
    assert cost1 == cost2 == cost3
    assert cost_governor_agent.spend == cost1 + cost2 + cost3


def test_track_zero_tokens(cost_governor_agent):
    """Test tracking with zero tokens."""
    cost = cost_governor_agent.track("gpt-4", 0, 0)
    
    assert cost == 0.0
    assert cost_governor_agent.spend == 0.0


def test_track_large_token_counts():
    """Test tracking with large token counts."""
    from agentic_core.L5_safety.guardrails.CostGovernorAgent import CostGovernorAgent
    # Use a high budget limit to avoid exceeding it
    agent = CostGovernorAgent({"budget_limit": 100.0})
    
    # Large token counts that could cause precision issues
    large_input = 1000000
    large_output = 500000
    
    cost = agent.track("gpt-4", large_input, large_output)
    expected_cost = (large_input + large_output) * 2e-05
    
    assert cost == expected_cost
    assert agent.spend == expected_cost


@pytest.mark.autonomy
def test_heal_repository_smoke(cost_governor_agent):
    """Autonomy heal smoke test — ensure no crash."""
    result = cost_governor_agent.heal_repository()
    
    # CostGovernorAgent is operational L5 safety - should skip healing
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_heal_repository_parameters(cost_governor_agent):
    """Test heal_repository accepts expected parameters."""
    result = cost_governor_agent.heal_repository(
        dry_run=False,
        execute=True,
        depth=1,
        max_depth=2
    )
    
    assert isinstance(result, dict)
    assert result.get("skipped") == 1


def test_heal_repository_cycle_detection():
    """Test heal_repository cycle detection."""
    agent = CostGovernorAgent({})
    
    # Simulate cycle by passing agent's own name in call_path
    call_path = {agent.__class__.__name__}
    result = agent.heal_repository(_call_path=call_path)
    
    assert isinstance(result, dict)
    assert result.get("errors") == 1
    assert result.get("cycle_detected") is True


def test_heal_repository_depth_limit():
    """Test heal_repository depth limiting."""
    agent = CostGovernorAgent({})
    
    # Test depth limiting
    result = agent.heal_repository(depth=5, max_depth=3)
    
    assert isinstance(result, dict)
    assert result.get("errors") == 1
    assert result.get("depth_limited") is True


def test_timeout_decorator_applied(cost_governor_agent):
    """Test that heal_repository has timeout decorator applied."""
    # The method should have timeout applied - we verify it exists
    assert hasattr(cost_governor_agent.heal_repository, '__wrapped__')


def test_healer_mixin_inheritance(cost_governor_agent):
    """Test that agent properly inherits from HealerMixin."""
    from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
    assert isinstance(cost_governor_agent, HealerMixin)


def test_cost_calculation_precision():
    """Test that cost calculations maintain proper precision."""
    agent = CostGovernorAgent({"budget_limit": 100.0})
    
    # Test with various token combinations
    test_cases = [
        (1, 1),      # Minimal
        (100, 200),  # Small
        (1000, 500), # Medium
        (10000, 5000) # Large
    ]
    
    total_expected = 0
    for input_tokens, output_tokens in test_cases:
        cost = agent.track("test-model", input_tokens, output_tokens)
        expected_cost = (input_tokens + output_tokens) * 2e-05
        assert cost == expected_cost
        total_expected += expected_cost
    
    # Total spend should match sum of individual costs
    assert abs(agent.spend - total_expected) < 1e-10  # Account for floating point precision


def test_config_immutability(cost_governor_agent):
    """Test that config changes don't affect initialized agent."""
    original_limit = cost_governor_agent.limit
    original_config = cost_governor_agent.config
    
    # Modify the config dict (shouldn't affect agent)
    original_config["budget_limit"] = 999.0
    
    # Agent's limit should remain unchanged
    assert cost_governor_agent.limit == original_limit
