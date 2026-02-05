"""
Test Suite for Phase 4 LLM and Embedding Gateways

Tests TC-PHASE4-001 through TC-PHASE4-004:
- Singleton reset functionality
- Audit log FIFO rotation (memory leak prevention)
- Provider fallback logic
- Embedding cache behavior
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestSovereignLLMGateway:
    """Tests for SovereignLLMGateway."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

        SovereignLLMGateway.reset_instance()

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

        SovereignLLMGateway.reset_instance()

    def test_tc_phase4_001_singleton_reset(self):
        """
        TC-PHASE4-001: Singleton Reset

        Procedure:
        1. Call get_llm_gateway() twice
        2. Compare object IDs
        3. Call reset_instance()
        4. Call get_llm_gateway() again

        Expected:
        - id1 == id2 (Singleton holds)
        - id3 != id1 (Reset successful)
        """
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import (
            SovereignLLMGateway,
            get_llm_gateway,
        )

        # Step 1-2: Get gateway twice, verify same instance
        gateway1 = get_llm_gateway()
        gateway2 = get_llm_gateway()

        assert id(gateway1) == id(gateway2), "Singleton should return same instance"

        # Step 3: Reset singleton
        SovereignLLMGateway.reset_instance()

        # Step 4: Get new instance
        gateway3 = get_llm_gateway()

        assert id(gateway3) != id(gateway1), "Reset should create new instance"

    def test_tc_phase4_002_audit_memory_leak(self):
        """
        TC-PHASE4-002: Audit Memory Leak Prevention

        Procedure:
        1. Get Gateway instance
        2. Set config MAX_AUDIT_LOG_SIZE = 5 via env
        3. Inject 10 audit entries
        4. Check len(gateway.audit_log)

        Expected:
        - len(log) <= 5 (Not 10)
        - Oldest entries pruned (FIFO rotation)
        """
        from unittest import mock

        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        # Set config limit via env
        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "5"}):
            gateway = get_llm_gateway()

            # Flood the log with 10 entries
            for i in range(10):
                gateway._audit(f"provider_{i}", f"model_{i}", True, 10.0 + i)

            # Verify FIFO rotation
            assert len(gateway.audit_log) <= 5, (
                f"Log should be capped at 5, got {len(gateway.audit_log)}"
            )
            assert gateway.operation_stats["total"] == 10, "Total should track all operations"

            # Verify oldest entries were pruned (FIFO)
            providers_in_log = [entry["provider"] for entry in gateway.audit_log]
            assert "provider_0" not in providers_in_log, "Oldest entry should be pruned"

    @pytest.mark.asyncio
    async def test_tc_phase4_003_provider_fallback(self):
        """
        TC-PHASE4-003: Provider Fallback

        Procedure:
        1. Patch _call_openai to raise Exception
        2. Call generate(provider="openai", fallback=["anthropic"])
        3. Patch _call_anthropic to return success

        Expected:
        - Call should succeed
        - operation_stats["fallbacks"] increments
        - audit_log has 2 entries (1 fail, 1 success)
        """
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        gateway = get_llm_gateway()

        # Mock the provider calls
        async def mock_openai_fail(*args, **kwargs):
            raise Exception("OpenAI API Down")

        async def mock_anthropic_success(*args, **kwargs):
            return {"content": "Success from Anthropic", "tokens": 50}

        with patch.object(gateway, "_call_openai", side_effect=mock_openai_fail):
            with patch.object(gateway, "_call_anthropic", side_effect=mock_anthropic_success):
                result = await gateway.generate(
                    "test prompt", provider="openai", fallback_providers=["anthropic"]
                )

        # Verify fallback succeeded
        assert result["content"] == "Success from Anthropic"
        assert gateway.operation_stats["fallbacks"] == 1, "Fallback counter should increment"

        # Verify audit log captured both attempts
        assert len(gateway.audit_log) == 2, "Should have 2 audit entries"
        assert gateway.audit_log[0]["success"] is False, "First entry should be failure"
        assert gateway.audit_log[1]["success"] is True, "Second entry should be success"

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_runtime_error(self):
        """Test that RuntimeError is raised when all providers fail."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        gateway = get_llm_gateway()

        async def mock_fail(*args, **kwargs):
            raise Exception("Provider failed")

        with patch.object(gateway, "_call_openai", side_effect=mock_fail):
            with patch.object(gateway, "_call_anthropic", side_effect=mock_fail):
                with patch.object(gateway, "_call_google", side_effect=mock_fail):
                    with pytest.raises(RuntimeError, match="All LLM providers failed"):
                        await gateway.generate("test", provider="openai")

    def test_default_model_constants(self):
        """Verify default model constants come from config."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        gateway = get_llm_gateway()

        # [PHASE 6] models now come from config
        assert gateway.config.openai_model == "gpt-4o"
        assert gateway.config.anthropic_model == "claude-3-5-sonnet-20241022"
        assert gateway.config.google_model == "gemini-1.5-pro"
        assert gateway.config.max_audit_log_size == 1000


