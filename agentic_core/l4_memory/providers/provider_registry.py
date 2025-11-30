"""
Provider Registry Module
LEVEL 5 - Registry for managing memory providers and their configurations
"""

from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from enum import Enum
from abc import ABC, abstractmethod

class ProviderStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ProviderConfig:
    """Configuration for a memory provider"""
    provider_id: str
    provider_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    enabled: bool = True
    status: ProviderStatus = ProviderStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ProviderRegistration:
    """Registration information for a provider"""
    provider_class: Type
    config: ProviderConfig
    instance: Optional[Any] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"

class MemoryProvider(ABC):
    """Abstract base class for memory providers"""

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the provider"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the provider"""
        pass

class ProviderRegistry:
    """Registry for managing memory providers"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, ProviderRegistration] = {}
        self.provider_types: Dict[str, Type[MemoryProvider]] = {}
        self.default_providers: List[str] = []

    def register_provider_type(self, provider_type: str, provider_class: Type[MemoryProvider]) -> None:
        """Register a provider type"""
        try:
            self.provider_types[provider_type] = provider_class
            self.logger.info(f"Registered provider type: {provider_type}")
        except Exception as e:
            self.logger.error(f"Failed to register provider type {provider_type}: {str(e)}")
            raise e

    async def register_provider(self, config: ProviderConfig) -> str:
        """Register and initialize a provider instance"""
        try:
            # Validate provider type
            if config.provider_type not in self.provider_types:
                raise ValueError(f"Unknown provider type: {config.provider_type}")

            # Create provider instance
            provider_class = self.provider_types[config.provider_type]
            provider_instance = provider_class()

            # Initialize provider
            init_success = await provider_instance.initialize(config.config)
            if not init_success:
                config.status = ProviderStatus.ERROR
                raise RuntimeError(f"Failed to initialize provider {config.provider_id}")

            # Register provider
            registration = ProviderRegistration(
                provider_class=provider_class,
                config=config,
                instance=provider_instance,
                last_health_check=datetime.utcnow(),
                health_status="healthy"
            )

            self.providers[config.provider_id] = registration

            # Add to default providers if high priority
            if config.priority >= 5:
                self.default_providers.append(config.provider_id)
                self.default_providers.sort(key=lambda pid: self.providers[pid].config.priority, reverse=True)

            self.logger.info(f"Registered provider: {config.provider_id}")
            return config.provider_id

        except Exception as e:
            self.logger.error(f"Failed to register provider {config.provider_id}: {str(e)}")
            raise e

    async def unregister_provider(self, provider_id: str) -> bool:
        """Unregister and shutdown a provider"""
        try:
            if provider_id not in self.providers:
                return False

            registration = self.providers[provider_id]

            # Shutdown provider
            if registration.instance:
                await registration.instance.shutdown()

            # Remove from registry
            del self.providers[provider_id]

            # Remove from default providers
            if provider_id in self.default_providers:
                self.default_providers.remove(provider_id)

            self.logger.info(f"Unregistered provider: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unregister provider {provider_id}: {str(e)}")
            return False

    def get_provider(self, provider_id: str) -> Optional[Any]:
        """Get a provider instance by ID"""
        if provider_id in self.providers:
            return self.providers[provider_id].instance
        return None

    def get_provider_config(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration by ID"""
        if provider_id in self.providers:
            return self.providers[provider_id].config
        return None

    def list_providers(self, provider_type: str = None, status: ProviderStatus = None) -> List[ProviderConfig]:
        """List providers with optional filtering"""
        providers = []

        for registration in self.providers.values():
            config = registration.config

            # Filter by type
            if provider_type and config.provider_type != provider_type:
                continue

            # Filter by status
            if status and config.status != status:
                continue

            providers.append(config)

        return providers

    def get_default_providers(self) -> List[str]:
        """Get list of default provider IDs"""
        return self.default_providers.copy()

    def set_default_providers(self, provider_ids: List[str]) -> bool:
        """Set default providers"""
        try:
            # Validate all providers exist
            for provider_id in provider_ids:
                if provider_id not in self.providers:
                    raise ValueError(f"Provider {provider_id} not found")

            self.default_providers = provider_ids.copy()
            self.logger.info(f"Set default providers: {provider_ids}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set default providers: {str(e)}")
            return False

    async def enable_provider(self, provider_id: str) -> bool:
        """Enable a provider"""
        try:
            if provider_id not in self.providers:
                return False

            registration = self.providers[provider_id]
            registration.config.enabled = True
            registration.config.status = ProviderStatus.ACTIVE
            registration.config.updated_at = datetime.utcnow()

            self.logger.info(f"Enabled provider: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to enable provider {provider_id}: {str(e)}")
            return False

    async def disable_provider(self, provider_id: str) -> bool:
        """Disable a provider"""
        try:
            if provider_id not in self.providers:
                return False

            registration = self.providers[provider_id]
            registration.config.enabled = False
            registration.config.status = ProviderStatus.INACTIVE
            registration.config.updated_at = datetime.utcnow()

            self.logger.info(f"Disabled provider: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to disable provider {provider_id}: {str(e)}")
            return False

    async def update_provider_config(self, provider_id: str, config_updates: Dict[str, Any]) -> bool:
        """Update provider configuration"""
        try:
            if provider_id not in self.providers:
                return False

            registration = self.providers[provider_id]

            # Update configuration
            registration.config.config.update(config_updates)
            registration.config.updated_at = datetime.utcnow()

            # Reinitialize provider if it has new config
            if registration.instance:
                init_success = await registration.instance.initialize(registration.config.config)
                if not init_success:
                    registration.config.status = ProviderStatus.ERROR
                    return False

                registration.config.status = ProviderStatus.ACTIVE

            self.logger.info(f"Updated configuration for provider: {provider_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update provider config {provider_id}: {str(e)}")
            return False

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all providers"""
        results = {}

        for provider_id, registration in self.providers.items():
            try:
                if registration.instance:
                    health_result = await registration.instance.health_check()
                    registration.last_health_check = datetime.utcnow()
                    registration.health_status = health_result.get("status", "unknown")
                    results[provider_id] = health_result
                else:
                    results[provider_id] = {"status": "no_instance", "error": "Provider not initialized"}

            except Exception as e:
                registration.health_status = "error"
                results[provider_id] = {"status": "error", "error": str(e)}

        return results

    async def health_check_provider(self, provider_id: str) -> Dict[str, Any]:
        """Perform health check on a specific provider"""
        try:
            if provider_id not in self.providers:
                return {"status": "not_found", "error": f"Provider {provider_id} not found"}

            registration = self.providers[provider_id]

            if not registration.instance:
                return {"status": "no_instance", "error": "Provider not initialized"}

            health_result = await registration.instance.health_check()
            registration.last_health_check = datetime.utcnow()
            registration.health_status = health_result.get("status", "unknown")

            return health_result

        except Exception as e:
            registration.health_status = "error"
            return {"status": "error", "error": str(e)}

    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get provider registry statistics"""
        status_counts = {}
        type_counts = {}

        for registration in self.providers.values():
            config = registration.config

            # Count by status
            status = config.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            # Count by type
            provider_type = config.provider_type
            type_counts[provider_type] = type_counts.get(provider_type, 0) + 1

        return {
            "total_providers": len(self.providers),
            "default_providers": len(self.default_providers),
            "registered_types": list(self.provider_types.keys()),
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "enabled_providers": sum(1 for r in self.providers.values() if r.config.enabled)
        }

    async def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all providers"""
        results = {}

        for provider_id, registration in self.providers.items():
            try:
                if registration.instance:
                    shutdown_success = await registration.instance.shutdown()
                    results[provider_id] = shutdown_success
                else:
                    results[provider_id] = True

            except Exception as e:
                self.logger.error(f"Failed to shutdown provider {provider_id}: {str(e)}")
                results[provider_id] = False

        # Clear registry
        self.providers.clear()
        self.default_providers.clear()

        return results

# Mock provider implementations for demonstration
class MockRAGProvider(MemoryProvider):
    """Mock RAG provider for testing"""

    async def initialize(self, config: Dict[str, Any]) -> bool:
        await asyncio.sleep(0.01)
        return True

    async def health_check(self) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {"status": "healthy", "documents": 100}

    async def shutdown(self) -> bool:
        await asyncio.sleep(0.01)
        return True

class MockKGProvider(MemoryProvider):
    """Mock Knowledge Graph provider for testing"""

    async def initialize(self, config: Dict[str, Any]) -> bool:
        await asyncio.sleep(0.01)
        return True

    async def health_check(self) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {"status": "healthy", "nodes": 50, "edges": 75}

    async def shutdown(self) -> bool:
        await asyncio.sleep(0.01)
        return True

__all__ = [
    "ProviderRegistry", "ProviderConfig", "ProviderRegistration",
    "MemoryProvider", "ProviderStatus", "MockRAGProvider", "MockKGProvider"
]
