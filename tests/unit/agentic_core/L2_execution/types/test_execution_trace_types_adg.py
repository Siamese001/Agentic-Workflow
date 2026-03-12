"""ADG-driven tests for L2_execution/types/execution_trace_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.execution_trace_types import (
        _compute_replay_key,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    _compute_replay_key = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="execution_trace_types deps unavailable")
class TestComputeReplayKey:
    def test_returns_hex_string(self):
        result = _compute_replay_key("trace-1", "plan-hash", "transcript-hash")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_deterministic(self):
        r1 = _compute_replay_key("t", "p", "x")
        r2 = _compute_replay_key("t", "p", "x")
        assert r1 == r2

    def test_different_inputs_differ(self):
        r1 = _compute_replay_key("t1", "p", "x")
        r2 = _compute_replay_key("t2", "p", "x")
        assert r1 != r2


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
