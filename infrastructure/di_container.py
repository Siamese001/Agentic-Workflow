"""
Infrastructure dependency injection for résumé processing workflows.

Provides service management and dependency resolution for comprehensive résumé improvement operations.
"""

from typing import Any, Dict, TypeVar, Callable, Optional
import functools

T = TypeVar('T')

# Simple service registry for atomic architecture
_services: Dict[str, Any] = {}

class SimpleDIContainer:
    """
    Manages dependency injection services for résumé processing architecture.

    Ensures proper service resolution and lifecycle management for résumé improvement workflows.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """
        Registers service for résumé processing dependency injection.

        Enables modular service management for comprehensive résumé enhancement operations.
        """
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """
        Retrieves registered service for résumé processing workflows.

        Provides reliable dependency resolution for résumé improvement operations.
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """
        Checks service registration status for résumé processing.

        Validates service availability for résumé improvement workflows.
        """
        return name in self._services
    
    def clear(self) -> None:
        """
        Clears all registered services for résumé processing.

        Resets dependency container for fresh résumé improvement workflow initialization.
        """
        self._services.clear()

# Global container instance
_container: Optional[SimpleDIContainer] = None

def get_container() -> SimpleDIContainer:
    """
    Retrieves global dependency container for résumé processing.

    Ensures consistent service management across résumé improvement workflows.
    """
    global _container
    if _container is None:
        _container = SimpleDIContainer()
    return _container

def register_service(name: str, service: Any) -> None:
    """
    Registers service in global container for résumé processing.

    Enables centralized service management for comprehensive résumé enhancement operations.
    """
    get_container().register(name, service)

def get_service(name: str) -> Any:
    """
    Retrieves service from global container for résumé workflows.

    Provides consistent dependency access for résumé improvement processing.
    """
    return get_container().get(name)

def inject_dependencies(**dependencies: Any) -> Callable:
    """
    Creates dependency injection decorator for résumé processing functions.

    Enables automatic service resolution for modular résumé improvement workflows.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Inject dependencies
            for key, service_name in dependencies.items():
                if key not in kwargs:
                    kwargs[key] = get_service(service_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def initialize_default_services() -> None:
    """
    Initializes default services for résumé processing architecture.

    Sets up essential dependencies for comprehensive résumé improvement workflows.
    """
    # Register default atomic services
    register_service("state_manager", None)  # Will be injected later
    register_service("safety_validator", None)  # Will be injected later
