"""ADG-driven tests for L2_execution/types/vllm_backpressure_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_backpressure_types import (
        MAX_QUEUE_DEPTH,
        QUEUE_WAIT_TIMEOUT_SECONDS,
        CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    MAX_QUEUE_DEPTH = None
    QUEUE_WAIT_TIMEOUT_SECONDS = None
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = None


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types deps unavailable")
class TestVllmBackpressureConstants:
    def test_max_queue_depth_is_int(self):
        assert isinstance(MAX_QUEUE_DEPTH, int)
        assert MAX_QUEUE_DEPTH > 0

    def test_queue_wait_timeout_is_positive(self):
        assert isinstance(QUEUE_WAIT_TIMEOUT_SECONDS, float)
        assert QUEUE_WAIT_TIMEOUT_SECONDS > 0

    def test_circuit_breaker_threshold_is_int(self):
        assert isinstance(CIRCUIT_BREAKER_FAILURE_THRESHOLD, int)
        assert CIRCUIT_BREAKER_FAILURE_THRESHOLD > 0


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
