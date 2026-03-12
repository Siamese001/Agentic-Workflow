"""ADG-driven tests for L2_execution/cid_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle


class TestExecutionCycle:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExecutionCycle)

    def test_is_frozen(self):
        cycle = ExecutionCycle(cid="c-1", attempt=1, status="new")
        with pytest.raises((AttributeError, TypeError)):
            cycle.status = "done"

    def test_creates(self):
        cycle = ExecutionCycle(cid="c-1", attempt=1, status="new")
        assert cycle.cid == "c-1"
        assert cycle.attempt == 1


class TestCIDRegistry:
    def test_creates(self):
        reg = CIDRegistry()
        assert reg is not None
        assert reg._cycles == {}

    def test_new_cycle_returns_execution_cycle(self):
        reg = CIDRegistry()
        cycle = reg.new_cycle("cid-001")
        assert isinstance(cycle, ExecutionCycle)
        assert cycle.cid == "cid-001"
        assert cycle.attempt == 1
        assert cycle.status == "new"
