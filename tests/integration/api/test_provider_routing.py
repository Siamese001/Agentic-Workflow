"""Integration tests for API provider routing and fallbacks."""
from __future__ import annotations
import os
from unittest.mock import MagicMock, patch
import pytest

from agentic_workflow.runtime.shared.multi_provider_clients import (
    Provider, get_client, get_available_providers, reset_all_clients,
)

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
            with patch("agentic_workflow.runtime.shared.multi_provider_clients.AsyncOpenAI") as mock:
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
