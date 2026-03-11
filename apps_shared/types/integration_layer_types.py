"""
Integration Layer - Connects apps_lic and apps_rg with shared infrastructure.

Provides unified configuration loading, service discovery, and cross-app
communication patterns.
Phase 3B - Integration Layer Implementation
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class AppDomain(str, Enum):
    """Application domains."""

    LIC = "lic"
    RG = "rg"
    SHARED = "shared"


@dataclass
class ServiceEndpoint:
    """Represents a service endpoint."""

    name: str
    domain: AppDomain
    handler: Callable[..., Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __hash__(self):
        return hash(f"{self.domain.value}:{self.name}")


@dataclass
class IntegrationConfig:
    """Configuration for integration layer."""

    project_root: Path = field(default_factory=lambda: Path.cwd())
    config_dir: str = "config"
    enable_cross_domain: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600


class ServiceRegistry:
    """Registry for managing service endpoints across domains."""

    def __init__(self):
        self._services: dict[str, ServiceEndpoint] = {}
        self._domain_services: dict[AppDomain, list[str]] = {
            AppDomain.LIC: [],
            AppDomain.RG: [],
            AppDomain.SHARED: [],
        }

    def register(self, endpoint: ServiceEndpoint) -> None:
        """Register a service endpoint."""
        key = f"{endpoint.domain.value}:{endpoint.name}"
        self._services[key] = endpoint
        if key not in self._domain_services[endpoint.domain]:
            self._domain_services[endpoint.domain].append(key)
        logger.info(f"Registered service: {key}")

    def get(self, name: str, domain: AppDomain | None = None) -> ServiceEndpoint | None:
        """Get a service endpoint by name and optional domain."""
        if domain:
            key = f"{domain.value}:{name}"
            return self._services.get(key)

        # Search all domains
        for d in AppDomain:
            key = f"{d.value}:{name}"
            if key in self._services:
                return self._services[key]

        return None

    def get_by_domain(self, domain: AppDomain) -> list[ServiceEndpoint]:
        """Get all services in a domain."""
        return [self._services[key] for key in self._domain_services[domain] if key in self._services]

    def list_all(self) -> list[ServiceEndpoint]:
        """List all registered services."""
        return list(self._services.values())

    def unregister(self, name: str, domain: AppDomain) -> bool:
        """Unregister a service endpoint."""
        key = f"{domain.value}:{name}"
        if key in self._services:
            del self._services[key]
            if key in self._domain_services[domain]:
                self._domain_services[domain].remove(key)
            logger.info(f"Unregistered service: {key}")
            return True
        return False


class ConfigurationLoader:
    """Loads and manages configuration across domains."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self._loaded_configs: dict[str, dict[str, Any]] = {}

    def _get_config_path(self, domain: AppDomain, config_name: str) -> Path:
        """Get the path to a configuration file."""
        if domain == AppDomain.SHARED:
            return self.config.project_root / self.config.config_dir / f"{config_name}.yaml"
        return self.config.project_root / f"apps_{domain.value}" / "domain" / "config" / f"{config_name}.json"

    def load(
        self,
        config_name: str,
        domain: AppDomain = AppDomain.SHARED,
    ) -> dict[str, Any]:
        """Load a configuration file."""
        cache_key = f"{domain.value}:{config_name}"

        if self.config.enable_caching and cache_key in self._loaded_configs:
            return self._loaded_configs[cache_key]

        config_path = self._get_config_path(domain, config_name)

        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return {}

        try:
            if config_path.suffix == ".json":
                import json

                with open(config_path) as f:
                    config_data = json.load(f)
            elif config_path.suffix in (".yaml", ".yml"):
                try:
                    import yaml

                    with open(config_path) as f:
                        config_data = yaml.safe_load(f) or {}
                except ImportError:
                    logger.warning("PyYAML not installed, cannot load YAML configs")
                    config_data = {}
            else:
                logger.warning(f"Unsupported config format: {config_path.suffix}")
                config_data = {}

            if self.config.enable_caching:
                self._loaded_configs[cache_key] = config_data

            logger.debug(f"Loaded configuration: {config_path}")
            return config_data

        except Exception as e:
            logger.error(f"Failed to load configuration {config_path}: {e}")
            return {}

    def get_value(
        self,
        key: str,
        domain: AppDomain = AppDomain.SHARED,
        config_name: str = "settings",
        default: Any = None,
    ) -> Any:
        """Get a specific configuration value."""
        config = self.load(config_name, domain)
        keys = key.split(".")

        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def clear_cache(self, domain: AppDomain | None = None) -> None:
        """Clear cached configurations."""
        if domain:
            keys_to_remove = [k for k in self._loaded_configs if k.startswith(f"{domain.value}:")]
            for k in keys_to_remove:
                del self._loaded_configs[k]
        else:
            self._loaded_configs.clear()


