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
        Registers service for résumé processing workflows.

        Enables modular service management for comprehensive résumé enhancement operations.
        """
        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered")
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """
        Retrieves registered service for résumé processing workflows.

        Provides reliable dependency resolution for résumé improvement operations.
        Returns None if service is not registered.
        """
        return self._services.get(name)
    
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

def inject_dependencies(context: Any) -> Any:
    """
    Injects dependencies into a context object for résumé processing workflows.
    
    Args:
        context: The context object to inject services into
        
    Returns:
        The context object with services injected
    """
    container = get_container()
    
    # Inject common services if they don't already exist
    if not hasattr(context, 'pinecone_adapter'):
        from l4.pinecone_adapter import PineconeAdapter, PineconeConfig
        adapter = container.get(PineconeAdapter)
        if adapter is None:
            config = PineconeConfig(
                api_key="test_key",
                index_name="test_index",
                environment="test"
            )
            adapter = PineconeAdapter(config)
            container.register(PineconeAdapter, adapter)
        context.pinecone_adapter = adapter
    
    if not hasattr(context, 'safety_engine'):
        from l5.policy import SafetyEngine
        engine = container.get(SafetyEngine)
        if engine is None:
            engine = SafetyEngine()
            container.register(SafetyEngine, engine)
        context.safety_engine = engine
    
    if not hasattr(context, 'state_manager'):
        # Add state manager if available
        state_manager = container.get('state_manager')
        if state_manager:
            context.state_manager = state_manager
    
    return context


def inject_dependencies_decorator(**dependencies: Any) -> Callable:
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
    # Clear existing services to avoid duplicate registration
    container = get_container()
    container.clear()
    
    # Register PineconeAdapter with default config
    from l4.pinecone_adapter import PineconeAdapter, PineconeConfig
    config = PineconeConfig(
        api_key="test_key",
        index_name="test_index"
    )
    adapter = PineconeAdapter(config)
    register_service("pinecone_adapter", adapter)
    register_service(PineconeAdapter, adapter)
    
    # Register SafetyEngine
    from l5.policy import SafetyEngine
    engine = SafetyEngine()
    register_service("safety_engine", engine)
    register_service(SafetyEngine, engine)
    
    # Register other default services
    register_service("state_manager", None)
    register_service("safety_validator", None)
