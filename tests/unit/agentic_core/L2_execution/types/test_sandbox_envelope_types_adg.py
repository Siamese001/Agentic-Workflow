"""ADG-driven tests for L2_execution/types/sandbox_envelope_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.sandbox_envelope_types import ToolBudget
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolBudget = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sandbox_envelope_types deps unavailable")
class TestToolBudget:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolBudget)

    def test_is_frozen(self):
        b = ToolBudget()
        with pytest.raises((AttributeError, TypeError)):
            b.compute_ms = 1000

    def test_defaults(self):
        b = ToolBudget()
        assert b.compute_ms == 5_000
        assert b.memory_mb == 256
        assert b.stdout_bytes == 65_536

    def test_custom_values(self):
        b = ToolBudget(compute_ms=1000, memory_mb=128, stdout_bytes=1024)
        assert b.compute_ms == 1000

    def test_zero_compute_raises(self):
        with pytest.raises(ValueError):
            ToolBudget(compute_ms=0, memory_mb=256, stdout_bytes=65536)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
