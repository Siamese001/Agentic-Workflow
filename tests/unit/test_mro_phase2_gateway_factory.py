"""
Phase 2 MRO Refactoring Tests - Gateway Factory
================================================
Validates the GatewayFactory composition pattern.

Tests verify:
1. GatewayFactory provides singleton instances
2. GatewayBundle aggregates all gateways
3. Stub implementations work for testing
4. Reset functionality works for test isolation
"""

import pytest
from pathlib import Path
import sys

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L2_execution.gateway_factory import (
    GatewayFactory,
    GatewayBundle,
    _StubLLMGateway,
    _StubEmbeddingGateway,
    _StubValidatorOrchestrator,
    _StubHealingOrchestrator,
)

# Mark all tests as guardian tests
pytestmark = pytest.mark.guardian


class TestGatewayFactorySingletons:
    """Test that GatewayFactory provides singleton instances."""

    def setup_method(self):
        """Reset factory before each test."""
        GatewayFactory.reset_all()

    def teardown_method(self):
        """Reset factory after each test."""
        GatewayFactory.reset_all()

    def test_llm_gateway_is_singleton(self):
        """LLM gateway should be a singleton."""
        gateway1 = GatewayFactory.get_llm_gateway()
        gateway2 = GatewayFactory.get_llm_gateway()
        assert gateway1 is gateway2

    def test_embedding_gateway_is_singleton(self):
        """Embedding gateway should be a singleton."""
        gateway1 = GatewayFactory.get_embedding_gateway()
        gateway2 = GatewayFactory.get_embedding_gateway()
        assert gateway1 is gateway2

    def test_validator_orchestrator_is_singleton(self):
        """Validator orchestrator should be a singleton."""
        orch1 = GatewayFactory.get_validator_orchestrator()
        orch2 = GatewayFactory.get_validator_orchestrator()
        assert orch1 is orch2

    def test_healing_orchestrator_is_singleton(self):
        """Healing orchestrator should be a singleton."""
        orch1 = GatewayFactory.get_healing_orchestrator()
        orch2 = GatewayFactory.get_healing_orchestrator()
        assert orch1 is orch2


class TestGatewayBundle:
    """Test GatewayBundle aggregation."""

    def setup_method(self):
        """Reset factory before each test."""
        GatewayFactory.reset_all()

    def teardown_method(self):
        """Reset factory after each test."""
        GatewayFactory.reset_all()

    def test_create_all_returns_bundle(self):
        """create_all should return a GatewayBundle."""
        bundle = GatewayFactory.create_all()
        assert isinstance(bundle, GatewayBundle)

    def test_bundle_has_all_gateways(self):
        """Bundle should have all gateway types."""
        bundle = GatewayFactory.create_all()
        assert bundle.llm is not None
        assert bundle.embedding is not None
        assert bundle.validator is not None
        assert bundle.healing is not None

    def test_create_minimal_has_llm_only(self):
        """create_minimal should only have LLM gateway set."""
        bundle = GatewayFactory.create_minimal()
        assert bundle.llm is not None
        assert bundle.embedding is None
        assert bundle.validator is None
        assert bundle.healing is None


class TestStubImplementations:
    """Test stub implementations for testing scenarios."""

    @pytest.mark.asyncio
    async def test_stub_llm_gateway_generate(self):
        """Stub LLM gateway should return valid response."""
        stub = _StubLLMGateway()
        response = await stub.generate("Test prompt")
        assert "content" in response
        assert response["stub"] is True

    @pytest.mark.asyncio
    async def test_stub_embedding_gateway_get_embedding(self):
        """Stub embedding gateway should return valid embedding."""
        stub = _StubEmbeddingGateway()
        embedding = await stub.get_embedding("Test content")
        assert isinstance(embedding, list)
        assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_stub_embedding_gateway_batch(self):
        """Stub embedding gateway batch should return multiple embeddings."""
        stub = _StubEmbeddingGateway()
        embeddings = await stub.get_embeddings_batch(["a", "b", "c"])
        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)

    @pytest.mark.asyncio
    async def test_stub_validator_orchestrator(self):
        """Stub validator orchestrator should return valid result."""
        stub = _StubValidatorOrchestrator()
        result = await stub.validate("content", "test_validator")
        assert result["valid"] is True
        assert result["stub"] is True

    @pytest.mark.asyncio
    async def test_stub_healing_orchestrator(self):
        """Stub healing orchestrator should return valid result."""
        stub = _StubHealingOrchestrator()
        result = await stub.heal({"type": "test_violation"})
        assert result["healed"] is True
        assert result["stub"] is True


class TestFactoryReset:
    """Test factory reset functionality."""

    def test_reset_clears_all_singletons(self):
        """reset_all should clear all cached instances."""
        # Get instances
        llm1 = GatewayFactory.get_llm_gateway()
        embed1 = GatewayFactory.get_embedding_gateway()

        # Reset
        GatewayFactory.reset_all()

        # Get new instances
        llm2 = GatewayFactory.get_llm_gateway()
        embed2 = GatewayFactory.get_embedding_gateway()

        # Should be different instances (new objects created)
        assert llm1 is not llm2
        assert embed1 is not embed2


class TestCompositionPattern:
    """Test that composition pattern works as expected."""

    def setup_method(self):
        """Reset factory before each test."""
        GatewayFactory.reset_all()

    def teardown_method(self):
        """Reset factory after each test."""
        GatewayFactory.reset_all()

    def test_agent_can_use_composition(self):
        """Demonstrate composition pattern works."""

        class MockAgent:
            def __init__(self):
                self.gateways = GatewayFactory.create_all()

            @property
            def llm(self):
                return self.gateways.llm

        agent = MockAgent()
        assert agent.llm is not None
        assert agent.gateways.validator is not None

    def test_agent_can_use_selective_gateways(self):
        """Agent can selectively get only needed gateways."""

        class MinimalAgent:
            def __init__(self):
                self.llm = GatewayFactory.get_llm_gateway()

        agent = MinimalAgent()
        assert agent.llm is not None
