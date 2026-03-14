"""StaticDispatchRegistry — replaces dynamic __import__ / importlib.import_module calls.

Addresses the ADG ``invokes_eval`` and ``invokes_dynamic`` gap: 986 edges across
non-test production code use ``__import__``, ``importlib.import_module``, or
``importlib.util.spec_from_file_location`` as the mechanism for loading plugin
modules. Each such call bypasses static analysis and the policy hash enforcer.

This registry provides a controlled, pre-registered dispatch surface:
- Callers register module paths at import time using ``register``.
- At call time, ``dispatch`` resolves the registered module and returns the
  callable or object — no ``__import__`` or ``importlib`` needed at runtime.
- Unregistered dispatch attempts raise ``UnregisteredDispatchError`` (fail-closed).

ADG governance plane: replacing ``invokes_dynamic`` edges with ``dispatch`` calls
converts ungoverned dynamic invocation into ``routes_through`` edges terminating
at this registry, which is itself ``validated_by_registry``.
"""

from __future__ import annotations

import importlib
import logging
from types import ModuleType
from typing import Any
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate, Callable

Logger = logging.getLogger(__name__)


class UnregisteredDispatchError(LookupError):
    """Raised when dispatch is requested for an unregistered symbol."""


class StaticDispatchRegistry:
    """Controlled dispatch surface replacing dynamic __import__ usage.

    Example::

        registry = StaticDispatchRegistry()
        registry.register("guardian.hygiene", "agentic_core.L0_routing.scripts.run_guardian_hygiene")
        registry.register("guardian.c0", "agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty")

        # Later — no __import__ needed:
        mod = registry.dispatch("guardian.hygiene")
        mod.main()

    The registry is fail-closed: dispatching an unregistered key raises
    ``UnregisteredDispatchError`` rather than falling through to dynamic import.
    """

    def __init__(self) -> None:
        self._registry: dict[str, str] = {}
        self._resolved: dict[str, ModuleType] = {}

    def register(self, key: str, module_path: str) -> None:
        """Register *module_path* under *key*.

        Args:
            key: Logical dispatch key (e.g. ``"guardian.hygiene"``).
            module_path: Fully-qualified Python module path (e.g.
                ``"agentic_core.L0_routing.scripts.run_guardian_hygiene"``).
        """
        if key in self._registry and self._registry[key] != module_path:
            Logger.warning(
                "[StaticDispatchRegistry] Overwriting key '%s': %s -> %s",
                key,
                self._registry[key],
                module_path,
            )
        self._registry[key] = module_path
        self._resolved.pop(key, None)
        Logger.debug("[StaticDispatchRegistry] registered '%s' -> '%s'", key, module_path)

    def register_many(self, mapping: dict[str, str]) -> None:
        """Register multiple ``{key: module_path}`` pairs at once."""
        for key, path in mapping.items():
            self.register(key, path)

    def dispatch(self, key: str) -> ModuleType:
        """Return the module registered under *key*.

        Lazily imports the module on first call; returns the cached module
        on subsequent calls.

        Raises:
            UnregisteredDispatchError: if *key* has not been registered.
            ImportError: if the registered module cannot be imported.
        """
        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="static_dispatch", target=key)
        if key not in self._registry:
            raise UnregisteredDispatchError(
                f"[StaticDispatchRegistry] No module registered for key '{key}'. "
                f"Registered keys: {sorted(self._registry)}"
            )
        if key not in self._resolved:
            module_path = self._registry[key]
            Logger.debug("[StaticDispatchRegistry] importing '%s' for key '%s'", module_path, key)
            self._resolved[key] = importlib.import_module(module_path)
        return self._resolved[key]

    def dispatch_attr(self, key: str, attr: str) -> Any:
        """Return *attr* from the module registered under *key*.

        Raises:
            UnregisteredDispatchError: if *key* not registered.
            AttributeError: if *attr* not found on the module.
        """
        mod = self.dispatch(key)
        if not hasattr(mod, attr):
            raise AttributeError(
                f"[StaticDispatchRegistry] Module '{self._registry[key]}' has no attribute '{attr}'."
            )
        return getattr(mod, attr)

    def dispatch_callable(self, key: str, attr: str) -> Callable[..., Any]:
        """Return a callable *attr* from the module registered under *key*.

        Raises:
            TypeError: if the resolved attribute is not callable.
        """
        obj = self.dispatch_attr(key, attr)
        if not callable(obj):
            raise TypeError(f"[StaticDispatchRegistry] '{attr}' on '{self._registry[key]}' is not callable.")
        return obj

    def is_registered(self, key: str) -> bool:
        """Return True if *key* has been registered."""
        return key in self._registry

    def registered_keys(self) -> list[str]:
        """Return sorted list of all registered keys."""
        return sorted(self._registry)

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, key: str) -> bool:
        return key in self._registry


_GUARDIAN_REGISTRY: StaticDispatchRegistry | None = None


def get_guardian_registry() -> StaticDispatchRegistry:
    """Return the singleton guardian registry, creating and pre-populating it on first call."""
    global _GUARDIAN_REGISTRY
    if _GUARDIAN_REGISTRY is None:
        _GUARDIAN_REGISTRY = StaticDispatchRegistry()
        _GUARDIAN_REGISTRY.register_many(
            {
                "guardian.hygiene": "agentic_core.L0_routing.scripts.run_guardian_hygiene",
                "guardian.c0_sovereignty": "agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty",
                "guardian.change_package": "agentic_core.L0_routing.scripts.run_guardian_change_package_activation",
                "guardian.cross_layer": "agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation",
                "guardian.escalation_determinism": "agentic_core.L0_routing.scripts.run_guardian_escalation_determinism",
                "guardian.gateway_bypass": "agentic_core.L0_routing.scripts.run_guardian_gateway_bypass",
                "guardian.all": "agentic_core.L0_routing.scripts.run_all_guardians",
                "seam.canonical_truth": "agentic_core.L0_routing.seams.canonical_truth_seam",
                "meta.apply_ops": "agentic_core.L0_routing.meta_control.meta_apply_ops",
            }
        )
    return _GUARDIAN_REGISTRY
