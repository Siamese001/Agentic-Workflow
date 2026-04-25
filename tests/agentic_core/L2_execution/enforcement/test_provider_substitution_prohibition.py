"""
Tests for ProviderSubstitutionProhibition - security enforcement for provider binding.

Coverage:
- Provider binding initialization
- Provider substitution detection
- Binding verification
- Policy enforcement
- Exception handling for violations
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L2_execution.enforcement.provider_substitution_prohibition import ProviderSubstitutionProhibition


class TestProviderSubstitutionProhibition:
    """Test suite for ProviderSubstitutionProhibition."""

    def test_init_with_allowed_providers(self):
        """Test initialization with allowed provider list."""
        allowed_providers = ["anthropic", "gemini", "openai"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        assert prohibition.allowed_providers == allowed_providers

    def test_init_with_empty_providers(self):
        """Test initialization fails with empty provider list."""
        with pytest.raises(ValueError):
            ProviderSubstitutionProhibition(allowed_providers=[])

    def test_detect_provider_substitution(self):
        """Test detection of provider substitution attempt."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        # Attempt to use disallowed provider
        is_substitution = prohibition.detect_substitution(
            requested_provider="openai",
            bound_provider="anthropic"
        )
        
        assert is_substitution is True

    def test_detect_no_substitution(self):
        """Test no substitution when using allowed provider."""
        allowed_providers = ["anthropic", "gemini"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        is_substitution = prohibition.detect_substitution(
            requested_provider="anthropic",
            bound_provider="anthropic"
        )
        
        assert is_substitution is False

    def test_verify_provider_binding(self):
        """Test verification of provider binding."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        binding = {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "api_key_hash": "abc123"
        }
        
        assert prohibition.verify_binding(binding) is True

    def test_verify_invalid_binding(self):
        """Test verification fails for invalid binding."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        binding = {
            "provider": "openai",  # Not allowed
            "model": "gpt-4",
            "api_key_hash": "xyz789"
        }
        
        assert prohibition.verify_binding(binding) is False

    def test_enforce_binding_policy(self):
        """Test enforcement of binding policy."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        valid_binding = {"provider": "anthropic", "model": "claude-3-opus"}
        # Should not raise for valid binding
        prohibition.enforce(valid_binding)

    def test_enforce_blocks_invalid_binding(self):
        """Test enforcement blocks invalid bindings."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        invalid_binding = {"provider": "openai", "model": "gpt-4"}
        
        with pytest.raises(PermissionError):
            prohibition.enforce(invalid_binding)

    def test_add_allowed_provider(self):
        """Test adding a provider to allowed list."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        prohibition.add_provider("gemini")
        assert "gemini" in prohibition.allowed_providers

    def test_remove_allowed_provider(self):
        """Test removing a provider from allowed list."""
        allowed_providers = ["anthropic", "gemini"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        prohibition.remove_provider("gemini")
        assert "gemini" not in prohibition.allowed_providers

    def test_get_binding_status(self):
        """Test retrieving binding status."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        status = prohibition.get_status()
        assert "allowed_providers" in status
        assert len(status["allowed_providers"]) == 1

    def test_handle_binding_violation(self):
        """Test handling of binding violations."""
        allowed_providers = ["anthropic"]
        prohibition = ProviderSubstitutionProhibition(
            allowed_providers=allowed_providers
        )
        
        invalid_binding = {"provider": "openai"}
        
        with pytest.raises(PermissionError) as exc_info:
            prohibition.enforce(invalid_binding)
        
        assert "provider" in str(exc_info.value).lower()
