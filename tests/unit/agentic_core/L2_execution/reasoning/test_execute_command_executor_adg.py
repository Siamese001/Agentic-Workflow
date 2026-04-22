"""Smoke tests for execute-command executor exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestExecuteCommandExecutorAdg:
    """Smoke tests for execute-command executor exports."""

    def test_get_project_root(self) -> None:
        """Import get_project_root export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "get_project_root")
        assert callable(func)

    def test_validate_sandbox(self) -> None:
        """Import validate_sandbox export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "validate_sandbox")
        assert callable(func)

    def test_ExecuteCommandArgs_init(self) -> None:
        """Import ExecuteCommandArgs class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ExecuteCommandArgs")
        assert klass is not None

    def test_ExecutionTimeoutError_init(self) -> None:
        """Import ExecutionTimeoutError class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ExecutionTimeoutError")
        assert klass is not None
