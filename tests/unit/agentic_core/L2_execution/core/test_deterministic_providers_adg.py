"""Smoke tests for DeterministicProvidersAdg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestDeterministicProvidersAdg:
    """Smoke tests for DeterministicProvidersAdg exports."""

    def test_deterministic_providers_adg_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "deterministic_providers_adg")
        assert module is not None

    def test_deterministic_providers_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "DeterministicProvidersAdg")
        assert klass is not None

    def test_deterministic_providers_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_deterministic_providers_adg")
        assert callable(validator)
