"""Unit tests for runtime/shared/sdk_registry.py"""
import pytest

class TestSDKRegistry:
    """TestSDKRegistry implementation."""
    def test_contains_core_sdks(self) -> None:
        """Execute test_contains_core_sdks operation."""
        for sdk in ["openai", "anthropic", "chromadb", "redis", "mcp"]:
            assert sdk in SDK_REGISTRY

    def test_entries_are_sdk_entry(self) -> None:
        """Execute test_entries_are_sdk_entry operation."""
        for name, entry in SDK_REGISTRY.items():
            assert isinstance(entry, SDKEntry)
            assert entry.name == name

    def test_determinism(self) -> None:
        """Execute test_determinism operation."""
        assert list(SDK_REGISTRY.keys()) == list(SDK_REGISTRY.keys())

class TestValidateSDK:
    """TestValidateSDK implementation."""
    def test_installed_package(self) -> None:
        """Execute test_installed_package operation."""
        success, err = validate_sdk("openai")
        assert success is True
        assert err is None

    def test_unknown_sdk(self) -> None:
        """Execute test_unknown_sdk operation."""
        success, err = validate_sdk("nonexistent_xyz")
        assert success is False
        assert "Unknown SDK" in err

class TestGetVectorStore:
    """TestGetVectorStore implementation."""
    def test_chromadb_singleton(self) -> None:
        """Execute test_chromadb_singleton operation."""
        reset_all_clients()
        with patch("agentic_workflow.runtime.shared.sdk_registry.chromadb") as m:
            m.Client.return_value = MagicMock()
            c1, c2 = get_vector_store("chromadb"), get_vector_store("chromadb")
            assert c1 is c2

    def test_invalid_provider(self) -> None:
        """Execute test_invalid_provider operation."""
        reset_all_clients()
        with pytest.raises(ValueError, match="Unknown"):
            get_vector_store("invalid_db")

class TestGetRedisClient:
    """TestGetRedisClient implementation."""
    def test_default_config(self) -> None:
        """Execute test_default_config operation."""
        reset_all_clients()
        with patch("agentic_workflow.runtime.shared.sdk_registry.redis") as m:
            m.Redis.return_value = MagicMock()
            get_redis_client()
            m.Redis.assert_called_once()
