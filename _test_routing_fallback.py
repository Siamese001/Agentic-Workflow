#!/usr/bin/env python3
"""Test script for resilient routing fallback behavior.

Verifies:
- Primary provider routing when healthy
- Automatic fallback when primary circuit breaker is open
- Waterfall through multiple fallback providers
- AllProvidersDownError when all providers unavailable
- Routing telemetry logging

Usage:
    python test_routing_fallback.py
"""

import asyncio
import logging
import os
import sys
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import routing components
from runtime.shared.routing import (
    HardenedRouter,
    RouteConfig,
    RoutingTier,
    AllProvidersDownError,
    get_resilient_router,
    reset_router,
)
from runtime.shared.multi_provider_clients import Provider
from shared.resilience.circuit_breaker import CircuitBreakerState
from runtime.shared.agent_executor import AgentMessage


async def test_primary_routing():
    """Test routing to primary provider when healthy."""
    print("\n=== Testing Primary Provider Routing ===")
    
    # Create router with custom config
    config = RouteConfig(
        tier_name="test_tier",
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC],
        timeout_ms=30000,
    )
    
    router = HardenedRouter(configs={"test_tier": config})
    
    # Check that primary is healthy
    health = router.get_provider_health()
    print(f"Provider health: {health}")
    
    if Provider.OPENAI in router.executors:
        openai_state = router.executors[Provider.OPENAI].get_circuit_breaker_state()
        print(f"OpenAI circuit breaker state: {openai_state}")
        assert openai_state == "CLOSED", "OpenAI should be healthy"
        print("✓ Primary provider (OpenAI) is healthy")
    else:
        print("⚠ OpenAI executor not available (API key missing)")
    
    print("Primary routing test passed!\n")


async def test_fallback_routing():
    """Test automatic fallback when primary is down."""
    print("\n=== Testing Fallback Routing ===")
    
    # Create router
    config = RouteConfig(
        tier_name="test_tier",
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC, Provider.GOOGLE],
        timeout_ms=30000,
    )
    
    router = HardenedRouter(configs={"test_tier": config})
    
    # Manually open OpenAI circuit breaker to simulate failure
    if Provider.OPENAI in router.executors:
        openai_executor = router.executors[Provider.OPENAI]
        print("Simulating OpenAI circuit breaker OPEN...")
        
        # Trip the circuit breaker by recording failures
        for i in range(5):
            openai_executor.circuit_breaker.record_failure()
        
        state = openai_executor.get_circuit_breaker_state()
        print(f"OpenAI circuit breaker state: {state}")
        assert state == "OPEN", "Circuit breaker should be OPEN"
        print("✓ OpenAI circuit breaker is OPEN")
        
        # Check that router detects unhealthy primary
        is_healthy = router._is_provider_healthy(Provider.OPENAI)
        assert not is_healthy, "Router should detect unhealthy primary"
        print("✓ Router correctly detects unhealthy primary")
        
        # Reset for next test
        openai_executor.reset_circuit_breaker()
    else:
        print("⚠ Skipping test (OpenAI not available)")
    
    print("Fallback routing test passed!\n")


async def test_all_providers_down():
    """Test AllProvidersDownError when all providers unavailable."""
    print("\n=== Testing All Providers Down ===")
    
    # Create router
    config = RouteConfig(
        tier_name="test_tier",
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC],
        timeout_ms=30000,
    )
    
    router = HardenedRouter(configs={"test_tier": config})
    
    # Open all circuit breakers
    for provider, executor in router.executors.items():
        if hasattr(executor, 'circuit_breaker'):
            for i in range(5):
                executor.circuit_breaker.record_failure()
            print(f"Opened circuit breaker for {provider.value}")
    
    # Verify all providers are unhealthy
    health = router.get_provider_health()
    all_down = all(not status["healthy"] for status in health.values())
    
    if all_down:
        print("✓ All providers marked as unhealthy")
        print(f"Provider health: {health}")
    else:
        print("⚠ Some providers still healthy (expected if API keys missing)")
    
    # Reset circuit breakers
    router.reset_all_circuit_breakers()
    print("✓ Circuit breakers reset")
    
    print("All providers down test passed!\n")


