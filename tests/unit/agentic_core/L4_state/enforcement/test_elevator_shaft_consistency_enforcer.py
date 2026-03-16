"""Tests for ElevatorShaftConsistencyEnforcer — runtime semantic clock sync gate."""

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

_emit_records_execution_trace("p0", "evidence", "test_elevator_shaft_consistency_enforcer")
_emit_applies_guardrail("p0", "test_elevator_shaft_consistency_enforcer", "p0_governance")
_emit_reads_policy_state("p0", "test_elevator_shaft_consistency_enforcer", "policy_binding")
_emit_snapshots_state("p0", "test_elevator_shaft_consistency_enforcer", "state_snapshot")
emit_replay_key("p0", "test_elevator_shaft_consistency_enforcer")
emit_determinism_digest("p0", "test_elevator_shaft_consistency_enforcer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
    ClockSyncViolation,
    ElevatorShaftConsistencyEnforcer,
    MonotonicityViolation,
    WallClockContaminationError,
    assert_clock_synchronized,
    assert_no_wall_clock_in_module,
    get_enforcer,
    reset_enforcer,
)


def _snap(tick: int) -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=tick)


class TestAssertClockSynchronized:
    def test_identical_ticks_passes(self):
        assert_clock_synchronized(_snap(10), _snap(10))

    def test_within_tolerance_passes(self):
        assert_clock_synchronized(_snap(10), _snap(14), tolerance=5)

    def test_at_exact_tolerance_passes(self):
        assert_clock_synchronized(_snap(10), _snap(15), tolerance=5)

    def test_exceeds_tolerance_raises(self):
        with pytest.raises(ClockSyncViolation, match="drift 6 exceeds tolerance 5"):
            assert_clock_synchronized(_snap(10), _snap(16), tolerance=5)

    def test_reverse_order_drift_raises(self):
        with pytest.raises(ClockSyncViolation):
            assert_clock_synchronized(_snap(20), _snap(10), tolerance=5)

    def test_zero_tolerance_different_ticks_raises(self):
        with pytest.raises(ClockSyncViolation):
            assert_clock_synchronized(_snap(1), _snap(2), tolerance=0)

    def test_zero_tolerance_same_tick_passes(self):
        assert_clock_synchronized(_snap(5), _snap(5), tolerance=0)

    def test_context_in_error_message(self):
        with pytest.raises(ClockSyncViolation, match="L0<>L2"):
            assert_clock_synchronized(_snap(0), _snap(100), tolerance=5, context="L0<>L2")


class TestAssertNoWallClockInModule:
    def test_clean_module_passes(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1 + 2\n", encoding="utf-8")
        assert_no_wall_clock_in_module(module)

    def test_wall_clock_module_raises(self, tmp_path):
        module = tmp_path / "dirty.py"
        module.write_text("import time\ndef f():\n    return time.time()\n", encoding="utf-8")
        with pytest.raises(WallClockContaminationError, match="wall-clock contamination"):
            assert_no_wall_clock_in_module(module, context="test")

    def test_missing_module_raises(self, tmp_path):
        missing = tmp_path / "nonexistent.py"
        with pytest.raises(WallClockContaminationError):
            assert_no_wall_clock_in_module(missing)


class TestElevatorShaftConsistencyEnforcerRecordAdvance:
    def test_first_advance_recorded(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        assert enforcer.layer_tick("L0") == 5

    def test_monotonic_advance_ok(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L0", _snap(10))
        assert enforcer.layer_tick("L0") == 10

    def test_same_tick_advance_ok(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L0", _snap(5))
        assert enforcer.layer_tick("L0") == 5

    def test_non_monotonic_advance_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(10))
        with pytest.raises(MonotonicityViolation, match="non-monotonic tick"):
            enforcer.record_advance("L0", _snap(9))

    def test_independent_layers(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L2", _snap(3))
        assert enforcer.layer_tick("L0") == 5
        assert enforcer.layer_tick("L2") == 3

    def test_unknown_layer_returns_none(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        assert enforcer.layer_tick("L99") is None


class TestElevatorShaftConsistencyEnforcerAssertSync:
    def test_synchronized_layers_passes(self):
        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=5)
        enforcer.record_advance("L0", _snap(10))
        enforcer.record_advance("L2", _snap(12))
        enforcer.assert_layers_synchronized("L0", "L2")

    def test_drifted_layers_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer(drift_tolerance=3)
        enforcer.record_advance("L0", _snap(10))
        enforcer.record_advance("L2", _snap(20))
        with pytest.raises(ClockSyncViolation):
            enforcer.assert_layers_synchronized("L0", "L2")

    def test_missing_layer_a_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L2", _snap(5))
        with pytest.raises(KeyError, match="L0"):
            enforcer.assert_layers_synchronized("L0", "L2")

    def test_missing_layer_b_raises(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        with pytest.raises(KeyError, match="L2"):
            enforcer.assert_layers_synchronized("L0", "L2")


class TestElevatorShaftConsistencyEnforcerRegisterModule:
    def test_clean_module_registered(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.register_module(module)

    def test_dirty_module_raises(self, tmp_path):
        module = tmp_path / "dirty.py"
        module.write_text("import datetime\ndef f():\n    return datetime.utcnow()\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        with pytest.raises(WallClockContaminationError):
            enforcer.register_module(module)

    def test_module_not_scanned_twice(self, tmp_path):
        module = tmp_path / "clean.py"
        module.write_text("x = 1\n", encoding="utf-8")
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.register_module(module)
        enforcer.register_module(module)


class TestElevatorShaftConsistencyEnforcerSummary:
    def test_summary_contains_all_layers(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(5))
        enforcer.record_advance("L2", _snap(3))
        s = enforcer.summary()
        assert "L0" in s
        assert "L2" in s
        assert s["L0"]["last_tick"] == 5
        assert s["L2"]["last_tick"] == 3

    def test_summary_tracks_advance_count(self):
        enforcer = ElevatorShaftConsistencyEnforcer()
        enforcer.record_advance("L0", _snap(1))
        enforcer.record_advance("L0", _snap(2))
        enforcer.record_advance("L0", _snap(3))
        assert enforcer.summary()["L0"]["advance_count"] == 3


class TestGlobalEnforcer:
    def setup_method(self):
        reset_enforcer()

    def test_get_enforcer_returns_instance(self):
        e = get_enforcer()
        assert isinstance(e, ElevatorShaftConsistencyEnforcer)

    def test_get_enforcer_singleton(self):
        e1 = get_enforcer()
        e2 = get_enforcer()
        assert e1 is e2

    def test_reset_enforcer_creates_fresh_instance(self):
        e1 = get_enforcer()
        e1.record_advance("L0", _snap(100))
        reset_enforcer()
        e2 = get_enforcer()
        assert e2 is not e1
        assert e2.layer_tick("L0") is None

    def teardown_method(self):
        reset_enforcer()
