"""Infrastructure Dependency Injection Container.

Provides dependency injection services for the atomic architecture.
"""

from typing import Any, Dict, TypeVar, Callable, Optional
import functools

T = TypeVar('T')

# Simple service registry for atomic architecture
_services: Dict[str, Any] = {}

class SimpleDIContainer:
    """Simple dependency injection container for atomic architecture."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """Register a service in the container."""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """Get a service from the container."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()

# Global container instance
_container: Optional[SimpleDIContainer] = None

def get_container() -> SimpleDIContainer:
    """Get the global DI container instance."""
    global _container
    if _container is None:
        _container = SimpleDIContainer()
    return _container

def register_service(name: str, service: Any) -> None:
    """Register a service in the global container."""
    get_container().register(name, service)

def get_service(name: str) -> Any:
    """Get a service from the global container."""
    return get_container().get(name)

def inject_dependencies(**dependencies: Any) -> Callable:
    """Decorator to inject dependencies into functions."""
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
    """Initialize default services for atomic architecture."""
    # Register default atomic services
    register_service("state_manager", None)  # Will be injected later
    register_service("safety_validator", None)  # Will be injected later