class TestEmbeddingSovereignAgent:
    """Tests for EmbeddingSovereignAgent."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import EmbeddingSovereignAgent

        EmbeddingSovereignAgent.reset_instance()

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import EmbeddingSovereignAgent

        EmbeddingSovereignAgent.reset_instance()

    @pytest.mark.asyncio
    async def test_tc_phase4_004_embed_cache(self):
        """
        TC-PHASE4-004: Embedding cache

        Procedure:
        1. Call get_embedding("test_content")
        2. Verify _get_gemini_embedding was called
        3. Call get_embedding("test_content") again

        Expected:
        - 2nd call does NOT trigger provider
        - operation_stats["cache_hits"] increments
        - Returns identical vector
        """
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway

        gateway = get_embedding_gateway()

        # Mock the embedding provider
        mock_embedding = [0.1, 0.2, 0.3] * 256  # 768 dimensions for gemini

        async def mock_gemini(*args, **kwargs):
            return mock_embedding

        # Mock cache methods
        cache_store = {}

        async def mock_cache_get(key):
            return cache_store.get(key)

        async def mock_cache_set(key, value, ttl=None):
            cache_store[key] = value

        with patch.object(
            gateway, "_get_gemini_embedding", side_effect=mock_gemini
        ) as mock_provider:
            with patch.object(gateway, "cache_get", side_effect=mock_cache_get):
                with patch.object(gateway, "cache_set", side_effect=mock_cache_set):
                    # First call - should hit provider
                    result1 = await gateway.get_embedding("test_content", provider="gemini")

                    assert mock_provider.call_count == 1, "Provider should be called once"
                    assert gateway.operation_stats["cache_misses"] == 1

                    # Second call - should hit cache
                    result2 = await gateway.get_embedding("test_content", provider="gemini")

                    assert mock_provider.call_count == 1, "Provider should NOT be called again"
                    assert gateway.operation_stats["cache_hits"] == 1

                    # Verify identical results
                    assert result1 == result2, "Cached result should match original"

    def test_embedding_singleton_reset(self):
        """Test that reset_instance works for EmbeddingSovereignAgent."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import (
            EmbeddingSovereignAgent,
            get_embedding_gateway,
        )

        gateway1 = get_embedding_gateway()
        gateway2 = get_embedding_gateway()

        assert id(gateway1) == id(gateway2), "Singleton should return same instance"

        EmbeddingSovereignAgent.reset_instance()

        gateway3 = get_embedding_gateway()

        assert id(gateway3) != id(gateway1), "Reset should create new instance"

    def test_embedding_audit_fifo_rotation(self):
        """Test FIFO rotation in embedding audit log."""
        from unittest import mock

        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "5"}):
            gateway = get_embedding_gateway()

            # Flood the log
            for i in range(10):
                gateway._audit(f"provider_{i}", True, False, 10.0 + i)

            assert len(gateway.audit_log) <= 5, (
                f"Log should be capped at 5, got {len(gateway.audit_log)}"
            )
            assert gateway.operation_stats["total"] == 10

    def test_content_hash_deterministic(self):
        """Test that content hash is deterministic."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway

        gateway = get_embedding_gateway()

        hash1 = gateway._content_hash("test content")
        hash2 = gateway._content_hash("test content")
        hash3 = gateway._content_hash("different content")

        assert hash1 == hash2, "Same content should produce same hash"
        assert hash1 != hash3, "Different content should produce different hash"
        assert len(hash1) == 16, "Hash should be 16 characters"


class TestLLMProviderMixin:
    """Tests for LLMProviderMixin."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

        SovereignLLMGateway.reset_instance()

    def test_mixin_lazy_loads_gateway(self):
        """Test that mixin lazy-loads the gateway."""

        class TestAgent(LLMProviderMixin):
            pass

        agent = TestAgent()

        assert agent._llm_gateway is None, "Gateway should not be loaded yet"

        gateway = agent.llm_gateway

        assert gateway is not None, "Gateway should be loaded after access"
        assert agent._llm_gateway is gateway, "Gateway should be cached"


class TestEmbeddingMixin:
    """Tests for EmbeddingMixin."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import EmbeddingSovereignAgent

        EmbeddingSovereignAgent.reset_instance()

    def test_mixin_lazy_loads_gateway(self):
        """Test that mixin lazy-loads the embedding gateway."""

        class TestAgent(EmbeddingMixin):
            pass

        agent = TestAgent()

        assert agent._embedding_gateway is None, "Gateway should not be loaded yet"

        gateway = agent.embedding_gateway

        assert gateway is not None, "Gateway should be loaded after access"
        assert agent._embedding_gateway is gateway, "Gateway should be cached"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
