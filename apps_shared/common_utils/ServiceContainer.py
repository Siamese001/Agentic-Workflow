"""Service Container - Dependency Injection System.

This module implements a lightweight dependency injection container to eliminate
global singletons and improve testability. Services are registered by type
and resolved as needed throughout the application.
"""

import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""

    pass


class ServiceContainer:
    """Simple dependency injection container.

    Supports:
    - Type-based registration and resolution
    - Factory functions for lazy initialization
    - Singleton instances (default)
    - Transient instances (new each time)
    """

    def __init__(self, name: str = "default"):
        """Initialize the container.

        Args:
            name: Optional name for the container (useful for debugging)
        """
        self.name = name
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
        self._singletons: dict[type, Any] = {}
        self._lifecycle: dict[type, str] = {}  # "singleton" or "transient"

    def register(
        self,
        interface: type[T],
        implementation: T | None = None,
        factory: Callable[[], T] | None = None,
        lifecycle: str = "singleton",
    ) -> None:
        """Register a service in the container.

        Args:
            interface: The type/class to register
            implementation: Optional instance to use (for singletons)
            factory: Optional factory function to create instances
            lifecycle: "singleton" (default) or "transient"

        Raises:
            ValueError: If neither implementation nor factory is provided
        """
        if implementation is None and factory is None:
            raise ValueError("Must provide either implementation or factory")

        if lifecycle not in ["singleton", "transient"]:
            raise ValueError("Lifecycle must be 'singleton' or 'transient'")

        self._lifecycle[interface] = lifecycle

        if implementation is not None:
            if lifecycle == "singleton":
                self._singletons[interface] = implementation
            else:
                self._services[interface] = implementation

        if factory is not None:
            self._factories[interface] = factory

        logger.debug(f"Registered {interface.__name__} in container '{self.name}'")

    def resolve(self, interface: type[T]) -> T:
        """Resolve a service from the container.

        Args:
            interface: The type/class to resolve

        Returns:
            An instance of the requested type

        Raises:
            ServiceNotFoundError: If the service is not registered
        """
        # Check if service is registered
        if interface not in self._lifecycle:
            raise ServiceNotFoundError(f"{interface.__name__} not registered in container")

        lifecycle = self._lifecycle[interface]

        # Handle singleton lifecycle
        if lifecycle == "singleton":
            if interface in self._singletons:
                return self._singletons[interface]

            # Create singleton if not exists
            if interface in self._factories:
                instance = self._factories[interface]()
                self._singletons[interface] = instance
                return instance

            if interface in self._services:
                return self._services[interface]

        # Handle transient lifecycle
        if lifecycle == "transient":
            if interface in self._factories:
                return self._factories[interface]()

            if interface in self._services:
                # For transient, we need to create a copy if possible
                implementation = self._services[interface]
                try:
                    return type(implementation)()
                except Exception:
                    # If we can't create a new instance, return the original
                    logger.warning(
                        f"Could not create transient instance of {interface.__name__}, returning singleton"
                    )
                    return implementation

        raise ServiceNotFoundError(f"Could not resolve {interface.__name__}")

    def is_registered(self, interface: type) -> bool:
        """Check if a service is registered.

        Args:
            interface: The type/class to check

        Returns:
            True if registered, False otherwise
        """
        return interface in self._lifecycle

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._lifecycle.clear()
        logger.debug(f"Cleared all services from container '{self.name}'")

    def list_services(self) -> dict[type, str]:
        """List all registered services and their lifecycles.

        Returns:
            Dictionary mapping types to lifecycle names
        """
        return self._lifecycle.copy()


# Global default container for backward compatibility
_default_container: ServiceContainer | None = None


def get_default_container() -> ServiceContainer:
    """Get the default container instance.

    Returns:
        The default ServiceContainer
    """
    global _default_container
    if _default_container is None:
        _default_container = ServiceContainer("default")
    return _default_container


def register_default(
    interface: type[T],
    implementation: T | None = None,
    factory: Callable[[], T] | None = None,
    lifecycle: str = "singleton",
) -> None:
    """Register a service in the default container.

    This is a convenience function for global registration.

    Args:
        interface: The type/class to register
        implementation: Optional instance to use
        factory: Optional factory function
        lifecycle: "singleton" (default) or "transient"
    """
    get_default_container().register(interface, implementation, factory, lifecycle)


def resolve_default(interface: type[T]) -> T:
    """Resolve a service from the default container.

    This is a convenience function for global resolution.

    Args:
        interface: The type/class to resolve

    Returns:
        An instance of the requested type
    """
    return get_default_container().resolve(interface)


# Service marker interface for better type safety
class Service(ABC):
    """Base class for services that can be dependency injected."""

    pass