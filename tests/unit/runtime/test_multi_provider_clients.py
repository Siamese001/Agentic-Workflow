"""Unit tests for runtime/shared/multi_provider_clients.py"""
import os
import pytest
from runtime.shared.multi_provider_clients import Provider, get_api_key, get_client, reset_all_clien
    ts, ProviderConfig, DEFAULT_MAX_RETRIES

class TestProviderEnum:
    """TODO: Add docstring."""

        """TODO: Add docstring."""

    def test_provider_values(self):
        """Docstring."""
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert isinstance(Provider.OPENAI, str)
        """TODO: Add docstring."""


    def test_provider_iteration_determinism(self):
        """Docstring."""
        assert list(Provider) == list(Provider)
        """TODO: Add docstring."""


    """TODO: Add docstring."""

class TestGetApiKey:
        """TODO: Add docstring."""

    def test_success(self):
        """Docstring."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            assert get_api_key(Provider.OPENAI) == "sk-test"

    def test_missing_raises(self):
        """TODO: Add docstring."""

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="not set"):
                get_api_key(Provider.OPENAI)
        """TODO: Add docstring."""


    def test_determinism(self):
        """Docstring."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant"}):
            assert get_api_key(Provider.ANTHROPIC) == get_api_key(Provider.ANTHROPIC)
    """TODO: Add docstring."""


class TestGetClient:
    """Docstring."""
    def test_singleton(self):
        """Docstring."""
        reset_all_clients()
        """TODO: Add docstring."""

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("runtime.shared.multi_provider_clients._create_client") as m:
                mock_client = MagicMock()
                m.return_value = mock_client
                c1, c2 = get_client(Provider.OPENAI), get_client(Provider.OPENAI)
                assert c1 is c2
                assert m.call_count == 1
        """TODO: Add docstring."""


    def test_missing_key_raises(self):
        """Docstring."""
        reset_all_clients()
        with patch.dict(os.environ, {}, clear=True):
        """TODO: Add docstring."""

            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError):
    """TODO: Add docstring."""

                get_client(Provider.OPENAI)

class TestProviderConfig:
    """Docstring."""
    def test_defaults(self):
        """Docstring."""
        cfg = ProviderConfig()
        assert cfg.max_retries == DEFAULT_MAX_RETRIES
        assert cfg.timeout > 0

    def test_custom(self):
        """Docstring."""
        cfg = ProviderConfig(max_retries=3, timeout=30.0)
        assert cfg.max_retries == 3