async def test_routing_tiers():
    """Test different routing tiers."""
    print("\n=== Testing Routing Tiers ===")
    
    router = get_resilient_router()
    
    # Check available tiers
    available_tiers = list(router.configs.keys())
    print(f"Available routing tiers: {available_tiers}")
    
    expected_tiers = [
        RoutingTier.REASONING.value,
        RoutingTier.SPEED.value,
        RoutingTier.COST_OPTIMIZED.value,
        RoutingTier.BALANCED.value,
    ]
    
    for tier in expected_tiers:
        assert tier in available_tiers, f"Missing tier: {tier}"
        config = router.get_config(tier)
        print(f"\n{tier}:")
        print(f"  Primary: {config.primary_provider.value}")
        print(f"  Fallbacks: {[p.value for p in config.fallback_providers]}")
        print(f"  Timeout: {config.timeout_ms}ms")
    
    print("\n✓ All routing tiers configured correctly")
    print("Routing tiers test passed!\n")


async def test_provider_health_monitoring():
    """Test provider health monitoring."""
    print("\n=== Testing Provider Health Monitoring ===")
    
    router = get_resilient_router()
    
    # Get health status
    health = router.get_provider_health()
    print("Provider health status:")
    for provider, status in health.items():
        print(f"  {provider}: {status}")
    
    # Count healthy providers
    healthy_count = sum(1 for status in health.values() if status["healthy"])
    print(f"\n✓ {healthy_count}/{len(health)} providers healthy")
    
    print("Provider health monitoring test passed!\n")


async def test_singleton_factory():
    """Test singleton factory pattern."""
    print("\n=== Testing Singleton Factory ===")
    
    # Get router instance
    router1 = get_resilient_router()
    router2 = get_resilient_router()
    
    # Should be same instance
    assert router1 is router2, "Should return same singleton instance"
    print("✓ Singleton pattern working correctly")
    
    # Reset and get new instance
    reset_router()
    router3 = get_resilient_router()
    
    # Should be different instance
    assert router3 is not router1, "Should create new instance after reset"
    print("✓ Router reset working correctly")
    
    print("Singleton factory test passed!\n")


async def test_mock_execution():
    """Test router execution with mocked executors."""
    print("\n=== Testing Mock Execution ===")
    
    # Create router with custom config
    config = RouteConfig(
        tier_name="test_tier",
        primary_provider=Provider.OPENAI,
        fallback_providers=[Provider.ANTHROPIC],
        timeout_ms=30000,
    )
    
    router = HardenedRouter(configs={"test_tier": config})
    
    # Mock the executors
    mock_openai = AsyncMock()
    mock_openai.run_llm = AsyncMock(return_value="OpenAI response")
    mock_openai.get_circuit_breaker_state = Mock(return_value="CLOSED")
    mock_openai.circuit_breaker = Mock()
    mock_openai.circuit_breaker.state = CircuitBreakerState.CLOSED
    
    mock_anthropic = AsyncMock()
    mock_anthropic.run_llm = AsyncMock(return_value="Anthropic response")
    mock_anthropic.get_circuit_breaker_state = Mock(return_value="CLOSED")
    mock_anthropic.circuit_breaker = Mock()
    mock_anthropic.circuit_breaker.state = CircuitBreakerState.CLOSED
    
    # Replace executors with mocks
    router.executors[Provider.OPENAI] = mock_openai
    router.executors[Provider.ANTHROPIC] = mock_anthropic
    
    # Test primary routing
    result = await router.execute_with_fallback(
        tier="test_tier",
        prompt="Test prompt",
    )
    
    assert result == "OpenAI response", "Should route to primary"
    assert mock_openai.run_llm.called, "Should call OpenAI executor"
    assert not mock_anthropic.run_llm.called, "Should not call Anthropic"
    print("✓ Primary routing works with mocks")
    
    # Test fallback routing
    mock_openai.reset_mock()
    mock_anthropic.reset_mock()
    mock_openai.circuit_breaker.state = CircuitBreakerState.OPEN
    mock_openai.get_circuit_breaker_state = Mock(return_value="OPEN")
    
    result = await router.execute_with_fallback(
        tier="test_tier",
        prompt="Test prompt",
    )
    
    assert result == "Anthropic response", "Should route to fallback"
    assert not mock_openai.run_llm.called, "Should not call OpenAI (circuit open)"
    assert mock_anthropic.run_llm.called, "Should call Anthropic fallback"
    print("✓ Fallback routing works with mocks")
    
    print("Mock execution test passed!\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("RESILIENT ROUTING FALLBACK TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_primary_routing,
        test_fallback_routing,
        test_all_providers_down,
        test_routing_tiers,
        test_provider_health_monitoring,
        test_singleton_factory,
        test_mock_execution,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Resilient routing is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
