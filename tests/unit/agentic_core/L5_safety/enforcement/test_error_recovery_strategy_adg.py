"""ADG-driven tests for L5_safety/enforcement/error_recovery_strategy.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.error_recovery_strategy import ErrorRecoveryStrategy


class TestErrorRecoveryStrategy:
    def test_creates(self):
        s = ErrorRecoveryStrategy()
        assert s is not None

    def test_creates_with_kwargs(self):
        s = ErrorRecoveryStrategy(max_retries=3)
        assert s is not None

    def test_is_class(self):
        assert isinstance(ErrorRecoveryStrategy, type)

    def test_importable(self):
        assert callable(ErrorRecoveryStrategy)
