"""Smoke tests for execution gateway exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestExecutionGatewayAdg:
    """Smoke tests for execution gateway exports."""

    def test_create_envelope(self) -> None:
        """Import create_envelope export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "create_envelope")
        assert callable(func)

    def test_SignatureBoundaryError_init(self) -> None:
        """Import SignatureBoundaryError class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "SignatureBoundaryError")
        assert klass is not None

    def test_ExecutionGateway_init(self) -> None:
        """Import ExecutionGateway class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ExecutionGateway")
        assert klass is not None

    def test_ExecutionGateway_create_envelope(self) -> None:
        """Validate ExecutionGateway.create_envelope method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ExecutionGateway")
        assert hasattr(klass, "create_envelope")
