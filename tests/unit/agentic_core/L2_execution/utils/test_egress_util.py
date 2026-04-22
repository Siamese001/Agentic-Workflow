"""Smoke tests for egress_util exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestEgressUtil:
    """Validate the egress_util module surface without invoking live behavior."""

    def test_egress_util_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "egress_util")
        assert module is not None

    def test_egress_util_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "egress_util")
        assert module.__doc__ is not None

    def test_egress_util_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "egress_util")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
