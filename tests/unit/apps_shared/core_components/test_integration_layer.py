"""
Unit tests for Integration Layer.

Tests Phase 3B - Integration Layer Implementation.
"""

from pathlib import Path

import pytest

from apps_shared.types.integration_layer_types import (
    AppDomain,
    ConfigurationLoader,
    IntegrationBridge,
    IntegrationConfig,
    ServiceEndpoint,
    ServiceRegistry,
    get_integration_bridge,
)


class TestAppDomain:
    """Test AppDomain enum."""

    def test_domain_values(self):
        """Test domain enum values."""
        assert AppDomain.LIC.value == "lic"
        assert AppDomain.RG.value == "rg"
        assert AppDomain.SHARED.value == "shared"


class TestServiceEndpoint:
    """Test ServiceEndpoint dataclass."""

    def test_endpoint_creation(self):
        """Test creating a service endpoint."""
        endpoint = ServiceEndpoint(
            name="test-service",
            domain=AppDomain.LIC,
            metadata={"key": "value"},
        )
        assert endpoint.name == "test-service"
        assert endpoint.domain == AppDomain.LIC
        assert endpoint.enabled is True
        assert endpoint.handler is None

    def test_endpoint_hash(self):
        """Test endpoint hashing for use in sets/dicts."""
        endpoint1 = ServiceEndpoint(name="svc", domain=AppDomain.LIC)
        endpoint2 = ServiceEndpoint(name="svc", domain=AppDomain.LIC)
        endpoint3 = ServiceEndpoint(name="svc", domain=AppDomain.RG)

        assert hash(endpoint1) == hash(endpoint2)
        assert hash(endpoint1) != hash(endpoint3)


class TestIntegrationConfig:
    """Test IntegrationConfig dataclass."""

    def test_config_defaults(self):
        """Test IntegrationConfig default values."""
        config = IntegrationConfig()
        assert config.config_dir == "config"
        assert config.enable_cross_domain is True
        assert config.enable_caching is True
        assert config.cache_ttl == 3600


class TestServiceRegistry:
    """Test ServiceRegistry functionality."""

    def test_register_and_get(self):
        """Test registering and getting a service."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.LIC)
        registry.register(endpoint)

        retrieved = registry.get("test", AppDomain.LIC)
        assert retrieved is endpoint

    def test_get_without_domain(self):
        """Test getting service without specifying domain."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.RG)
        registry.register(endpoint)

        retrieved = registry.get("test")
        assert retrieved is endpoint

    def test_get_nonexistent(self):
        """Test getting a nonexistent service."""
        registry = ServiceRegistry()
        result = registry.get("nonexistent", AppDomain.LIC)
        assert result is None

    def test_get_by_domain(self):
        """Test getting all services in a domain."""
        registry = ServiceRegistry()
        registry.register(ServiceEndpoint(name="svc1", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc2", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc3", domain=AppDomain.RG))

        lic_services = registry.get_by_domain(AppDomain.LIC)
        assert len(lic_services) == 2

        rg_services = registry.get_by_domain(AppDomain.RG)
        assert len(rg_services) == 1

    def test_list_all(self):
        """Test listing all services."""
        registry = ServiceRegistry()
        registry.register(ServiceEndpoint(name="svc1", domain=AppDomain.LIC))
        registry.register(ServiceEndpoint(name="svc2", domain=AppDomain.RG))

        all_services = registry.list_all()
        assert len(all_services) == 2

    def test_unregister(self):
        """Test unregistering a service."""
        registry = ServiceRegistry()
        endpoint = ServiceEndpoint(name="test", domain=AppDomain.LIC)
        registry.register(endpoint)

        result = registry.unregister("test", AppDomain.LIC)
        assert result is True

        retrieved = registry.get("test", AppDomain.LIC)
        assert retrieved is None

    def test_unregister_nonexistent(self):
        """Test unregistering a nonexistent service."""
        registry = ServiceRegistry()
        result = registry.unregister("nonexistent", AppDomain.LIC)
        assert result is False