class IntegrationBridge:
    """
    Main integration bridge connecting apps_lic and apps_rg.

    Provides:
    - Service discovery and routing
    - Configuration management
    - Cross-domain communication
    """

    def __init__(self, config: IntegrationConfig | None = None):
        self.config = config or IntegrationConfig()
        self.service_registry = ServiceRegistry()
        self.config_loader = ConfigurationLoader(self.config)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the integration bridge."""
        if self._initialized:
            return

        logger.info("Initializing integration bridge...")

        # Register default shared services
        self._register_default_services()

        self._initialized = True
        logger.info("Integration bridge initialized")

    def _register_default_services(self) -> None:
        """Register default shared services."""
        # These are placeholder services that can be overridden
        default_services = [
            ServiceEndpoint(
                name="config",
                domain=AppDomain.SHARED,
                metadata={"description": "Configuration service"},
            ),
            ServiceEndpoint(
                name="logging",
                domain=AppDomain.SHARED,
                metadata={"description": "Logging service"},
            ),
            ServiceEndpoint(
                name="metrics",
                domain=AppDomain.SHARED,
                metadata={"description": "Metrics collection service"},
            ),
        ]

        for service in default_services:
            self.service_registry.register(service)

    def get_service(
        self,
        name: str,
        domain: AppDomain | None = None,
    ) -> ServiceEndpoint | None:
        """Get a service endpoint."""
        self.initialize()
        return self.service_registry.get(name, domain)

    def call_service(
        self,
        name: str,
        domain: AppDomain | None = None,
        *args,
        **kwargs,
    ) -> Any:
        """Call a service handler."""
        endpoint = self.get_service(name, domain)

        if not endpoint:
            raise ValueError(f"Service not found: {name}")

        if not endpoint.enabled:
            raise ValueError(f"Service disabled: {name}")

        if not endpoint.handler:
            raise ValueError(f"Service has no handler: {name}")

        return endpoint.handler(*args, **kwargs)

    def load_config(
        self,
        config_name: str,
        domain: AppDomain = AppDomain.SHARED,
    ) -> dict[str, Any]:
        """Load a configuration."""
        return self.config_loader.load(config_name, domain)

    def get_config_value(
        self,
        key: str,
        domain: AppDomain = AppDomain.SHARED,
        config_name: str = "settings",
        default: Any = None,
    ) -> Any:
        """Get a configuration value."""
        return self.config_loader.get_value(key, domain, config_name, default)

    def list_services(self, domain: AppDomain | None = None) -> list[dict[str, Any]]:
        """List registered services."""
        self.initialize()

        if domain:
            services = self.service_registry.get_by_domain(domain)
        else:
            services = self.service_registry.list_all()

        return [
            {
                "name": s.name,
                "domain": s.domain.value,
                "enabled": s.enabled,
                "metadata": s.metadata,
            }
            for s in services
        ]


# Singleton instance
_integration_bridge: IntegrationBridge | None = None


def get_integration_bridge() -> IntegrationBridge:
    """Get the singleton integration bridge instance."""
    global _integration_bridge
    if _integration_bridge is None:
        _integration_bridge = IntegrationBridge()
    return _integration_bridge
