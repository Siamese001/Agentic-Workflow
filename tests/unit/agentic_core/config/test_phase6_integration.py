"""
Test Suite for Phase 6 Integration - Config Manager Wiring

Tests TC-INTEG-001 through TC-INTEG-003:
- Config propagation to LLM Gateway
- Healing depth limit from config
- Dynamic memory cap from config
"""

import os
import sys
from unittest import mock

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestLLMGatewayConfigIntegration:
    """Tests for LLM Gateway config integration."""

    def setup_method(self):
        """Reset singletons before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

        SovereignLLMGateway.reset_instance()
        SovereignConfigManager.reset_instance()
        # Clear env vars
        for key in ["OPENAI_MODEL", "ANTHROPIC_MODEL", "SOVEREIGN_MAX_AUDIT_LOG_SIZE"]:
            if key in os.environ:
                del os.environ[key]

    def teardown_method(self):
        """Clean up singletons after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import SovereignLLMGateway

        SovereignLLMGateway.reset_instance()
        SovereignConfigManager.reset_instance()

    @pytest.mark.asyncio
    async def test_tc_integ_001_config_propagation(self):
        """
        TC-INTEG-001: Config Propagation

        Procedure:
        1. Reset SovereignLLMGateway and SovereignConfigManager
        2. Set env OPENAI_MODEL="custom-gpt"
        3. Instantiate Gateway
        4. Call generate()

        Expected:
        - Gateway uses "custom-gpt" (from Config)
        - Audit log reflects "custom-gpt"
        - PASS: Hardcoding removed
        """
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        with mock.patch.dict(os.environ, {"OPENAI_MODEL": "test-model-v99"}):
            gateway = get_llm_gateway()

            # Mock the provider call to avoid actual API calls
            async def mock_openai_call(*args, **kwargs):
                return {"content": "test response", "tokens": 10}

            with mock.patch.object(gateway, "_call_openai", side_effect=mock_openai_call):
                result = await gateway.generate("test prompt", provider="openai")

                # Verify result
                assert result["content"] == "test response"

                # Verify audit log captured the custom model
                assert len(gateway.audit_log) == 1
                last_log = gateway.audit_log[-1]
                assert last_log["model"] == "test-model-v99"
                assert last_log["provider"] == "openai"
                assert last_log["success"] is True

    @pytest.mark.asyncio
    async def test_config_fallback_uses_dynamic_models(self):
        """Test that fallback uses dynamic model defaults from config."""
        from agentic_core.L2_execution.mcp.SovereignLLMGateway import get_llm_gateway

        with mock.patch.dict(
            os.environ, {"OPENAI_MODEL": "custom-openai", "ANTHROPIC_MODEL": "custom-anthropic"}
        ):
            gateway = get_llm_gateway()

            # Mock openai to fail, anthropic to succeed
            async def mock_openai_fail(*args, **kwargs):
                raise Exception("OpenAI down")

            async def mock_anthropic_success(*args, **kwargs):
                return {"content": "anthropic response", "tokens": 15}

            with mock.patch.object(gateway, "_call_openai", side_effect=mock_openai_fail):
                with mock.patch.object(
                    gateway, "_call_anthropic", side_effect=mock_anthropic_success
                ):
                    result = await gateway.generate(
                        "test", provider="openai", fallback_providers=["anthropic"]
                    )

                    assert result["content"] == "anthropic response"
                    assert gateway.operation_stats["fallbacks"] == 1

                    # Check that anthropic was called with custom model
                    assert len(gateway.audit_log) == 2
                    assert gateway.audit_log[1]["model"] == "custom-anthropic"


