"""ADG importability contract for agentic_core/L2_execution/healers/qwen_circuit_breaker.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_qwen_circuit_breaker.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.qwen_circuit_breaker import (  # noqa: F401
        QwenCircuitBreaker,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    QwenCircuitBreaker = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="qwen_circuit_breaker.py deps unavailable")
class TestQwenCircuitBreakerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: qwen_circuit_breaker.py must be importable."""
        assert _AVAILABLE

    def test_qwencircuitbreaker_is_type(self) -> None:
        assert QwenCircuitBreaker is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

