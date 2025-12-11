"""Integration tests for API provider routing and fallbacks."""
from __future__ import annotations
import os
from unittest.mock import MagicMock, patch
import pytest
from runtime.shared.multi_provider_clients import reset_all_clients, get_available_providers, Provider, get_client

# Skip integration tests if no API keys are present - DISABLED FOR FINAL VALIDATION
# skip_if_no_keys = pytest.mark.skipif(
#     not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]),
#     reason="No API keys configured for integration tests"
# )
skip_if_no_keys = pytest.mark.skipif(False, reason="Disabled for final validation")


@skip_if_no_keys
class TestProviderRouting:
    @pytest.fixture(autouse=True)
    def reset_state(self):
        reset_all_clients()
        yield
        reset_all_clients()

    def test_available_providers_with_keys(self):
        """Returns providers that have API keys configured."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant",
        }):
            available = get_available_providers()
            assert Provider.OPENAI in available
            assert Provider.ANTHROPIC in available

    def test_client_creation_with_valid_key(self):
        """Client is created when API key is present."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("data.sdks_mcps.reference_clients.minimal_openai.AsyncOpenAI") as mock:
                mock.return_value = MagicMock()
                client = get_client(Provider.OPENAI)
                assert client is not None
                mock.assert_called_once()

    def test_provider_enum_routing(self):
        """Provider enum values map correctly for routing."""
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert Provider.GROQ.value == "groq"
        assert Provider.TOGETHER.value == "together"
