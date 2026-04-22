"""Smoke tests for provider_type_config exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestProvidertypeconfig:
    """Smoke tests for provider_type_config exports."""

    def test_module_importable(self) -> None:
        """Import root export."""
        module = import_attr_or_skip("agentic_core", "provider_type_config")
        assert module is not None

    def test_module_has_exports(self) -> None:
        """Validate __all__ exports when declared."""
        module = import_attr_or_skip("agentic_core", "provider_type_config")
        exports = getattr(module, "__all__", ())
        assert all(hasattr(module, name) for name in exports)

    def test_module_docstring_present(self) -> None:
        """Ensure module docstring is present."""
        module = import_attr_or_skip("agentic_core", "provider_type_config")
        assert module.__doc__ is not None

    def test_module_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "provider_type_config")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
