"""Dependency Injection Container

Provides centralized dependency injection for all layers to enforce
strict L1-L5 atomicity and prevent direct service imports.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, TypeVar, Protocol, runtime_checkable
from dataclasses import dataclass, field
import logging

from l4.pinecone_adapter import PineconeAdapter
from l4.manager import StateManager
from l5.policy import SafetyEngine

logger = logging.getLogger(__name__)

T = TypeVar('T')


@runtime_checkable
class DIContainer(Protocol):
    """Protocol for dependency injection containers."""
    
    def get(self, service_type: type[T]) -> Optional[T]:
        """Get a service instance by type."""
        ...
    
    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance."""
        ...


@dataclass
class SimpleDIContainer:
    """Simple dependency injection container."""
    
    _services: Dict[type, Any] = field(default_factory=dict)
    
    def get(self, service_type: type[T]) -> Optional[T]:
        """Get a service instance by type."""
        return self._services.get(service_type)
    
    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance."""
        if service_type in self._services:
            raise ValueError(f"Service type {service_type.__name__} is already registered")
        self._services[service_type] = instance
        logger.debug(f"Registered service: {service_type.__name__}")
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()


# Global container instance
_global_container: Optional[SimpleDIContainer] = None


def get_container() -> SimpleDIContainer:
    """Get the global DI container."""
    global _global_container
    if _global_container is None:
        _global_container = SimpleDIContainer()
    return _global_container


def register_service(service_type: type[T], instance: T) -> None:
    """Register a service in the global container."""
    get_container().register(service_type, instance)


def get_service(service_type: type[T]) -> Optional[T]:
    """Get a service from the global container."""
    return get_container().get(service_type)


def initialize_default_services() -> None:
    """Initialize default services for the container."""
    container = get_container()
    
    # Register L4 services
    if not container.get(PineconeAdapter):
        from l4.pinecone_adapter import PineconeConfig
        pinecone_config = PineconeConfig(
            api_key="dummy-key",
            index_name="test-index"
        )
        container.register(PineconeAdapter, PineconeAdapter(pinecone_config))
    
    # Register L5 services  
    if not container.get(SafetyEngine):
        container.register(SafetyEngine, SafetyEngine())


def inject_dependencies(ctx: Any) -> Any:
    """Inject dependencies into execution context.
    
    This ensures all layers consume services via DI, not direct imports.
    
    Args:
        ctx: Execution context to inject into
        
    Returns:
        Context with injected dependencies
    """
    container = get_container()
    
    # Inject L4 services
    pinecone_adapter = container.get(PineconeAdapter)
    if pinecone_adapter and not hasattr(ctx, 'pinecone_adapter'):
        ctx.pinecone_adapter = pinecone_adapter
    
    state_manager = container.get(StateManager)
    if state_manager and not hasattr(ctx, 'state_manager'):
        ctx.state_manager = state_manager
    
    # Inject L5 services
    safety_engine = container.get(SafetyEngine)
    if safety_engine and not hasattr(ctx, 'safety_engine'):
        ctx.safety_engine = safety_engine
    
    return ctx


__all__ = [
    'DIContainer',
    'SimpleDIContainer', 
    'get_container',
    'register_service',
    'get_service',
    'initialize_default_services',
    'inject_dependencies',
]



