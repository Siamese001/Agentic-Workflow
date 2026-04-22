"""Smoke tests for __init___adg exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestInitAdg:
    """Smoke tests for __init___adg exports."""

    def test___init___adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "__init___adg")
        assert module is not None

    def test___init___adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "InitAdg")
        assert klass is not None

    def test___init___adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate___init___adg")
        assert callable(validator)
