"""
Tests for SovereignLLMGateway - LLM provider gateway and enforcement.

Coverage:
- Provider initialization and validation
- Request routing to providers
- Provider substitution prohibition
- Token counting and budget enforcement
- Response validation
- Error handling for provider failures
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway


class TestSovereignLLMGateway:
    """Test suite for SovereignLLMGateway."""

    def test_init_with_valid_provider_config(self):
        """Test initialization with valid provider configuration."""
        config = {
            "anthropic": {
                "api_key": "test_key",
                "model": "claude-3-opus"
            }
        }
        gateway = SovereignLLMGateway(provider_config=config)
        assert gateway.provider_config == config

    def test_init_with_missing_provider_config(self):
        """Test initialization fails with missing provider config."""
        with pytest.raises(ValueError):
            SovereignLLMGateway(provider_config={})

    def test_route_request_to_provider(self):
        """Test routing request to specified provider."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        provider = Mock()
        provider.complete.return_value = "Response"
        gateway.providers["anthropic"] = provider
        
        response = gateway.route(
            provider="anthropic",
            prompt="Test prompt"
        )
        
        assert response == "Response"
        provider.complete.assert_called_once()

    def test_provider_substitution_prohibition(self):
        """Test provider substitution is prohibited."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        # Attempt to use unconfigured provider
        with pytest.raises(PermissionError):
            gateway.route(
                provider="openai",  # Not configured
                prompt="Test prompt"
            )

    def test_enforce_token_budget(self):
        """Test token budget enforcement."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(
            provider_config=config,
            max_tokens_per_request=1000
        )
        
        provider = Mock()
        provider.complete.return_value = "Response"
        gateway.providers["anthropic"] = provider
        
        # Request exceeds budget
        with pytest.raises(ValueError):
            gateway.route(
                provider="anthropic",
                prompt="Test",
                max_tokens=2000  # Exceeds 1000 limit
            )

    def test_validate_provider_response(self):
        """Test validation of provider response."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        valid_response = {"content": "Test response", "finish_reason": "stop"}
        assert gateway.validate_response(valid_response) is True

    def test_validate_malformed_response(self):
        """Test validation fails for malformed response."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        malformed_response = {"invalid": "structure"}
        assert gateway.validate_response(malformed_response) is False

    def test_handle_provider_failure(self):
        """Test graceful handling of provider failure."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        provider = Mock()
        provider.complete.side_effect = Exception("Provider error")
        gateway.providers["anthropic"] = provider
        
        with pytest.raises(RuntimeError):
            gateway.route(provider="anthropic", prompt="Test")

    def test_get_provider_status(self):
        """Test retrieving status of all providers."""
        config = {
            "anthropic": {"api_key": "test_key", "model": "claude-3-opus"},
            "gemini": {"api_key": "test_key", "model": "gemini-pro"}
        }
        gateway = SovereignLLMGateway(provider_config=config)
        
        status = gateway.get_provider_status()
        
        assert "anthropic" in status
        assert "gemini" in status

    def test_register_provider(self):
        """Test registering a new provider."""
        config = {"anthropic": {"api_key": "test_key", "model": "claude-3-opus"}}
        gateway = SovereignLLMGateway(provider_config=config)
        
        new_provider = Mock()
        gateway.register_provider("gemini", new_provider)
        
        assert "gemini" in gateway.providers

    def test_unregister_provider(self):
        """Test unregistering a provider."""
        config = {"anthropic": {"api_key": "test_key", "model": "claude-3-opus"}}
        gateway = SovereignLLMGateway(provider_config=config)
        
        provider = Mock()
        gateway.providers["anthropic"] = provider
        
        gateway.unregister_provider("anthropic")
        assert "anthropic" not in gateway.providers

    def test_token_counting(self):
        """Test accurate token counting."""
        config = {"anthropic": {"api_key": "test_key", "model": "claude-3-opus"}}
        gateway = SovereignLLMGateway(provider_config=config)
        
        prompt = "This is a test prompt with several words."
        count = gateway.count_tokens(prompt)
        
        assert count > 0
        assert isinstance(count, int)
