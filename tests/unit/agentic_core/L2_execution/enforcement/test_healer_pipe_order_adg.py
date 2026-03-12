"""ADG-driven tests for L2_execution/enforcement/healer_pipe_order.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.healer_pipe_order import enforce_healer_pipe_order


VALID_10_STEPS = ("s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10")


class TestEnforceHealerPipeOrder:
    def test_callable(self):
        assert callable(enforce_healer_pipe_order)

    def test_passes_when_matching(self):
        enforce_healer_pipe_order(VALID_10_STEPS, list(VALID_10_STEPS))

    def test_raises_permission_error_on_wrong_order(self):
        reordered = list(VALID_10_STEPS)
        reordered[0], reordered[1] = reordered[1], reordered[0]
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(VALID_10_STEPS, reordered)

    def test_raises_permission_error_on_extra_step(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(VALID_10_STEPS, list(VALID_10_STEPS) + ["s11"])

    def test_raises_permission_error_on_missing_step(self):
        with pytest.raises(PermissionError):
            enforce_healer_pipe_order(VALID_10_STEPS, list(VALID_10_STEPS[:-1]))

    def test_asserts_10_expected_steps(self):
        with pytest.raises(AssertionError):
            enforce_healer_pipe_order(("only", "9", "steps", "here", "a", "b", "c", "d", "e"), [])
