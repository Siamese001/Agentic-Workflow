"""Smoke tests for factory_util_adg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestFactoryUtilAdg:
    """Smoke tests for factory_util_adg exports."""

    def test_factory_util_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "factory_util_adg")
        assert module is not None

    def test_factory_util_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "FactoryUtilAdg")
        assert klass is not None

    def test_factory_util_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_factory_util_adg")
        assert callable(validator)
