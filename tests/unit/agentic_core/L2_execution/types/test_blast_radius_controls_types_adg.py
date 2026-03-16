"""ADG-driven tests for L2_execution/types/blast_radius_controls_types.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_blast_radius_controls_types_adg")
_emit_applies_guardrail("p0", "test_blast_radius_controls_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_blast_radius_controls_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_blast_radius_controls_types_adg", "state_snapshot")
emit_replay_key("p0", "test_blast_radius_controls_types_adg")
emit_determinism_digest("p0", "test_blast_radius_controls_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
