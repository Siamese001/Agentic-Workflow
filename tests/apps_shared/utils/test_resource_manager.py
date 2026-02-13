"""
Unit tests for Resource Manager.

Tests Phase 2B - Resource Management & Namespacing.
"""

import json
import time
from unittest.mock import MagicMock, patch

import pytest
from apps_shared.utils.resource_types import (
    ResourceConfig,
    ResourceKey,
    ResourceManager,
    ResourceNamespace,
    get_resource_manager,
)


class TestResourceNamespace:
    """Test ResourceNamespace enum."""

    def test_namespace_values(self):
        """Test namespace enum values."""
        assert ResourceNamespace.LIC.value == "lic"
        assert ResourceNamespace.RG.value == "rg"
        assert ResourceNamespace.SHARED.value == "shared"
        assert ResourceNamespace.SYSTEM.value == "system"


class TestResourceConfig:
    """Test ResourceConfig dataclass."""

    def test_config_defaults(self):
        """Test ResourceConfig default values."""
        config = ResourceConfig()
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_db == 0
        assert config.redis_password is None
        assert config.default_ttl == 3600
        assert config.namespace_prefix == "agentic"
        assert config.enable_redis is True

    def test_config_custom_values(self):
        """Test ResourceConfig with custom values."""
        config = ResourceConfig(
            redis_host="redis.example.com",
            redis_port=6380,
            redis_db=1,
            redis_password="secret",
            default_ttl=7200,
            namespace_prefix="custom",
            enable_redis=False,
        )
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380
        assert config.redis_db == 1
        assert config.redis_password == "secret"
        assert config.default_ttl == 7200
        assert config.namespace_prefix == "custom"
        assert config.enable_redis is False


class TestResourceKey:
    """Test ResourceKey dataclass."""

    def test_key_string_generation(self):
        """Test ResourceKey string representation."""
        key = ResourceKey(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="user123",
        )
        assert str(key) == "agentic:lic:cache:user123"

    def test_key_with_custom_prefix(self):
        """Test ResourceKey with custom prefix."""
        key = ResourceKey(
            namespace=ResourceNamespace.RG,
            category="state",
            identifier="session456",
            prefix="custom",
        )
        assert str(key) == "custom:rg:state:session456"

    def test_key_parse(self):
        """Test ResourceKey parsing from string."""
        key = ResourceKey.parse("agentic:shared:config:settings")
        assert key.prefix == "agentic"
        assert key.namespace == ResourceNamespace.SHARED
        assert key.category == "config"
        assert key.identifier == "settings"

    def test_key_parse_invalid(self):
        """Test ResourceKey parsing with invalid string."""
        with pytest.raises(ValueError, match="Invalid resource key format"):
            ResourceKey.parse("invalid:key")


