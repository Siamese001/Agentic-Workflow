"""Smoke tests for UniversalWriteGateway ADG exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestUniversalwritegatewayAdg:
    """Smoke tests for UniversalWriteGateway ADG exports."""

    def test_UniversalWriteGateway_adg_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "UniversalWriteGateway_adg")
        assert module is not None

    def test_UniversalWriteGateway_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "UniversalwritegatewayAdg")
        assert klass is not None

    def test_UniversalWriteGateway_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_UniversalWriteGateway_adg")
        assert callable(validator)
