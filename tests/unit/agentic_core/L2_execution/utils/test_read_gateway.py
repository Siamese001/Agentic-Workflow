"""Smoke tests for read_gateway exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestReadGateway:
    """Smoke tests for read_gateway exports."""

    def test_read_gateway_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "read_gateway")
        assert module is not None

    def test_read_gateway_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "ReadGateway")
        assert klass is not None

    def test_read_gateway_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_read_gateway")
        assert callable(validator)
