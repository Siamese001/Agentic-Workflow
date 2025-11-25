"""
Infrastructure dependency injection for résumé processing workflows.

Provides service management and dependency resolution for comprehensive résumé improvement operations.
"""

from typing import Any, Dict, TypeVar, Callable
import functools

T = TypeVar('T')

# Simple service registry for atomic architecture
_services: Dict[str, Any] = {}

def register_service(name: str, service: Any) -> None:
    """
    Registers service for résumé processing dependency injection.

    Enables modular service management for comprehensive résumé enhancement operations.
    """
    _services[name] = service

def get_service(name: str) -> Any:
    """
    Retrieves registered service for résumé processing workflows.

    Provides reliable dependency resolution for résumé improvement operations.
    """
    if name not in _services:
        raise ValueError(f"Service '{name}' not registered")
    return _services[name]

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