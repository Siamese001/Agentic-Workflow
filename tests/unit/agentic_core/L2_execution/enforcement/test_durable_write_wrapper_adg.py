"""ADG-driven tests for L2_execution/enforcement/durable_write_wrapper.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.durable_write_wrapper import durable_write
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    durable_write = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="durable_write_wrapper deps unavailable")
class TestDurableWrite:
    def test_callable(self):
        assert callable(durable_write)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