class TestHealingOrchestratorConfigIntegration:
    """Tests for Healing Orchestrator config integration."""

    def setup_method(self):
        """Reset singletons before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()
        SovereignConfigManager.reset_instance()
        for key in ["SOVEREIGN_MAX_HEALING_ATTEMPTS", "SOVEREIGN_MAX_AUDIT_LOG_SIZE"]:
            if key in os.environ:
                del os.environ[key]

    def teardown_method(self):
        """Clean up singletons after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()
        SovereignConfigManager.reset_instance()

    @pytest.mark.asyncio
    async def test_tc_integ_002_healing_depth_limit(self):
        """
        TC-INTEG-002: Healing Depth Limit

        Procedure:
        1. Set env SOVEREIGN_MAX_HEALING_ATTEMPTS="1"
        2. Reset Orchestrator
        3. Trigger recursive heal (depth 2)

        Expected:
        - Returns max_depth_exceeded on 2nd attempt
        - PASS: Config controls healing logic
        """
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_HEALING_ATTEMPTS": "1"}):
            orchestrator = get_healing_orchestrator()

            # Simulate already being at depth 1 (which equals the limit)
            violation = {"type": "test_violation"}
            context = {"_healing_depth": 1}

            result = await orchestrator.heal(violation, context)

            assert result["status"] == "failed"
            assert result["reason"] == "max_depth_exceeded"


class TestValidatorOrchestratorConfigIntegration:
    """Tests for Validator Orchestrator config integration."""

    def setup_method(self):
        """Reset singletons before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()
        SovereignConfigManager.reset_instance()
        if "SOVEREIGN_MAX_AUDIT_LOG_SIZE" in os.environ:
            del os.environ["SOVEREIGN_MAX_AUDIT_LOG_SIZE"]

    def teardown_method(self):
        """Clean up singletons after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()
        SovereignConfigManager.reset_instance()

    def test_tc_integ_003_dynamic_memory_cap(self):
        """
        TC-INTEG-003: Dynamic Memory Cap

        Procedure:
        1. Set env SOVEREIGN_MAX_AUDIT_LOG_SIZE="2"
        2. Reset ValidatorOrchestrator
        3. Run 5 validations

        Expected:
        - Log size is exactly 2
        - PASS: Env var controls memory usage
        """
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
            get_validator_orchestrator,
        )

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "2"}):
            orchestrator = get_validator_orchestrator()

            # Run 5 validations via _audit directly
            for i in range(5):
                orchestrator._audit(f"validator_{i}", True, 10.0)

            # Verify log is capped at 2
            assert len(orchestrator.audit_log) <= 2
            assert orchestrator.operation_stats["total_validations"] == 5


class TestEmbeddingAgentConfigIntegration:
    """Tests for Embedding Agent config integration."""

    def setup_method(self):
        """Reset singletons before each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import EmbeddingSovereignAgent

        EmbeddingSovereignAgent.reset_instance()
        SovereignConfigManager.reset_instance()
        if "SOVEREIGN_MAX_AUDIT_LOG_SIZE" in os.environ:
            del os.environ["SOVEREIGN_MAX_AUDIT_LOG_SIZE"]

    def teardown_method(self):
        """Clean up singletons after each test."""
        from agentic_core.config.SovereignConfigManager import SovereignConfigManager
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import EmbeddingSovereignAgent

        EmbeddingSovereignAgent.reset_instance()
        SovereignConfigManager.reset_instance()

    def test_embedding_dimensions_from_config(self):
        """Test that embedding dimensions come from config."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway

        gateway = get_embedding_gateway()

        # Verify dimensions match config defaults
        assert gateway.EXPECTED_DIMENSIONS["gemini"] == 768
        assert gateway.EXPECTED_DIMENSIONS["openai"] == 1536

    def test_embedding_audit_uses_config_limit(self):
        """Test that embedding audit log respects config limit."""
        from agentic_core.L2_execution.mcp.EmbeddingSovereignAgent import get_embedding_gateway

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "3"}):
            gateway = get_embedding_gateway()

            # Flood the log
            for i in range(10):
                gateway._audit(f"provider_{i}", True, False, 10.0)

            assert len(gateway.audit_log) <= 3
            assert gateway.operation_stats["total"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
