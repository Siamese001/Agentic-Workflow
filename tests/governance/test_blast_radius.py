"""
Tests for BlastRadiusControls execution budget caps.

Phase 3.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.types.blast_radius_controls import (
    DEFAULT_BLAST_RADIUS,
    BlastRadiusControls,
    BlastRadiusExceeded,
)


class TestBlastRadiusControlsDefaults:
    def test_default_instance(self) -> None:
        b = BlastRadiusControls()
        assert b.max_state_diff_bytes == 65_536
        assert b.max_file_write_bytes == 1_048_576
        assert b.max_compute_ms == 30_000
        assert b.max_parallel_branches == 4
        assert b.max_tool_calls_per_minute == 120

    def test_default_blast_radius_singleton(self) -> None:
        assert isinstance(DEFAULT_BLAST_RADIUS, BlastRadiusControls)

    def test_frozen_dataclass(self) -> None:
        b = BlastRadiusControls()
        with pytest.raises((AttributeError, TypeError)):
            b.max_state_diff_bytes = 999  # type: ignore[misc]


class TestBlastRadiusControlsValidation:
    def test_zero_max_state_diff_rejected(self) -> None:
        with pytest.raises(ValueError):
            BlastRadiusControls(max_state_diff_bytes=0)

    def test_negative_compute_ms_rejected(self) -> None:
        with pytest.raises(ValueError):
            BlastRadiusControls(max_compute_ms=-1)


class TestBlastRadiusControlsEnforcement:
    def test_state_diff_within_limit(self) -> None:
        b = BlastRadiusControls(max_state_diff_bytes=100)
        b.check_state_diff(99)  # should not raise

    def test_state_diff_at_limit(self) -> None:
        b = BlastRadiusControls(max_state_diff_bytes=100)
        b.check_state_diff(100)  # should not raise

    def test_state_diff_exceeds_limit(self) -> None:
        b = BlastRadiusControls(max_state_diff_bytes=100)
        with pytest.raises(BlastRadiusExceeded, match="State diff"):
            b.check_state_diff(101)

    def test_file_write_within_limit(self) -> None:
        b = BlastRadiusControls(max_file_write_bytes=500)
        b.check_file_write(499)

    def test_file_write_exceeds_limit(self) -> None:
        b = BlastRadiusControls(max_file_write_bytes=500)
        with pytest.raises(BlastRadiusExceeded, match="write"):
            b.check_file_write(501)

    def test_compute_within_limit(self) -> None:
        b = BlastRadiusControls(max_compute_ms=1000)
        b.check_compute(999)

    def test_compute_exceeds_limit(self) -> None:
        b = BlastRadiusControls(max_compute_ms=1000)
        with pytest.raises(BlastRadiusExceeded, match="Compute"):
            b.check_compute(1001)

    def test_parallel_branches_within_limit(self) -> None:
        b = BlastRadiusControls(max_parallel_branches=4)
        b.check_parallel_branches(4)

    def test_parallel_branches_exceeds_limit(self) -> None:
        b = BlastRadiusControls(max_parallel_branches=4)
        with pytest.raises(BlastRadiusExceeded, match="branches"):
            b.check_parallel_branches(5)

    def test_tool_call_rate_within_limit(self) -> None:
        b = BlastRadiusControls(max_tool_calls_per_minute=60)
        b.check_tool_call_rate(60)

    def test_tool_call_rate_exceeds_limit(self) -> None:
        b = BlastRadiusControls(max_tool_calls_per_minute=60)
        with pytest.raises(BlastRadiusExceeded, match="rate"):
            b.check_tool_call_rate(61)
