"""Smoke tests for SubAtomicRegistryAgent ADG exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestSubatomicregistryagentAdg:
    """Smoke tests for SubAtomicRegistryAgent ADG exports."""

    def test_SubAtomicRegistryAgent_adg_imports(self) -> None:
        """Import module export."""
        symbol = import_attr_or_skip("agentic_core", "SubAtomicRegistryAgent_adg")
        assert symbol is not None

    def test_SubAtomicRegistryAgent_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "SubatomicregistryagentAdg")
        assert klass is not None

    def test_SubAtomicRegistryAgent_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_SubAtomicRegistryAgent_adg")
        assert callable(validator)
