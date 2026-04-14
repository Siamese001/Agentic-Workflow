"""Smoke tests for rollback refiner exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestRollbackRefinerAdg:
    """Smoke tests for rollback refiner exports."""

    def test_refine_export(self) -> None:
        """Import refine export."""
        func = import_attr_or_skip("agentic_core.L2_execution.reasoning", "refine")
        assert callable(func)

    def test_RollbackRefiner_init(self) -> None:
        """Import RollbackRefiner class."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "RollbackRefiner")
        assert klass is not None

    def test_RollbackRefiner_refine(self) -> None:
        """Validate RollbackRefiner.refine method is present."""
        klass = import_attr_or_skip("agentic_core.L2_execution.reasoning", "RollbackRefiner")
        assert hasattr(klass, "refine")

    def test_DefaultDeterministicRollbackRefiner_init(self) -> None:
        """Import DefaultDeterministicRollbackRefiner class."""
        klass = import_attr_or_skip(
            "agentic_core.L2_execution.reasoning", "DefaultDeterministicRollbackRefiner"
        )
        assert klass is not None

    def test_DefaultDeterministicRollbackRefiner_refine(self) -> None:
        """Validate DefaultDeterministicRollbackRefiner.refine method is present."""
        klass = import_attr_or_skip(
            "agentic_core.L2_execution.reasoning", "DefaultDeterministicRollbackRefiner"
        )
        assert hasattr(klass, "refine")
