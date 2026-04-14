"""Smoke tests for definitions_adg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestDefinitionsAdg:
    """Smoke tests for definitions_adg exports."""

    def test_definitions_adg_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "definitions_adg")
        assert module is not None

    def test_definitions_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "DefinitionsAdg")
        assert klass is not None

    def test_definitions_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_definitions_adg")
        assert callable(validator)
