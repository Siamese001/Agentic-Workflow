"""Smoke tests for ProtocolAdg exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestProtocolAdg:
    """Smoke tests for ProtocolAdg exports."""

    def test_protocol_adg_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "protocol_adg")
        assert module is not None

    def test_protocol_adg_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "ProtocolAdg")
        assert klass is not None

    def test_protocol_adg_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_protocol_adg")
        assert callable(validator)
