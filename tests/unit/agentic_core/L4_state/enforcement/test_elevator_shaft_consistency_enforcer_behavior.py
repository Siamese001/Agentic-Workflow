"""Behavioral tests for elevator_shaft_consistency_enforcer."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L4_state.enforcement.elevator_shaft_consistency_enforcer import (
    ClockSyncViolation,
    ElevatorShaftConsistencyEnforcer,
    LayerClockRecord,
    MonotonicityViolation,
    WallClockContaminationError,
    assert_clock_synchronized,
    assert_no_wall_clock_in_module,
    get_enforcer,
    reset_enforcer,
)


def snap(tick: int) -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=tick)


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_enforcer()


# ---- Exception classes ----------------------------------------------


class TestExceptions:
    @pytest.mark.parametrize(
        "exc",
        [
            ClockSyncViolation,
            MonotonicityViolation,
            WallClockContaminationError,
        ],
    )
    def test_inherits_runtime_error(self, exc: type) -> None:
        assert issubclass(exc, RuntimeError)


# ---- LayerClockRecord -----------------------------------------------


class TestLayerClockRecord:
    def test_defaults(self) -> None:
        r = LayerClockRecord(layer="L0")
        assert r.last_tick == 0
        assert r.advance_count == 0


# ---- assert_clock_synchronized --------------------------------------


class TestAssertClockSynchronized:
    def test_equal_ticks_pass(self) -> None:
        assert_clock_synchronized(snap(10), snap(10))

    def test_within_tolerance_passes(self) -> None:
        assert_clock_synchronized(snap(10), snap(13), tolerance=5)

    def test_exceeds_tolerance_raises(self) -> None:
        with pytest.raises(ClockSyncViolation, match="clock drift"):
            assert_clock_synchronized(snap(10), snap(20), tolerance=5)

    def test_context_in_error(self) -> None:
        with pytest.raises(ClockSyncViolation, match="myctx"):
            assert_clock_synchronized(snap(0), snap(100), tolerance=1, context="myctx")


# ---- ElevatorShaftConsistencyEnforcer -------------------------------


class TestEnforcerRecordAdvance:
    def test_first_advance_accepted(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(5))
        assert e.layer_tick("L0") == 5

    def test_monotonic_advance_accepted(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(5))
        e.record_advance("L0", snap(8))
        assert e.layer_tick("L0") == 8

    def test_non_monotonic_rejected(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(10))
        with pytest.raises(MonotonicityViolation, match="non-monotonic"):
            e.record_advance("L0", snap(5))

    def test_same_tick_accepted(self) -> None:
        # tick >= last_tick is valid (only strictly less is a violation)
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(5))
        e.record_advance("L0", snap(5))

    def test_advance_count_increments(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(1))
        e.record_advance("L0", snap(2))
        e.record_advance("L0", snap(3))
        assert e._layer_records["L0"].advance_count == 3


class TestAssertLayersSynchronized:
    def test_synced_layers_pass(self) -> None:
        e = ElevatorShaftConsistencyEnforcer(drift_tolerance=3)
        e.record_advance("L0", snap(10))
        e.record_advance("L1", snap(12))
        e.assert_layers_synchronized("L0", "L1")

    def test_drifted_layers_raise(self) -> None:
        e = ElevatorShaftConsistencyEnforcer(drift_tolerance=2)
        e.record_advance("L0", snap(10))
        e.record_advance("L1", snap(20))
        with pytest.raises(ClockSyncViolation):
            e.assert_layers_synchronized("L0", "L1")

    def test_unknown_layer_a_raises_keyerror(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L1", snap(5))
        with pytest.raises(KeyError, match="L0"):
            e.assert_layers_synchronized("L0", "L1")

    def test_unknown_layer_b_raises_keyerror(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(5))
        with pytest.raises(KeyError, match="L1"):
            e.assert_layers_synchronized("L0", "L1")


class TestLayerTick:
    def test_unknown_layer_returns_none(self) -> None:
        assert ElevatorShaftConsistencyEnforcer().layer_tick("L99") is None

    def test_known_layer_returns_tick(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(42))
        assert e.layer_tick("L0") == 42


class TestSummary:
    def test_empty_summary_has_adg_violates(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        summary = e.summary()
        assert "adg_violates" in summary

    def test_summary_tracks_layers(self) -> None:
        e = ElevatorShaftConsistencyEnforcer()
        e.record_advance("L0", snap(5))
        e.record_advance("L0", snap(7))
        e.record_advance("L1", snap(3))
        summary = e.summary()
        assert summary["L0"]["last_tick"] == 7
        assert summary["L0"]["advance_count"] == 2
        assert summary["L1"]["last_tick"] == 3


# ---- register_module (mocked wall-clock scanner) -------------------


class TestRegisterModule:
    def test_clean_module_registered(self, monkeypatch, tmp_path: Path) -> None:
        # Patch the scanner to return no violations
        import agentic_core.L6_observability.utils.engines.semantic_clock_validator as scv

        monkeypatch.setattr(scv, "scan_module_for_wallclock", lambda p: [])
        e = ElevatorShaftConsistencyEnforcer()
        fake = tmp_path / "clean.py"
        fake.write_text("pass", encoding="utf-8")
        logging.info("C3 write receipt: elevator-shaft clean module fixture written")
        e.register_module(fake)
        assert str(fake) in e._scanned_modules

    def test_contaminated_module_rejected(self, monkeypatch, tmp_path: Path) -> None:
        import agentic_core.L6_observability.utils.engines.semantic_clock_validator as scv

        monkeypatch.setattr(
            scv,
            "scan_module_for_wallclock",
            lambda p: ["time.time()"],
        )
        e = ElevatorShaftConsistencyEnforcer()
        with pytest.raises(WallClockContaminationError):
            e.register_module(tmp_path / "bad.py")

    def test_already_scanned_is_idempotent(
        self,
        monkeypatch,
        tmp_path: Path,
    ) -> None:
        import agentic_core.L6_observability.utils.engines.semantic_clock_validator as scv

        calls = {"n": 0}

        def fake_scan(p):
            calls["n"] += 1
            return []

        monkeypatch.setattr(scv, "scan_module_for_wallclock", fake_scan)
        e = ElevatorShaftConsistencyEnforcer()
        f = tmp_path / "x.py"
        e.register_module(f)
        e.register_module(f)  # second call must not re-scan
        assert calls["n"] == 1


# ---- assert_no_wall_clock_in_module --------------------------------


class TestAssertNoWallClockInModule:
    def test_clean_passes(self, monkeypatch, tmp_path: Path) -> None:
        import agentic_core.L6_observability.utils.engines.semantic_clock_validator as scv

        monkeypatch.setattr(scv, "scan_module_for_wallclock", lambda p: [])
        assert_no_wall_clock_in_module(tmp_path / "x.py")

    def test_contaminated_raises(self, monkeypatch, tmp_path: Path) -> None:
        import agentic_core.L6_observability.utils.engines.semantic_clock_validator as scv

        monkeypatch.setattr(
            scv,
            "scan_module_for_wallclock",
            lambda p: ["datetime.now()"],
        )
        with pytest.raises(WallClockContaminationError, match="contamination"):
            assert_no_wall_clock_in_module(tmp_path / "x.py", context="test")


# ---- get_enforcer / reset_enforcer ---------------------------------


class TestGlobalEnforcer:
    def test_get_enforcer_returns_instance(self) -> None:
        e = get_enforcer()
        assert isinstance(e, ElevatorShaftConsistencyEnforcer)

    def test_get_enforcer_returns_same_singleton(self) -> None:
        a = get_enforcer()
        b = get_enforcer()
        assert a is b

    def test_reset_enforcer_clears_singleton(self) -> None:
        a = get_enforcer()
        reset_enforcer()
        b = get_enforcer()
        assert a is not b
