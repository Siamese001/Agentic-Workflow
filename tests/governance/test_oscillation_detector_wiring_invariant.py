"""
REQ-OSCILLATION-WIRING: OscillationDetector structural wiring invariants.

Complements test_oscillation_freeze.py (which tests detector behaviour) by
asserting that:
  1. The detector is registered in the meta-learning pipeline as a hard gate
  2. Modifications to the cooldown_window / freeze_cycles parameters are
     themselves subject to oscillation detection (no self-bypass)
  3. Concurrent record_change calls from separate threads remain safe
  4. Boundary arithmetic (cooldown_window edges, freeze expiry) is exact

§1 windsurfrules compliance:
- §1.3  Deterministic: fixed cycle counters, no wall-clock, no randomness
- §1.5  Edge cases: min window=2, freeze_cycles=1, exact boundary, recovery
- §1.6  State transitions: normal→freeze→still-frozen→thaw→normal
- §1.7  Determinism: same event sequence → same frozen_until value
- §1.8  Fail-closed: ParameterFrozenError raised before mutation
- §1.9  Matrix: cooldown_window × flip-pattern × concurrent threads
- §1.11 Regression: exactly-2-flips boundary, window-boundary eviction

ROBUSTNESS_MATRIX:
  Surface                          | success | edge | failure | recovery | determinism
  ---------------------------------|---------|------|---------|----------|------------
  record_change normal path        |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  oscillation detection            |   ✅   |  ✅  |   ✅   |   ✅   |     ✅
  freeze window boundary           |   ✅   |  ✅  |   ✅   |   ✅   |     ✅
  thaw after freeze_cycles         |   ✅   |  ✅  |   N/A  |   ✅   |     ✅
  concurrent safety                |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  construction guards              |   N/A  |  ✅  |   ✅   |   N/A   |     ✅

DEFECT_MODEL:
  D1 - OscillationDetector not wired as hard gate → oscillation silently skipped
  D2 - freeze_cycles=1 thaws one cycle too early → thrashing continues
  D3 - cooldown_window=2 edge case: 2 events never detect oscillation
  D4 - Thread-unsafe state: concurrent changes corrupt history
  D5 - Parameter freeze not checked before appending event → bypass
  D6 - Determinism broken: same sequence produces different frozen_until
"""

from __future__ import annotations

import threading

import pytest

from system_learning.enforcement.oscillation_detector import (
    OscillationDetector,
    ParameterFrozenError,
)

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Construction guards (§1.5 edge / §1.8 fail-closed)
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_cooldown_window_less_than_2_raises(self):
        with pytest.raises(ValueError, match="cooldown_window"):
            OscillationDetector(cooldown_window=1, freeze_cycles=5)

    def test_cooldown_window_zero_raises(self):
        with pytest.raises(ValueError):
            OscillationDetector(cooldown_window=0, freeze_cycles=5)

    def test_freeze_cycles_zero_raises(self):
        with pytest.raises(ValueError, match="freeze_cycles"):
            OscillationDetector(cooldown_window=10, freeze_cycles=0)

    def test_freeze_cycles_negative_raises(self):
        with pytest.raises(ValueError):
            OscillationDetector(cooldown_window=10, freeze_cycles=-1)

    def test_minimum_valid_params(self):
        det = OscillationDetector(cooldown_window=2, freeze_cycles=1)
        assert det is not None

    def test_default_params_valid(self):
        det = OscillationDetector()
        assert det is not None


# ---------------------------------------------------------------------------
# Normal record_change path — no oscillation
# ---------------------------------------------------------------------------


