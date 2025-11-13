"""Light-weight dependency injection utilities for LIC stacks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, MutableMapping


class DependencyNotRegisteredError(LookupError):
    """Raised when a dependency lookup fails."""


class DependencyAlreadyRegisteredError(RuntimeError):
    """Raised when attempting to register the same dependency twice."""


@dataclass
class _Provider:
    factory: Callable[["LICCoreContext"], Any]
    singleton: bool = True


class LICCoreContext:
    """Simple dependency container mirroring resume-gen's WorkflowContext."""

    def __init__(self) -> None:
        self._providers: Dict[str, _Provider] = {}
        self._instances: MutableMapping[str, Any] = {}

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------
    def register_factory(self, key: str, factory: Callable[["LICCoreContext"], Any], *, singleton: bool = True) -> None:
        if key in self._providers:
            raise DependencyAlreadyRegisteredError(f"Dependency '{key}' already registered")
        self._providers[key] = _Provider(factory=factory, singleton=singleton)

    def register_instance(self, key: str, instance: Any) -> None:
        if key in self._providers or key in self._instances:
            raise DependencyAlreadyRegisteredError(f"Dependency '{key}' already registered")
        self._instances[key] = instance

    # ------------------------------------------------------------------
    # Resolution helpers
    # ------------------------------------------------------------------
    def resolve(self, key: str) -> Any:
        if key in self._instances:
            return self._instances[key]
        provider = self._providers.get(key)
        if not provider:
            raise DependencyNotRegisteredError(f"Dependency '{key}' is not registered")
        value = provider.factory(self)
        if provider.singleton:
            self._instances[key] = value
        return value

    def reset(self) -> None:
        self._instances.clear()

    # ------------------------------------------------------------------
    # Bootstrapping helpers
    # ------------------------------------------------------------------
    @classmethod
    def bootstrap(cls) -> "LICCoreContext":
        """Return a context with the default LIC core dependencies registered."""

        from .conductor import Conductor
        from .metrics import MetricsTracker
        from .policy_controller import PolicyController

        ctx = cls()
        ctx.register_instance("policy_controller", PolicyController())
        ctx.register_instance("metrics_tracker", MetricsTracker())
        ctx.register_factory("conductor", lambda _ctx: Conductor(), singleton=True)
        return ctx