class TestConfigurationLoader:
    """Test ConfigurationLoader functionality."""

    def test_get_config_path_shared(self):
        """Test config path generation for shared domain."""
        config = IntegrationConfig(project_root=Path("/project"))
        loader = ConfigurationLoader(config)

        path = loader._get_config_path(AppDomain.SHARED, "settings")
        # Use Path comparison for cross-platform compatibility
        expected = Path("/project") / "config" / "settings.yaml"
        assert path == expected

    def test_get_config_path_lic(self):
        """Test config path generation for LIC domain."""
        config = IntegrationConfig(project_root=Path("/project"))
        loader = ConfigurationLoader(config)

        path = loader._get_config_path(AppDomain.LIC, "agent_specs")
        expected = Path("/project") / "apps_lic" / "domain" / "config" / "agent_specs.json"
        assert path == expected

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent config file."""
        config = IntegrationConfig(project_root=Path("/nonexistent"))
        loader = ConfigurationLoader(config)

        result = loader.load("settings", AppDomain.SHARED)
        assert result == {}

    def test_caching(self):
        """Test configuration caching."""
        config = IntegrationConfig(enable_caching=True)
        loader = ConfigurationLoader(config)

        # Manually add to cache
        loader._loaded_configs["shared:test"] = {"cached": True}

        result = loader.load("test", AppDomain.SHARED)
        assert result == {"cached": True}

    def test_clear_cache_all(self):
        """Test clearing all cached configurations."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:test1"] = {}
        loader._loaded_configs["lic:test2"] = {}

        loader.clear_cache()
        assert len(loader._loaded_configs) == 0

    def test_clear_cache_by_domain(self):
        """Test clearing cached configurations by domain."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:test1"] = {}
        loader._loaded_configs["lic:test2"] = {}

        loader.clear_cache(AppDomain.LIC)

        assert "shared:test1" in loader._loaded_configs
        assert "lic:test2" not in loader._loaded_configs

    def test_get_value_nested(self):
        """Test getting nested configuration value."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:settings"] = {"database": {"host": "localhost", "port": 5432}}

        value = loader.get_value("database.host", AppDomain.SHARED, "settings")
        assert value == "localhost"

    def test_get_value_with_default(self):
        """Test getting value with default."""
        config = IntegrationConfig()
        loader = ConfigurationLoader(config)

        loader._loaded_configs["shared:settings"] = {}

        value = loader.get_value(
            "nonexistent.key",
            AppDomain.SHARED,
            "settings",
            default="default_value",
        )
        assert value == "default_value"


class TestIntegrationBridge:
    """Test IntegrationBridge functionality."""

    def test_initialization(self):
        """Test bridge initialization."""
        bridge = IntegrationBridge()
        assert bridge._initialized is False

        bridge.initialize()
        assert bridge._initialized is True

    def test_default_services_registered(self):
        """Test that default services are registered on init."""
        bridge = IntegrationBridge()
        bridge.initialize()

        services = bridge.list_services(AppDomain.SHARED)
        service_names = [s["name"] for s in services]

        assert "config" in service_names
        assert "logging" in service_names
        assert "metrics" in service_names

    def test_get_service(self):
        """Test getting a service."""
        bridge = IntegrationBridge()
        bridge.initialize()

        service = bridge.get_service("config", AppDomain.SHARED)
        assert service is not None
        assert service.name == "config"

    def test_call_service_with_handler(self):
        """Test calling a service with a handler."""
        bridge = IntegrationBridge()

        def test_handler(x, y):
            return x + y

        endpoint = ServiceEndpoint(
            name="adder",
            domain=AppDomain.LIC,
            handler=test_handler,
        )
        bridge.service_registry.register(endpoint)

        result = bridge.call_service("adder", AppDomain.LIC, 1, 2)
        assert result == 3

    def test_call_service_not_found(self):
        """Test calling a nonexistent service."""
        bridge = IntegrationBridge()

        with pytest.raises(ValueError, match="Service not found"):
            bridge.call_service("nonexistent")

    def test_call_service_disabled(self):
        """Test calling a disabled service."""
        bridge = IntegrationBridge()

        endpoint = ServiceEndpoint(
            name="disabled",
            domain=AppDomain.LIC,
            handler=lambda: None,
            enabled=False,
        )
        bridge.service_registry.register(endpoint)

        with pytest.raises(ValueError, match="Service disabled"):
            bridge.call_service("disabled", AppDomain.LIC)

    def test_call_service_no_handler(self):
        """Test calling a service without a handler."""
        bridge = IntegrationBridge()
        bridge.initialize()

        with pytest.raises(ValueError, match="has no handler"):
            bridge.call_service("config", AppDomain.SHARED)

    def test_list_services_all(self):
        """Test listing all services."""
        bridge = IntegrationBridge()
        bridge.initialize()

        services = bridge.list_services()
        assert len(services) >= 3  # At least the default services

    def test_list_services_by_domain(self):
        """Test listing services by domain."""
        bridge = IntegrationBridge()
        bridge.service_registry.register(ServiceEndpoint(name="lic-svc", domain=AppDomain.LIC))

        services = bridge.list_services(AppDomain.LIC)
        assert len(services) == 1
        assert services[0]["name"] == "lic-svc"


class TestGetIntegrationBridge:
    """Test get_integration_bridge singleton."""

    def test_singleton_instance(self):
        """Test that get_integration_bridge returns singleton."""
        import apps_shared.types.integration_layer_types as il_module

        il_module._integration_bridge = None

        bridge1 = get_integration_bridge()
        bridge2 = get_integration_bridge()

        assert bridge1 is bridge2

        il_module._integration_bridge = None
