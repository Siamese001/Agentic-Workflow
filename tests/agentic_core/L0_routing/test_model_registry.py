"""Tests for L0_routing.config.model_registry module."""

from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config import model_registry


class TestModelRegistry:
    """Test suite for model registry constants and functions."""

    def test_deterministic_model_sentinel(self):
        """Test deterministic model sentinel constant."""
        assert model_registry.DETERMINISTIC_MODEL_SENTINEL == "local_deterministic"

    def test_qwen_local_model_id_default(self):
        """Test Qwen local model ID default value."""
        assert model_registry.QWEN_LOCAL_MODEL_ID == "Qwen/Qwen2.5-32B-Instruct-AWQ"

    def test_qwen_local_model_id_env_override(self):
        """Test Qwen local model ID can be overridden by env var."""
        with patch.dict(
            "os.environ", {"VLLM_MODEL_NAME": "custom/qwen-model"}
        ):
            # Reload module to pick up env var
            import importlib

            importlib.reload(model_registry)
            assert model_registry.QWEN_LOCAL_MODEL_ID == "custom/qwen-model"

    def test_vllm_base_url_default(self):
        """Test VLLM base URL default value."""
        assert model_registry.VLLM_BASE_URL == "http://localhost:8000/v1"

    def test_vllm_base_url_env_override(self):
        """Test VLLM base URL can be overridden by env var."""
        with patch.dict("os.environ", {"VLLM_BASE_URL": "http://custom:8080/v1"}):
            import importlib

            importlib.reload(model_registry)
            assert model_registry.VLLM_BASE_URL == "http://custom:8080/v1"

    def test_gemini_flash_model_id(self):
        """Test Gemini Flash model ID."""
        assert model_registry.GEMINI_FLASH_MODEL_ID == "gemini-3-flash-preview"

    def test_gemini_pro_model_id(self):
        """Test Gemini Pro model ID (refreshed 2026-05-01)."""
        assert model_registry.GEMINI_PRO_MODEL_ID == "gemini-3.1-pro-preview"

    def test_openai_model_id(self):
        """Test OpenAI model ID for consensus (refreshed 2026-05-01)."""
        assert model_registry.OPENAI_MODEL_ID == "gpt-5.4-mini"

    def test_anthropic_model_id(self):
        """Test Anthropic model ID for consensus."""
        assert model_registry.ANTHROPIC_MODEL_ID == "claude-sonnet-4-6"

    def test_consensus_jurors_default(self):
        """Test default consensus jurors (3 jurors, refreshed 2026-05-01)."""
        jurors = model_registry.CONSENSUS_JURORS
        assert len(jurors) == 3
        assert "gpt-5.4-mini" in jurors
        assert "claude-sonnet-4-6" in jurors
        assert "gemini-3.1-pro-preview" in jurors

    def test_consensus_jurors_with_qwen(self):
        """Test consensus jurors with Qwen enabled."""
        with patch.dict("os.environ", {"USE_QWEN_CONSENSUS_JUROR": "1"}):
            import importlib

            importlib.reload(model_registry)
            jurors = model_registry.CONSENSUS_JURORS
            assert len(jurors) == 4
            assert model_registry.QWEN_LOCAL_MODEL_ID in jurors

    def test_consensus_jurors_env_override(self):
        """Test consensus jurors can be overridden by env var."""
        custom_jurors = "gpt-5.4-mini,claude-sonnet-4-6,gemini-3.1-pro-preview,o3"
        with patch.dict("os.environ", {"CONSENSUS_JURORS": custom_jurors}):
            import importlib

            importlib.reload(model_registry)
            jurors = model_registry.CONSENSUS_JURORS
            assert len(jurors) == 4
            assert "o3" in jurors

    def test_embedding_model_id(self):
        """Test embedding model ID."""
        assert model_registry.EMBEDDING_MODEL_ID == "BAAI/bge-m3"

    def test_qwen_disallowed_failure_types(self):
        """Test Qwen disallowed failure types."""
        disallowed = model_registry.QWEN_DISALLOWED_FAILURE_TYPES
        assert "LAYER_VIOLATION" in disallowed
        assert "GATEWAY_BYPASS" in disallowed
        assert "KILL_SWITCH_BYPASS" in disallowed

    def test_tier_constants(self):
        """Test tier string constants."""
        assert model_registry.TIER_DETERMINISTIC == "DETERMINISTIC"
        assert model_registry.TIER_QWEN_LOCAL == "QWEN_LOCAL"
        assert model_registry.TIER_GEMINI_FLASH == "GEMINI_FLASH"
        assert model_registry.TIER_GEMINI_PRO == "GEMINI_PRO"
        assert model_registry.TIER_HITL == "HITL"

    def test_all_tiers(self):
        """Test ALL_TIERS constant includes all tiers."""
        expected_tiers = [
            "DETERMINISTIC",
            "QWEN_LOCAL",
            "GEMINI_FLASH",
            "GEMINI_PRO",
            "HITL",
        ]
        assert model_registry.ALL_TIERS == tuple(expected_tiers)

    def test_get_model_for_tier_deterministic(self):
        """Test get_model_for_tier for deterministic tier."""
        model = model_registry.get_model_for_tier(model_registry.TIER_DETERMINISTIC)
        assert model == "local_deterministic"

    def test_get_model_for_tier_qwen(self):
        """Test get_model_for_tier for Qwen tier."""
        model = model_registry.get_model_for_tier(model_registry.TIER_QWEN_LOCAL)
        assert model == model_registry.QWEN_LOCAL_MODEL_ID

    def test_get_model_for_tier_gemini_flash(self):
        """Test get_model_for_tier for Gemini Flash tier."""
        model = model_registry.get_model_for_tier(model_registry.TIER_GEMINI_FLASH)
        assert model == model_registry.GEMINI_FLASH_MODEL_ID

    def test_get_model_for_tier_gemini_pro(self):
        """Test get_model_for_tier for Gemini Pro tier."""
        model = model_registry.get_model_for_tier(model_registry.TIER_GEMINI_PRO)
        assert model == model_registry.GEMINI_PRO_MODEL_ID

    def test_get_model_for_tier_hitl(self):
        """Test get_model_for_tier for HITL tier."""
        model = model_registry.get_model_for_tier(model_registry.TIER_HITL)
        assert model == "human_review"

    def test_get_model_for_tier_invalid(self):
        """Test get_model_for_tier raises on invalid tier."""
        with pytest.raises(ValueError, match="Unknown tier"):
            model_registry.get_model_for_tier("INVALID_TIER")

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(model_registry, "get_model_for_tier")
        assert hasattr(model_registry, "ALL_TIERS")
        assert hasattr(model_registry, "CONSENSUS_JURORS")
        assert hasattr(model_registry, "QWEN_LOCAL_MODEL_ID")
        assert hasattr(model_registry, "GEMINI_PRO_MODEL_ID")
