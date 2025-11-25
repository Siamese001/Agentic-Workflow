"""Infrastructure Dependency Injection Container.

Provides dependency injection services for the atomic architecture.
"""

from typing import Any, Dict, TypeVar, Callable, Optional
import functools

T = TypeVar('T')

# Simple service registry for atomic architecture
_services: Dict[str, Any] = {}

def register_service(name: str, service: Any) -> None:
    """Register a service in the container."""
    _services[name] = service

def get_service(name: str) -> Any:
    """Get a service from the container."""
    if name not in _services:
        raise ValueError(f"Service '{name}' not registered")
    return _services[name]

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