class TestResourceManagerInMemory:
    """Test ResourceManager with in-memory cache (Redis disabled)."""

    def test_initialization(self):
        """Test ResourceManager initialization."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)
        assert manager.config == config
        assert manager._initialized is False

    def test_set_and_get(self):
        """Test setting and getting a resource."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        result = manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="test1",
            value={"data": "value"},
        )
        assert result is True

        retrieved = manager.get(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="test1",
        )
        assert retrieved == {"data": "value"}

    def test_get_nonexistent(self):
        """Test getting a nonexistent resource."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        result = manager.get(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="nonexistent",
        )
        assert result is None

    def test_delete(self):
        """Test deleting a resource."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        manager.set(
            namespace=ResourceNamespace.RG,
            category="state",
            identifier="test2",
            value="test_value",
        )

        result = manager.delete(
            namespace=ResourceNamespace.RG,
            category="state",
            identifier="test2",
        )
        assert result is True

        retrieved = manager.get(
            namespace=ResourceNamespace.RG,
            category="state",
            identifier="test2",
        )
        assert retrieved is None

    def test_exists(self):
        """Test checking resource existence."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        manager.set(
            namespace=ResourceNamespace.SHARED,
            category="config",
            identifier="test3",
            value=123,
        )

        assert manager.exists(
            namespace=ResourceNamespace.SHARED,
            category="config",
            identifier="test3",
        )

        assert not manager.exists(
            namespace=ResourceNamespace.SHARED,
            category="config",
            identifier="nonexistent",
        )

    def test_ttl_expiration(self):
        """Test TTL expiration in memory cache."""
        config = ResourceConfig(enable_redis=False, default_ttl=1)
        manager = ResourceManager(config)

        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="expiring",
            value="will_expire",
            ttl=1,
        )

        # Should exist immediately
        assert manager.exists(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="expiring",
        )

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        assert not manager.exists(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="expiring",
        )

    def test_namespace_isolation(self):
        """Test that namespaces are isolated."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        # Set same identifier in different namespaces
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="shared_id",
            value="lic_value",
        )
        manager.set(
            namespace=ResourceNamespace.RG,
            category="cache",
            identifier="shared_id",
            value="rg_value",
        )

        # Values should be different
        lic_value = manager.get(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="shared_id",
        )
        rg_value = manager.get(
            namespace=ResourceNamespace.RG,
            category="cache",
            identifier="shared_id",
        )

        assert lic_value == "lic_value"
        assert rg_value == "rg_value"

    def test_clear_namespace(self):
        """Test clearing a namespace."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        # Add resources to multiple namespaces
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item1",
            value="value1",
        )
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item2",
            value="value2",
        )
        manager.set(
            namespace=ResourceNamespace.RG,
            category="cache",
            identifier="item3",
            value="value3",
        )

        # Clear LIC namespace
        count = manager.clear_namespace(ResourceNamespace.LIC)
        assert count == 2

        # LIC resources should be gone
        assert not manager.exists(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item1",
        )
        assert not manager.exists(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item2",
        )

        # RG resource should still exist
        assert manager.exists(
            namespace=ResourceNamespace.RG,
            category="cache",
            identifier="item3",
        )

    def test_get_namespace_stats(self):
        """Test getting namespace statistics."""
        config = ResourceConfig(enable_redis=False)
        manager = ResourceManager(config)

        # Add resources
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item1",
            value="value1",
        )
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="state",
            identifier="item2",
            value="value2",
        )
        manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="item3",
            value="value3",
        )

        stats = manager.get_namespace_stats(ResourceNamespace.LIC)

        assert stats["namespace"] == "lic"
        assert stats["key_count"] == 3
        assert stats["categories"]["cache"] == 2
        assert stats["categories"]["state"] == 1


class TestResourceManagerRedis:
    """Test ResourceManager with mocked Redis."""

    def test_redis_initialization(self):
        """Test Redis initialization."""
        config = ResourceConfig(enable_redis=True)
        manager = ResourceManager(config)

        # Mock Redis
        manager._redis_client = MagicMock()
        manager._redis_client.ping.return_value = True
        manager._initialized = True

        assert manager._redis_client is not None

    def test_set_with_redis(self):
        """Test set operation with Redis."""
        config = ResourceConfig(enable_redis=True)
        manager = ResourceManager(config)

        # Mock Redis
        mock_redis = MagicMock()
        manager._redis_client = mock_redis
        manager._initialized = True

        result = manager.set(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="test",
            value={"key": "value"},
            ttl=3600,
        )

        assert result is True
        mock_redis.setex.assert_called_once()

    def test_get_with_redis(self):
        """Test get operation with Redis."""
        config = ResourceConfig(enable_redis=True)
        manager = ResourceManager(config)

        # Mock Redis
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps({"key": "value"})
        manager._redis_client = mock_redis
        manager._initialized = True

        result = manager.get(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="test",
        )

        assert result == {"key": "value"}
        mock_redis.get.assert_called_once()

    def test_delete_with_redis(self):
        """Test delete operation with Redis."""
        config = ResourceConfig(enable_redis=True)
        manager = ResourceManager(config)

        # Mock Redis
        mock_redis = MagicMock()
        manager._redis_client = mock_redis
        manager._initialized = True

        result = manager.delete(
            namespace=ResourceNamespace.LIC,
            category="cache",
            identifier="test",
        )

        assert result is True
        mock_redis.delete.assert_called_once()


class TestGetResourceManager:
    """Test get_resource_manager singleton."""

    def test_singleton_instance(self):
        """Test that get_resource_manager returns singleton."""
        # Reset singleton for test
        import apps_shared.utils.resource_types as rm_module

        rm_module._resource_manager = None

        with patch.dict(
            "os.environ",
            {"ENABLE_REDIS": "false"},
            clear=False,
        ):
            manager1 = get_resource_manager()
            manager2 = get_resource_manager()

            assert manager1 is manager2

        # Reset singleton after test
        rm_module._resource_manager = None
