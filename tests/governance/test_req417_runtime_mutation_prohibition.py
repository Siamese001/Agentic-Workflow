"""
Test REQ-417: Dynamic Runtime Mutation Prohibition

Tests that dynamic runtime mutation of classes, modules, or permissions via:
- monkeypatch
- setattr on core layer objects
- importlib.reload of core modules
- metaclass injection altering layer permissions
- equivalent reflection mechanisms

Runtime guard required at module load and class definition time for all core layers.
"""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.governance

# Import guard components without installing the guard
from agentic_core.L0_routing.enforcement.runtime_mutation_guard import (
    RuntimeMutationGuard,
    RuntimeMutationViolation,
    get_mutation_guard,
    guard_function_replacement,
    guard_importlib_reload,
    guard_metaclass_creation,
    guard_setattr,
    install_runtime_mutation_guard,
    is_protected_module,
    is_protected_object,
    uninstall_runtime_mutation_guard,
)


class TestREQ417RuntimeMutationProhibition:
    """Test suite for REQ-417 Dynamic Runtime Mutation Prohibition."""

    def test_is_protected_module_core_layers(self):
        """Test that core layers are identified as protected."""
        protected_modules = [
            "agentic_core.L0_routing",
            "agentic_core.L1_cognition",
            "agentic_core.L2_execution",
            "agentic_core.L3_orchestration",
            "agentic_core.L4_state",
            "agentic_core.L5_safety",
            "agentic_core.L6_observability",
            "agentic_core.L7_meta_learning",
            "apps_lic.test",
            "apps_rg.test",
            "apps_shared.test",
        ]

        for module_name in protected_modules:
            assert is_protected_module(module_name), f"{module_name} should be protected"

    def test_is_protected_module_non_core(self):
        """Test that non-core modules are not protected."""
        non_protected_modules = ["os", "sys", "json", "requests", "numpy", "pandas", "my_custom_module"]

        for module_name in non_protected_modules:
            assert not is_protected_module(module_name), f"{module_name} should not be protected"

    def test_is_protected_object_core_class(self):
        """Test that core layer classes are identified as protected."""

        # Create a mock class from protected module
        class MockCoreClass:
            __module__ = "agentic_core.L2_execution.test"

        assert is_protected_object(MockCoreClass)

    def test_is_protected_object_non_core(self):
        """Test that non-core objects are not protected."""

        class MockNonCoreClass:
            __module__ = "os"

        assert not is_protected_object(MockNonCoreClass)

    def test_guard_setattr_protected_attribute_blocked(self):
        """Test that modifying protected attributes is blocked."""

        class ProtectedClass:
            __module__ = "agentic_core.L0_routing.test"
            __class__ = type

        obj = ProtectedClass()

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_setattr(obj, "__class__", object)

        assert "Cannot modify protected attribute" in str(exc_info.value)
        assert "REQ-417" in str(exc_info.value)

    def test_guard_setattr_protected_existing_attribute_blocked(self):
        """Test that modifying existing protected attributes is blocked."""

        class ProtectedClass:
            __module__ = "agentic_core.L1_cognition.test"
            existing_attr = "original"

        obj = ProtectedClass()

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_setattr(obj, "existing_attr", "modified")

        assert "Cannot modify existing attribute" in str(exc_info.value)

    def test_guard_setattr_new_attribute_allowed(self):
        """Test that adding new non-protected attributes is allowed."""

        class ProtectedClass:
            __module__ = "agentic_core.L2_execution.test"

        obj = ProtectedClass()

        # Should not raise
        guard_setattr(obj, "new_attr", "value")
        assert obj.new_attr == "value"

    def test_guard_setattr_non_protected_object_allowed(self):
        """Test that modifying non-protected objects is allowed."""

        class NonProtectedClass:
            __module__ = "os"

        obj = NonProtectedClass()

        # Should not raise
        guard_setattr(obj, "any_attr", "value")
        assert obj.any_attr == "value"

    def test_guard_importlib_reload_protected_module_blocked(self):
        """Test that reloading protected modules is blocked."""
        # Create a mock module
        mock_module = MagicMock()
        mock_module.__name__ = "agentic_core.L3_orchestration.test"

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_importlib_reload(mock_module)

        assert "Cannot reload protected module" in str(exc_info.value)
        assert "REQ-417" in str(exc_info.value)

    def test_guard_importlib_reload_non_protected_allowed(self):
        """Test that reloading non-protected modules is allowed."""
        # Create a mock module
        mock_module = MagicMock()
        mock_module.__name__ = "os"

        # Mock importlib.reload to avoid actual reload
        with patch("importlib.reload") as mock_reload:
            mock_reload.return_value = mock_module

            # Should not raise
            result = guard_importlib_reload(mock_module)
            assert result == mock_module

    def test_guard_metaclass_creation_permission_override_blocked(self):
        """Test that metaclass cannot override permission methods."""

        class ProtectedBase:
            __module__ = "agentic_core.L5_safety.test"

        # Try to create metaclass that overrides permission methods
        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_metaclass_creation("TestMeta", (ProtectedBase,), {"check_permission": lambda self: True})

        assert "cannot override permission method" in str(exc_info.value)
        assert "REQ-417" in str(exc_info.value)

    def test_guard_metaclass_creation_attribute_override_blocked(self):
        """Test that metaclass cannot override attribute methods."""

        class ProtectedBase:
            __module__ = "agentic_core.L6_observability.test"

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_metaclass_creation(
                "TestMeta", (ProtectedBase,), {"__setattr__": lambda self, name, value: None}
            )

        assert "cannot override attribute methods" in str(exc_info.value)

    def test_guard_metaclass_creation_non_protected_allowed(self):
        """Test that metaclass creation is allowed for non-protected bases."""

        class NonProtectedBase:
            __module__ = "os"

        # Should not raise
        meta = guard_metaclass_creation(
            "TestMeta", (NonProtectedBase,), {"__setattr__": lambda self, name, value: None}
        )

        assert meta is not None

    def test_guard_function_replacement_protected_blocked(self):
        """Test that replacing protected functions is blocked."""

        def protected_func():
            pass

        protected_func.__module__ = "agentic_core.L0_routing.test"

        def new_func():
            pass

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_function_replacement(protected_func, new_func)

        assert "Cannot replace protected function" in str(exc_info.value)
        assert "REQ-417" in str(exc_info.value)

    def test_guard_function_replacement_non_protected_allowed(self):
        """Test that replacing non-protected functions is allowed."""

        def non_protected_func():
            pass

        non_protected_func.__module__ = "os"

        def new_func():
            pass

        # Should not raise
        guard_function_replacement(non_protected_func, new_func)

    def test_runtime_mutation_guard_install_uninstall(self):
        """Test installation and uninstallation of runtime mutation guard."""
        guard = RuntimeMutationGuard()

        # Initially not installed
        assert not guard.is_installed()

        # Install
        guard.install()
        assert guard.is_installed()

        # Uninstall
        guard.uninstall()
        assert not guard.is_installed()

    def test_get_mutation_guard_singleton(self):
        """Test that get_mutation_guard returns singleton instance."""
        guard1 = get_mutation_guard()
        guard2 = get_mutation_guard()

        assert guard1 is guard2
        assert isinstance(guard1, RuntimeMutationGuard)

    def test_install_runtime_mutation_guard_global(self):
        """Test global installation of runtime mutation guard."""
        # Save original state
        guard = get_mutation_guard()
        was_installed = guard.is_installed()

        try:
            # Install
            install_runtime_mutation_guard()
            assert guard.is_installed()

            # Uninstall
            uninstall_runtime_mutation_guard()
            assert not guard.is_installed()

        finally:
            # Restore original state
            if was_installed:
                install_runtime_mutation_guard()
            else:
                uninstall_runtime_mutation_guard()

    def test_test_runtime_mutation_guard(self):
        """Test the runtime mutation guard test function."""
        # Create our own test function to avoid import issues
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
                raise AssertionError("Should have raised RuntimeMutationViolation")
            except RuntimeMutationViolation:
                pass  # Expected

            # Test 2: Try to reload protected module
            try:
                import agentic_core

                guard_importlib_reload(agentic_core)
                raise AssertionError("Should have raised RuntimeMutationViolation")
            except RuntimeMutationViolation:
                pass  # Expected

            # Test passed
            result = True

        finally:
            # Clean up
            uninstall_runtime_mutation_guard()

        assert result is True

    def test_protected_attributes_list(self):
        """Test that protected attributes are properly defined."""
        from agentic_core.L0_routing.enforcement.runtime_mutation_guard import PROTECTED_ATTRIBUTES

        expected_attributes = {
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

        assert PROTECTED_ATTRIBUTES == expected_attributes

    def test_protected_layers_list(self):
        """Test that protected layers are properly defined."""
        from agentic_core.L0_routing.enforcement.runtime_mutation_guard import PROTECTED_LAYERS

        expected_layers = {
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

        assert PROTECTED_LAYERS == expected_layers

    def test_guard_setattr_protected_function_assignment_blocked(self):
        """Test that assigning protected function to protected object is blocked."""

        class ProtectedClass:
            __module__ = "agentic_core.L2_execution.test"

        def protected_func():
            pass

        protected_func.__module__ = "agentic_core.L0_routing.test"

        obj = ProtectedClass()

        with pytest.raises(RuntimeMutationViolation) as exc_info:
            guard_setattr(obj, "new_attr", protected_func)

        assert "protected" in str(exc_info.value).lower()

    def test_runtime_mutation_guard_persistence(self):
        """Test that guard persists across multiple operations."""
        guard = RuntimeMutationGuard()

        try:
            guard.install()

            # Multiple operations should work
            assert guard.is_installed()
            assert guard.is_installed()
            assert guard.is_installed()

        finally:
            guard.uninstall()

    def test_edge_case_empty_module_name(self):
        """Test edge case with empty module name."""

        class TestClass:
            __module__ = ""

        # Empty module name should not be protected
        assert not is_protected_object(TestClass)

    def test_edge_case_none_module_name(self):
        """Test edge case with None module name."""

        class TestClass:
            pass

        # None module name should not be protected
        TestClass.__module__ = None
        assert not is_protected_object(TestClass)
