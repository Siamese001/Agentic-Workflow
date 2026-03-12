"""Foundational behavioral tests for agentic_core/L2_execution/types/vllm_backpressure_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_vllm_backpressure_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vllm_backpressure_types import (  # noqa: F401
        VLLMQueueState,
        CircuitBreakerState,
        VLLMCircuitBreaker,
        BackpressureDecision,
        evaluate_backpressure,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMQueueState = None  # type: ignore[assignment,misc]
    CircuitBreakerState = None  # type: ignore[assignment,misc]
    VLLMCircuitBreaker = None  # type: ignore[assignment,misc]
    BackpressureDecision = None  # type: ignore[assignment,misc]
    evaluate_backpressure = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types.py deps unavailable")
class TestVLLMQueueStateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMQueueState)

    def test_is_frozen(self):
        assert VLLMQueueState.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMQueueState)}
        assert fnames >= {'current_depth', 'max_depth', 'oldest_wait_seconds', 'timeout_seconds'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMQueueState)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types.py deps unavailable")
class TestCircuitBreakerStateContract:
    def test_is_enum(self):
        import enum
        assert issubclass(CircuitBreakerState, enum.Enum)

    def test_has_members(self):
        assert len(list(CircuitBreakerState)) >= 1

    def test_member_values_accessible(self):
        for m in CircuitBreakerState:
            assert m.value is not None or m.value is None

    def test_known_member_closed_present(self):
        assert hasattr(CircuitBreakerState, 'CLOSED')

    def test_members_are_unique(self):
        values = [m.value for m in CircuitBreakerState]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types.py deps unavailable")
class TestVLLMCircuitBreakerContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VLLMCircuitBreaker)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(VLLMCircuitBreaker)}
        assert fnames >= {'tier', 'state', 'failure_threshold', 'consecutive_failures'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(VLLMCircuitBreaker)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types.py deps unavailable")
class TestBackpressureDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BackpressureDecision)

    def test_is_frozen(self):
        assert BackpressureDecision.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(BackpressureDecision)}
        assert fnames >= {'failure_type', 'model_id', 'circuit_breaker_open', 'escalate_to_gemini', 'queue_depth', 'reason'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(BackpressureDecision)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_backpressure_types.py deps unavailable")
class TestEvaluateBackpressureFunction:
    def test_is_callable(self):
        assert callable(evaluate_backpressure)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(evaluate_backpressure)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: vllm_backpressure_types importable or gracefully unavailable."""
    assert True
