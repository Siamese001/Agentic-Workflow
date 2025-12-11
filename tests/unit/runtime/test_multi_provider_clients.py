"""Unit tests for runtime/shared/multi_provider_clients.py"""
from __future__ import annotations
import os
from unittest.mock import MagicMock, patch
import pytest


class TestProviderEnum:
    def test_provider_values(self):
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert isinstance(Provider.OPENAI, str)

    def test_provider_iteration_determinism(self):
        assert list(Provider) == list(Provider)

class TestGetApiKey:
    def test_success(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            assert get_api_key(Provider.OPENAI) == "sk-test"

    def test_missing_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError, match="not set"):
                get_api_key(Provider.OPENAI)

    def test_determinism(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant"}):
            assert get_api_key(Provider.ANTHROPIC) == get_api_key(Provider.ANTHROPIC)

class TestGetClient:
    def test_singleton(self):
        reset_all_clients()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("agentic_workflow.runtime.shared.multi_provider_clients.AsyncOpenAI") as m:
                m.return_value = MagicMock()
                c1, c2 = get_client(Provider.OPENAI), get_client(Provider.OPENAI)
                assert c1 is c2
                assert m.call_count == 1

    def test_missing_key_raises(self):
        reset_all_clients()
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with pytest.raises(ValueError):
                get_client(Provider.OPENAI)

class TestProviderConfig:
    def test_defaults(self):
        cfg = ProviderConfig()
        assert cfg.max_retries == DEFAULT_MAX_RETRIES
        assert cfg.timeout > 0

    def test_custom(self):
        cfg = ProviderConfig(max_retries=3, timeout=30.0)
        assert cfg.max_retries == 3
