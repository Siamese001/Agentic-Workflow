"""Smoke tests for validation orchestrator exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestValidationOrchestratorAdg:
    """Smoke tests for validation orchestrator exports."""

    def test_can_run(self) -> None:
        """Import can_run export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "can_run")
        assert callable(func)

    def test_get_file_hash(self) -> None:
        """Import get_file_hash export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "get_file_hash")
        assert callable(func)

    def test_ValidationOrchestrator_init(self) -> None:
        """Import ValidationOrchestrator class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ValidationOrchestrator")
        assert klass is not None

    def test_ValidationOrchestrator_can_run(self) -> None:
        """Validate ValidationOrchestrator.can_run method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "ValidationOrchestrator")
        assert hasattr(klass, "can_run")
