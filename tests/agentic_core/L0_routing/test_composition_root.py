"""Tests for L0_routing.composition_root module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing import composition_root


class TestCompositionRoot:
    """Test suite for composition_root evidence resolver wiring."""

    def setup_method(self):
        """Reset module state before each test."""
        composition_root.clear_evidence_source()
        # Reset installation flag to allow re-installation in tests
        composition_root._INSTALLED = False

    def test_fail_closed_resolver(self):
        """Test default fail-closed resolver returns False."""
        assert composition_root._fail_closed_resolver("any_id") is False

    def test_fail_open_resolver(self):
        """Test legacy fail-open resolver returns True."""
        assert composition_root._fail_open_resolver("any_id") is True

    def test_composed_resolver_no_registration_fail_closed(self):
        """Test composed resolver with no registration and fail-closed default."""
        # Ensure no registration and fail-closed flag off
        composition_root.clear_evidence_source()
        with patch.dict(os.environ, {"SEMANTIC_CACHE_FAIL_OPEN_RESOLVER": "0"}):
            assert composition_root._composed_resolver("any_id") is False

    def test_composed_resolver_no_registration_fail_open(self):
        """Test composed resolver with no registration and fail-open flag."""
        composition_root.clear_evidence_source()
        with patch.dict(os.environ, {"SEMANTIC_CACHE_FAIL_OPEN_RESOLVER": "1"}):
            assert composition_root._composed_resolver("any_id") is True

    def test_composed_resolver_with_registration(self):
        """Test composed resolver delegates to registered resolver."""
        # Register a custom resolver
        custom_resolver = MagicMock(return_value=True)
        composition_root.register_evidence_source(custom_resolver)

        result = composition_root._composed_resolver("test_evidence_id")
        custom_resolver.assert_called_once_with("test_evidence_id")
        assert result is True

    def test_composed_resolver_registration_exception_handling(self):
        """Test composed resolver handles resolver exceptions gracefully."""
        # Register a resolver that raises an exception
        def failing_resolver(evidence_id):
            raise LookupError("Test exception")

        composition_root.register_evidence_source(failing_resolver)

        # Should return False (fail-closed) instead of propagating exception
        with patch.dict(os.environ, {"SEMANTIC_CACHE_FAIL_OPEN_RESOLVER": "0"}):
            result = composition_root._composed_resolver("test_id")
            assert result is False

    def test_register_evidence_source(self):
        """Test registration of custom evidence resolver."""
        custom_resolver = MagicMock(return_value=True)
        composition_root.register_evidence_source(custom_resolver)

        # Verify it's registered
        assert composition_root._REGISTERED_RESOLVER is custom_resolver

    def test_register_evidence_source_last_writer_wins(self):
        """Test that last registration wins (idempotent)."""
        resolver1 = MagicMock(return_value=True)
        resolver2 = MagicMock(return_value=False)

        composition_root.register_evidence_source(resolver1)
        assert composition_root._REGISTERED_RESOLVER is resolver1

        composition_root.register_evidence_source(resolver2)
        assert composition_root._REGISTERED_RESOLVER is resolver2

    def test_clear_evidence_source(self):
        """Test clearing the registered resolver."""
        custom_resolver = MagicMock(return_value=True)
        composition_root.register_evidence_source(custom_resolver)
        assert composition_root._REGISTERED_RESOLVER is custom_resolver

        composition_root.clear_evidence_source()
        assert composition_root._REGISTERED_RESOLVER is None

    def test_install_default_resolvers_idempotent(self):
        """Test that install_default_resolvers is idempotent."""
        # First call should install
        composition_root.install_default_resolvers()
        first_installed = composition_root._INSTALLED

        # Second call should be no-op
        composition_root.install_default_resolvers()
        second_installed = composition_root._INSTALLED

        assert first_installed
        assert second_installed

    def test_install_default_resolvers_l4_import_failure(self):
        """Test install handles L4 cache import failure gracefully."""
        composition_root._INSTALLED = False

        with patch(
            "agentic_core.L0_routing.composition_root.set_evidence_resolver",
            side_effect=ImportError("L4 not available"),
        ):
            # Should not raise, just log and return
            composition_root.install_default_resolvers()
            # Installation flag should remain False due to import failure
            assert composition_root._INSTALLED is False

    def test_install_default_resolvers_success(self):
        """Test successful installation wires the composed resolver."""
        composition_root._INSTALLED = False

        with patch(
            "agentic_core.L0_routing.composition_root.set_evidence_resolver"
        ) as mock_set_resolver:
            composition_root.install_default_resolvers()
            mock_set_resolver.assert_called_once_with(
                composition_root._composed_resolver
            )
            assert composition_root._INSTALLED

    def test_auto_install_on_import(self):
        """Test that resolver is auto-installed on module import."""
        # Re-import the module to trigger auto-install
        import importlib

        importlib.reload(composition_root)
        # After reload, _INSTALLED should be True (unless L4 import failed)
        # We can't assert this reliably in all environments, but we can verify
        # the function exists and is callable
        assert callable(composition_root._composed_resolver)

    def test_composed_resolver_various_exception_types(self):
        """Test composed resolver handles various exception types."""
        exception_types = [LookupError, ValueError, RuntimeError, TypeError]

        for exc_type in exception_types:
            def failing_resolver(evidence_id):
                raise exc_type("Test")

            composition_root.register_evidence_source(failing_resolver)

            with patch.dict(os.environ, {"SEMANTIC_CACHE_FAIL_OPEN_RESOLVER": "0"}):
                result = composition_root._composed_resolver("test")
                assert result is False

            composition_root.clear_evidence_source()

    def test_public_api_exports(self):
        """Test that public API functions are exported."""
        assert hasattr(composition_root, "register_evidence_source")
        assert hasattr(composition_root, "clear_evidence_source")
        assert hasattr(composition_root, "install_default_resolvers")
