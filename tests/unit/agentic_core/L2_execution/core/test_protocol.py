"""Smoke tests for Protocol exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestProtocol:
    """Smoke tests for Protocol exports."""

    def test_protocol_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "protocol")
        assert module is not None

    def test_protocol_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "Protocol")
        assert klass is not None

    def test_protocol_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_protocol")
        assert callable(validator)
