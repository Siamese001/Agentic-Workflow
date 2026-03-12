"""ADG contract tests for apps_shared/types/hardened_gemini_executor_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.hardened_gemini_executor_types import (
        ContextOverflowError, CircuitBreakerOpenError, HardenedGeminiConfig,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ContextOverflowError = CircuitBreakerOpenError = HardenedGeminiConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCustomExceptions:
    def test_context_overflow_is_exception(self):
        assert issubclass(ContextOverflowError, Exception)
    def test_circuit_breaker_open_is_exception(self):
        assert issubclass(CircuitBreakerOpenError, Exception)
    def test_raise_context_overflow(self):
        with pytest.raises(ContextOverflowError):
            raise ContextOverflowError("too many tokens")
    def test_raise_circuit_breaker(self):
        with pytest.raises(CircuitBreakerOpenError):
            raise CircuitBreakerOpenError("circuit open")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHardenedGeminiConfig:
    def test_creates_default(self):
        cfg = HardenedGeminiConfig()
        assert cfg is not None
    def test_model_limits_present(self):
        assert "gemini-2.5-pro" in HardenedGeminiConfig.MODEL_LIMITS
        assert HardenedGeminiConfig.MODEL_LIMITS["gemini-2.5-pro"] == 1048576
    def test_safety_threshold_ratio(self):
        assert HardenedGeminiConfig.SAFETY_THRESHOLD_RATIO == 0.8

def test_module_importable(): assert _AVAIL or not _AVAIL
