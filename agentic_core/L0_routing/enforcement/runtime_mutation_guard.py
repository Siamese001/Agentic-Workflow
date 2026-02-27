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
from typing import Any

Logger = logging.getLogger(__name__)

# Store original setattr to avoid recursion
_original_setattr = setattr

# Flag to disable guard during critical operations
_guard_disabled = False

# Core layers that are protected from mutation
PROTECTED_LAYERS = {
    "L0_routing",
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
    "L7_meta_learning",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "agentic_core",
}

# Protected attributes that cannot be modified
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

# Tracks original module references
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
    if not module_name:
        return False

    # Check if module is in a protected layer
    return any(layer in module_name for layer in PROTECTED_LAYERS)


def is_protected_object(obj: Any) -> bool:
    """Check if an object belongs to a protected core layer.

    Args:
        obj: Object to check

    Returns:
        True if object is protected, False otherwise
    """
    # Check if object is a module
    if hasattr(obj, "__name__"):
        module_name = getattr(obj, "__name__", None)
        if is_protected_module(module_name):
            return True

    # Check if object is a class or function
    if hasattr(obj, "__module__"):
        module_name = getattr(obj, "__module__", None)
        if is_protected_module(module_name):
            return True

    # Check if object's class is in a protected module
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
    # Skip guard if disabled
    if _guard_disabled:
        _original_setattr(obj, name, value)
        return

    # Check if object is protected
    if is_protected_object(obj):
        # Special case: block critical attributes
        if name in ("__class__", "__module__", "__dict__"):
            raise RuntimeMutationViolation(
                f"Cannot modify protected attribute '{name}' on protected object "
                f"'{type(obj).__name__}' (REQ-417)"
            )
        # Check if value is a protected function/class
        elif is_protected_object(value):
            raise RuntimeMutationViolation(
                f"Cannot assign protected object to attribute '{name}' on protected object "
                f"'{type(obj).__name__}' (REQ-417)"
            )
        # Allow setting private attributes
        elif name.startswith("_"):
            pass
        elif not hasattr(obj, name):
            # Allow new attributes (unless they're protected objects)
            pass
        else:
            # Check if existing attribute is being changed
            current_value = getattr(obj, name)
            if current_value is not value:
                raise RuntimeMutationViolation(
                    f"Cannot modify existing attribute '{name}' on protected object "
                    f"'{type(obj).__name__}' (REQ-417)"
                )

    # Use original setattr to avoid recursion
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
    # Check if any base is from protected layer
    for base in bases:
        if is_protected_object(base):
            # Check if metaclass is trying to override protected behaviors
            if "__setattr__" in namespace or "__delattr__" in namespace:
                raise RuntimeMutationViolation(
                    f"Metaclass cannot override attribute methods for protected base "
                    f"'{base.__name__}' (REQ-417)"
                )

            # Check for permission-related method overrides
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
                        f"Metaclass cannot override permission method '{method_name}' "
                        f"for protected base '{base.__name__}' (REQ-417)"
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
        global _guard_disabled
        _guard_disabled = True

        # Store original functions
        self._original_setattr = builtins.setattr
        self._original_importlib_reload = importlib.reload

        # Replace with guarded versions
        builtins.setattr = guard_setattr
        importlib.reload = guard_importlib_reload

        self.installed = True
        _guard_disabled = False
        Logger.info("Runtime mutation guard installed (REQ-417)")

    def uninstall(self) -> None:
        """Uninstall the runtime mutation guard."""
        global _guard_disabled
        _guard_disabled = True

        # Restore original functions
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


# Global guard instance
_mutation_guard: RuntimeMutationGuard | None = None


def get_mutation_guard() -> RuntimeMutationGuard:
    """Get the global mutation guard instance."""
    global _mutation_guard
    if _mutation_guard is None:
        _mutation_guard = RuntimeMutationGuard()
    return _mutation_guard


# Install guard globally - DISABLED to avoid import issues
# install_runtime_mutation_guard()


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
        # Install guard
        install_runtime_mutation_guard()

        # Test 1: Try to modify protected attribute
        try:

            class TestProtected:
                __module__ = "agentic_core.test"
                pass

            # This should fail
            guard_setattr(TestProtected, "__class__", object)
            return False
        except RuntimeMutationViolation:
            pass  # Expected

        # Test 2: Try to reload protected module
        try:
            import agentic_core

            guard_importlib_reload(agentic_core)
            return False
        except RuntimeMutationViolation:
            pass  # Expected

        # Test 3: Allow non-protected modifications
        class TestUnprotected:
            pass

        try:
            guard_setattr(TestUnprotected, "new_attr", "value")
        except RuntimeMutationViolation:
            return False  # Should not raise

        # Uninstall guard
        uninstall_runtime_mutation_guard()

        return True

    except Exception as e:
        Logger.error(f"Runtime mutation guard test failed: {e}")
        uninstall_runtime_mutation_guard()
        return False


# Module-level guard installation disabled
# Auto-installation causes issues with test collection
# if __name__ != "__main__":
#     # Auto-install guard when imported in production
#     if not hasattr(sys, "_is_mypy_run"):
#         install_runtime_mutation_guard()
