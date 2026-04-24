"""
Dynamic Runtime Mutation Prohibition (REQ-417)

Forbids dynamic runtime mutation of classes, modules, or permissions via:
- monkeypatch
- setattr on core layer objects
- importlib.reload of core modules
- metaclass injection altering layer permissions
- equivalent reflection mechanisms

Runtime guard required at module load and class definition time for all core layers.
"""

from __future__ import annotations

import builtins
import importlib
import logging
import types
import uuid
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_hard_fails_untranscripted,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)
from tqdm import tqdm

Logger = logging.getLogger(__name__)
_original_setattr = setattr
_guard_disabled = False
PROTECTED_LAYERS = {
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
    "L7_meta_learning",
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    AGENTIC_CORE_DIR,
}
PROTECTED_ATTRIBUTES = {
    "__class__",
    "__bases__",
    "__subclasses__",
    "__mro__",
    "__dict__",
    "__module__",
    "__qualname__",
    "__annotations__",
    "__doc__",
    "__name__",
}
_original_modules: dict[str, types.ModuleType] = {}
_original_classes: dict[str, type] = {}
_original_functions: dict[str, Any] = {}


class RuntimeMutationViolation(Exception):
    """Raised when dynamic runtime mutation is attempted."""

    pass


def is_protected_module(module_name: str | None) -> bool:
    """Check if a module is protected from mutation (REQ-417).

    Args:
        module_name: Name of the module to check

    Returns:
        True if module is protected, False otherwise
    """
    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.is_protected_module")
    if not module_name:
        return False
    return any(layer in module_name for layer in PROTECTED_LAYERS)


def is_protected_object(obj: Any) -> bool:
    """Check if an object belongs to a protected core layer.

    Args:
        obj: Object to check

    Returns:
        True if object is protected, False otherwise
    """
    if hasattr(obj, "__name__"):
        module_name = getattr(obj, "__name__", None)
        if is_protected_module(module_name):
            return True
    if hasattr(obj, "__module__"):
        module_name = getattr(obj, "__module__", None)
        if is_protected_module(module_name):
            return True
    if hasattr(obj, "__class__"):
        module_name = getattr(obj.__class__, "__module__", None)
        if is_protected_module(module_name):
            return True
    return False


