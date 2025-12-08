"""Unit tests for runtime/shared/sdk_registry.py"""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest

from agentic_workflow.runtime.shared.sdk_registry import (
    SDKCategory, SDKEntry, SDK_REGISTRY, validate_sdk,
    ChromaConfig, RedisConfig, get_vector_store, get_redis_client, reset_all_clients,
)

class TestSDKRegistry:
    def test_contains_core_sdks(self):
        for sdk in ["openai", "anthropic", "chromadb", "redis", "mcp"]:
            assert sdk in SDK_REGISTRY

    def test_entries_are_sdk_entry(self):
        for name, entry in SDK_REGISTRY.items():
            assert isinstance(entry, SDKEntry)
            assert entry.name == name

    def test_determinism(self):
        assert list(SDK_REGISTRY.keys()) == list(SDK_REGISTRY.keys())

class TestValidateSDK:
    def test_installed_package(self):
        success, err = validate_sdk("openai")
        assert success is True
        assert err is None

    def test_unknown_sdk(self):
        success, err = validate_sdk("nonexistent_xyz")
        assert success is False
        assert "Unknown SDK" in err

class TestGetVectorStore:
    def test_chromadb_singleton(self):
        reset_all_clients()
        with patch("agentic_workflow.runtime.shared.sdk_registry.chromadb") as m:
            m.Client.return_value = MagicMock()
            c1, c2 = get_vector_store("chromadb"), get_vector_store("chromadb")
            assert c1 is c2

    def test_invalid_provider(self):
        reset_all_clients()
        with pytest.raises(ValueError, match="Unknown"):
            get_vector_store("invalid_db")

class TestGetRedisClient:
    def test_default_config(self):
        reset_all_clients()
        with patch("agentic_workflow.runtime.shared.sdk_registry.redis") as m:
            m.Redis.return_value = MagicMock()
            client = get_redis_client()
            m.Redis.assert_called_once()