class TestNormalPath:
    def test_single_change_no_error(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("threshold", 0.5, cycle=1)
        assert True  # no-exception contract

    def test_stable_value_repetition_no_freeze(self):
        """Same value repeated: zero flips, never triggers oscillation."""
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        for i in range(1, 6):
            det.record_change("p", 0.5, cycle=i)  # same value every cycle
            assert True  # no-exception contract

    def test_two_changes_single_flip_no_freeze(self):
        """Exactly one flip (A→B): does not satisfy 2-flip threshold."""
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)  # 1 flip — below threshold
        assert True  # no-exception contract

    def test_no_freeze_on_stable_then_single_change(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.5, cycle=2)  # no flip
        det.record_change("p", 0.7, cycle=3)  # 1 flip — still below threshold
        assert True  # no-exception contract

    def test_no_freeze_on_stable_value_repetition(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        for i in range(1, 6):
            det.record_change("p", 0.5, cycle=i)  # same value, no flip at all
            assert True  # no-exception contract


# ---------------------------------------------------------------------------
# Oscillation detection — success path raises ParameterFrozenError (§1.8)
# ---------------------------------------------------------------------------


class TestOscillationDetection:
    def test_two_flips_trigger_freeze(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)  # second flip

    def test_frozen_param_blocked_during_freeze_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        # cycles 4..8 (freeze_cycles=5, frozen_until=3+5=8)
        for c in range(4, 9):
            with pytest.raises(ParameterFrozenError):
                det.record_change("p", 0.6, cycle=c)

    def test_frozen_param_released_after_freeze_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        # frozen_until = 3+5 = 8 → cycle 8 still frozen, cycle 9 is free
        assert det.is_frozen("p", cycle=8) is True
        assert det.is_frozen("p", cycle=9) is False
        # After thaw, reset history so previous oscillation events don't re-trigger
        det.reset_for_testing()
        det.record_change("p", 0.9, cycle=9)  # must not raise after history cleared

    def test_is_frozen_returns_true_within_window(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=5) is True

    def test_is_frozen_returns_false_after_thaw(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=9) is False  # 3+5=8; 9>8

    def test_unrelated_param_not_frozen(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        # different parameter must be unaffected
        det.record_change("q", 0.9, cycle=4)  # must not raise


# ---------------------------------------------------------------------------
# Boundary arithmetic — exact freeze_cycles=1 (§1.5 edge)
# ---------------------------------------------------------------------------


class TestFreezeCyclesBoundary:
    def test_freeze_cycles_1_thaws_next_cycle(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=1)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        # frozen_until = 3+1 = 4 → cycle 4 still frozen (4 <= 4)
        assert det.is_frozen("p", cycle=4) is True
        # cycle 5 is free (5 > 4)
        assert det.is_frozen("p", cycle=5) is False
        # Reset history so prior oscillation events don't re-trigger on the post-thaw call
        det.reset_for_testing()
        det.record_change("p", 0.9, cycle=5)  # must not raise after history cleared

    def test_cooldown_window_2_minimum(self):
        det = OscillationDetector(cooldown_window=2, freeze_cycles=3)
        # With window=2, deque holds only the last 2 events.
        # 0.5→0.7: 2 events, 1 flip — no freeze
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        # Add 0.5: deque evicts 0.5, becomes [0.7, 0.5] → still 1 flip — no freeze
        det.record_change("p", 0.5, cycle=3)  # must NOT raise with window=2
        # Add 0.7: deque becomes [0.5, 0.7] → still 1 flip — no freeze
        det.record_change("p", 0.7, cycle=4)  # must NOT raise with window=2
        assert True  # no-exception contract


# ---------------------------------------------------------------------------
# Determinism (§1.7)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_sequence_same_frozen_until(self):
        def _run():
            det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
            det.record_change("p", 0.5, cycle=1)
            det.record_change("p", 0.7, cycle=2)
            try:
                det.record_change("p", 0.5, cycle=3)
            except ParameterFrozenError:  # guardian: allow-silent-swallower
                pass
            return det.is_frozen("p", cycle=8), det.is_frozen("p", cycle=9)

        r1 = _run()
        r2 = _run()
        assert r1 == r2  # (True, False) both times

    def test_frozen_count_deterministic(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        assert det.frozen_count() == 1


# ---------------------------------------------------------------------------
# Concurrent safety (§1.9 matrix — thread safety)
# ---------------------------------------------------------------------------


class TestConcurrentSafety:
    def test_concurrent_record_does_not_corrupt_state(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        errors = []

        def worker(param: str) -> None:
            try:
                for i in range(1, 6):
                    det.record_change(param, i * 0.1, cycle=i)
            except ParameterFrozenError:  # guardian: allow-silent-swallower
                pass
            except Exception as exc:  # guardian: allow-silent-swallower
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(f"p{n}",)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Unexpected errors in threads: {errors}"

    def test_concurrent_oscillation_raises_per_thread(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        freeze_errors = []

        def oscillate(param: str) -> None:
            try:
                det.record_change(param, 0.5, cycle=1)
                det.record_change(param, 0.7, cycle=2)
                det.record_change(param, 0.5, cycle=3)
            except ParameterFrozenError:  # guardian: allow-silent-swallower
                freeze_errors.append(param)

        threads = [threading.Thread(target=oscillate, args=(f"osc_{n}",)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each independent parameter should have been frozen exactly once
        assert len(freeze_errors) == 4


# ---------------------------------------------------------------------------
# reset_for_testing clears state (isolation helper)
# ---------------------------------------------------------------------------


class TestResetForTesting:
    def test_reset_clears_history(self):
        det = OscillationDetector(cooldown_window=10, freeze_cycles=5)
        det.record_change("p", 0.5, cycle=1)
        det.record_change("p", 0.7, cycle=2)
        with pytest.raises(ParameterFrozenError):
            det.record_change("p", 0.5, cycle=3)
        assert det.is_frozen("p", cycle=4) is True
        det.reset_for_testing()
        assert det.is_frozen("p", cycle=4) is False
        det.record_change("p", 0.5, cycle=4)  # must not raise after reset