def guard_setattr(obj: Any, name: str, value: Any) -> None:
    """Guard setattr to prevent mutation of protected objects (REQ-417).

    Args:
        obj: Object to modify
        name: Attribute name
        value: New value

    Raises:
        RuntimeMutationViolation: If attempting to modify protected object
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.guard_setattr", "L0_ROUTING")
    if _guard_disabled:
        _original_setattr(obj, name, value)
        return
    if is_protected_object(obj):
        if name in ("__class__", "__module__", "__dict__"):
            raise RuntimeMutationViolation(
                f"Cannot modify protected attribute '{name}' on protected object '{type(obj).__name__}' (REQ-417)",
            )
        elif is_protected_object(value):
            raise RuntimeMutationViolation(
                f"Cannot assign protected object to attribute '{name}' on protected object '{type(obj).__name__}' (REQ-417)",
            )
        elif name.startswith("_"):
            pass
        elif not hasattr(obj, name):
            pass
        else:
            current_value = getattr(obj, name)
            if current_value is not value:
                raise RuntimeMutationViolation(
                    f"Cannot modify existing attribute '{name}' on protected object '{type(obj).__name__}' (REQ-417)",
                )
    _original_setattr(obj, name, value)


def guard_importlib_reload(module: types.ModuleType) -> types.ModuleType:
    """Guard importlib.reload to prevent reloading protected modules (REQ-417).

    Args:
        module: Module to reload

    Returns:
        The reloaded module

    Raises:
        RuntimeMutationViolation: If attempting to reload protected module
    """
    module_name = module.__name__
    if is_protected_module(module_name):
        raise RuntimeMutationViolation(f"Cannot reload protected module '{module_name}' (REQ-417)")
    return importlib.reload(module)


def guard_metaclass_creation(name: str, bases: tuple, namespace: dict) -> type:
    """Guard metaclass creation to prevent permission alteration (REQ-417).

    Args:
        name: Class name
        bases: Base classes
        namespace: Class namespace

    Returns:
        Created class

    Raises:
        RuntimeMutationViolation: If metaclass alters protected permissions
    """
    for base in tqdm(bases, desc="Processing", unit="item"):
        if is_protected_object(base):
            if "__setattr__" in namespace or "__delattr__" in namespace:
                raise RuntimeMutationViolation(
                    f"Metaclass cannot override attribute methods for protected base '{base.__name__}' (REQ-417)",
                )
            permission_methods = {
                "check_permission",
                "validate_access",
                "enforce_policy",
                "can_execute",
                "is_allowed",
            }
            for method_name in permission_methods:
                if method_name in namespace:
                    raise RuntimeMutationViolation(
                        f"Metaclass cannot override permission method '{method_name}' for protected base '{base.__name__}' (REQ-417)",
                    )
    return type(name, bases, namespace)


def guard_function_replacement(func: Any, new_func: Any) -> None:
    """Guard against replacing functions in protected modules.

    Args:
        func: Original function
        new_func: Replacement function

    Raises:
        RuntimeMutationViolation: If attempting to replace protected function
    """
    if is_protected_object(func):
        raise RuntimeMutationViolation(f"Cannot replace protected function '{func.__name__}' (REQ-417)")


class RuntimeMutationGuard:
    """Guards against dynamic runtime mutations in core layers."""

    def __init__(self):
        self.installed = False
        self._original_setattr = None
        self._original_importlib_reload = None

    def install(self) -> None:
        """Install the runtime mutation guard (REQ-417)."""
        # Check if disabled for testing
        import os

        if os.environ.get("DISABLE_RUNTIME_MUTATION_GUARD") == "1":
            return

        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RuntimeMutationGuard.install")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        global _guard_disabled
        _guard_disabled = True
        self._original_setattr = builtins.setattr
        self._original_importlib_reload = importlib.reload
        builtins.setattr = guard_setattr
        importlib.reload = guard_importlib_reload
        self.installed = True
        _guard_disabled = False
        Logger.info("Runtime mutation guard installed (REQ-417)")

    def uninstall(self) -> None:
        """Uninstall the runtime mutation guard."""
        global _guard_disabled
        _guard_disabled = True
        if hasattr(self, "_original_setattr"):
            builtins.setattr = self._original_setattr
        if hasattr(self, "_original_importlib_reload"):
            importlib.reload = self._original_importlib_reload
        self.installed = False
        _guard_disabled = False
        Logger.info("Runtime mutation guard uninstalled")

    def is_installed(self) -> bool:
        """Check if guard is installed.

        Returns:
            True if installed, False otherwise
        """
        return self.installed


_mutation_guard: RuntimeMutationGuard | None = None


def get_mutation_guard() -> RuntimeMutationGuard:
    """Get the global mutation guard instance."""
    global _mutation_guard
    if _mutation_guard is None:
        _mutation_guard = RuntimeMutationGuard()
    return _mutation_guard


def install_runtime_mutation_guard() -> None:
    """Install the runtime mutation guard (REQ-417)."""
    get_mutation_guard().install()


def uninstall_runtime_mutation_guard() -> None:
    """Uninstall the runtime mutation guard."""
    get_mutation_guard().uninstall()


def test_runtime_mutation_guard() -> bool:
    """Test that runtime mutation prohibition is working.

    Returns:
        True if guard is working, False otherwise
    """
    try:
        install_runtime_mutation_guard()
        try:

            class TestProtected:
                __module__ = "agentic_core.test"  # guardian: RuntimeMutationViolation should be handled with specific context
                pass

            guard_setattr(TestProtected, "__class__", object)
            return False
        # guardian: allow-silent-swallow -- acceptable exception handling
        except RuntimeMutationViolation as e:  # guardian: allow-log-and-swallow -- setattr guard: debug logged, guard check continues
            logging.getLogger(__name__).debug(
                "runtime_mutation_guard: RuntimeMutationViolation swallowed at L312: %s", e
            )
        try:
            import agentic_core

            guard_importlib_reload(agentic_core)
            # guardian: allow-silent-swallow -- acceptable exception handling
            return False
        except RuntimeMutationViolation as e:  # guardian: allow-log-and-swallow -- reload guard: debug logged, guard check continues
            logging.getLogger(__name__).debug(
                "runtime_mutation_guard: RuntimeMutationViolation swallowed at L320: %s", e
            )

        class TestUnprotected:
            pass

        # guardian: allow-silent-swallow -- acceptable exception handling
        try:
            guard_setattr(TestUnprotected, "new_attr", "value")
        except RuntimeMutationViolation:
            return False
        uninstall_runtime_mutation_guard()
        return True
    except (RuntimeError, OSError, TypeError) as e:  # test cleanup failure
        Logger.error(f"Runtime mutation guard test failed: {e}")
        uninstall_runtime_mutation_guard()
        return False
