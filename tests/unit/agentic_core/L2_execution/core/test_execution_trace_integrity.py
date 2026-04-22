"""Smoke tests for ExecutionTraceIntegrity exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestExecutionTraceIntegrity:
    """Smoke tests for ExecutionTraceIntegrity exports."""

    def test_execution_trace_integrity_imports(self) -> None:
        """Import module export."""
        module = import_attr_or_skip("agentic_core", "execution_trace_integrity")
        assert module is not None

    def test_execution_trace_integrity_class(self) -> None:
        """Import class export."""
        klass = import_attr_or_skip("agentic_core", "ExecutionTraceIntegrity")
        assert klass is not None

    def test_execution_trace_integrity_callable(self) -> None:
        """Import validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_execution_trace_integrity")
        assert callable(validator)
