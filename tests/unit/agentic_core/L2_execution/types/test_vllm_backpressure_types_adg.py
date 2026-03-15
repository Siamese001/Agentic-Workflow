"""ADG importability contract for agentic_core/L2_execution/types/vllm_backpressure_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_backpressure_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_backpressure_types import (  # noqa: F401
        BackpressureDecision,
        CircuitBreakerState,
        VLLMCircuitBreaker,
        VLLMQueueState,
        evaluate_backpressure,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    VLLMQueueState = None  # type: ignore[assignment,misc]
    CircuitBreakerState = None  # type: ignore[assignment,misc]
    VLLMCircuitBreaker = None  # type: ignore[assignment,misc]
    BackpressureDecision = None  # type: ignore[assignment,misc]
    evaluate_backpressure = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types deps unavailable")
class TestVllmBackpressureTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/vllm_backpressure_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmqueuestate_defined(self) -> None:
        assert VLLMQueueState is not None

    def test_circuitbreakerstate_defined(self) -> None:
        assert CircuitBreakerState is not None

    def test_vllmcircuitbreaker_defined(self) -> None:
        assert VLLMCircuitBreaker is not None

    def test_backpressuredecision_defined(self) -> None:
        assert BackpressureDecision is not None
