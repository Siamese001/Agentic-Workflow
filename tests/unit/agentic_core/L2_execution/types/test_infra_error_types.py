"""Smoke tests for infra_error_types exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestTypeSmoke:
    """Smoke tests for infra_error_types exports."""

    def test_infra_error_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "infra_error_types")
        assert module is not None

    def test_infra_error_types_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "infra_error_types")
        assert module.__doc__ is not None

    def test_infra_error_types_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "infra_error_types")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
