"""Smoke tests for blast_radius_controls_types_adg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestBlastradiuscontrolstypes:
    """Smoke tests for blast_radius_controls_types_adg exports."""

    def test_blast_radius_controls_types_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "blast_radius_controls_types")
        assert module is not None

    def test_blast_radius_controls_types_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "blast_radius_controls_types")
        assert klass is not None

    def test_blast_radius_controls_types_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "blast_radius_controls_types")
        assert callable(validator)
