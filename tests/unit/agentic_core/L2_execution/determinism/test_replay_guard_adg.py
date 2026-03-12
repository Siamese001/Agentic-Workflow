"""ADG-driven tests for L2_execution/determinism/replay_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.determinism.replay_guard import (
    ReplayGuard,
    ReplayViolation,
)


class TestReplayViolation:
    def test_is_runtime_error(self):
        assert issubclass(ReplayViolation, RuntimeError)

    def test_raises(self):
        with pytest.raises(ReplayViolation):
            raise ReplayViolation("nondeterminism detected")


class TestReplayGuard:
    def test_creates(self):
        guard = ReplayGuard(deterministic_seed=42)
        assert guard is not None

    def test_context_manager_enter_exit(self):
        guard = ReplayGuard(deterministic_seed=42)
        guard.__enter__()
        guard.__exit__(None, None, None)

    def test_has_enter_exit(self):
        assert hasattr(ReplayGuard, "__enter__")
        assert hasattr(ReplayGuard, "__exit__")
