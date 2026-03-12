"""ADG-driven tests for L2_execution/types/blast_radius_controls_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.blast_radius_controls_types import (
    BlastRadiusControls,
    BlastRadiusExceeded,
)


class TestBlastRadiusExceeded:
    def test_is_runtime_error(self):
        assert issubclass(BlastRadiusExceeded, RuntimeError)

    def test_raises(self):
        with pytest.raises(BlastRadiusExceeded):
            raise BlastRadiusExceeded("exceeded max_compute_ms")


class TestBlastRadiusControls:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BlastRadiusControls)

    def test_is_frozen(self):
        ctrl = BlastRadiusControls(
            max_state_diff_bytes=1024,
            max_file_write_bytes=2048,
            max_compute_ms=5000,
        )
        with pytest.raises((AttributeError, TypeError)):
            ctrl.max_compute_ms = 9999

    def test_creates(self):
        ctrl = BlastRadiusControls(
            max_state_diff_bytes=1024,
            max_file_write_bytes=2048,
            max_compute_ms=5000,
        )
        assert ctrl.max_state_diff_bytes == 1024
        assert ctrl.max_compute_ms == 5000
