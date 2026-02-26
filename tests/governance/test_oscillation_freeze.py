"""
Tests for OscillationDetector adaptive thrashing prevention.

Phase 6.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance

from system_learning.enforcement.oscillation_detector import (
    OscillationDetector,
    ParameterFrozenError,
)


class TestOscillationDetectorBasic:
    def setup_method(self) -> None:
        self.detector = OscillationDetector(cooldown_window=10, freeze_cycles=5)

    def test_single_change_no_freeze(self) -> None:
        self.detector.record_change("threshold_a", 0.7, cycle=1)

    def test_same_value_repeated_no_freeze(self) -> None:
        for i in range(5):
            self.detector.record_change("threshold_a", 0.7, cycle=i + 1)

    def test_two_different_values_no_freeze(self) -> None:
        self.detector.record_change("threshold_a", 0.7, cycle=1)
        self.detector.record_change("threshold_a", 0.5, cycle=2)

    def test_oscillation_triggers_freeze(self) -> None:
        self.detector.record_change("threshold_a", 0.7, cycle=1)
        self.detector.record_change("threshold_a", 0.5, cycle=2)
        with pytest.raises(ParameterFrozenError):
            self.detector.record_change("threshold_a", 0.7, cycle=3)

    def test_freeze_blocks_further_changes(self) -> None:
        self.detector.record_change("p", 1, cycle=1)
        self.detector.record_change("p", 2, cycle=2)
        try:
            self.detector.record_change("p", 1, cycle=3)
        except ParameterFrozenError:
            pass
        with pytest.raises(ParameterFrozenError):
            self.detector.record_change("p", 3, cycle=4)

    def test_freeze_expires_after_n_cycles(self) -> None:
        detector = OscillationDetector(cooldown_window=3, freeze_cycles=3)
        detector.record_change("p", 1, cycle=1)
        detector.record_change("p", 2, cycle=2)
        try:
            detector.record_change("p", 1, cycle=3)  # triggers freeze until cycle 6
        except ParameterFrozenError:
            pass
        # cycle 4,5,6 still frozen; cycle 7 past freeze_until=6 and uses brand-new value
        assert detector.is_frozen("p", cycle=6) is True
        assert detector.is_frozen("p", cycle=7) is False

    def test_different_params_independent(self) -> None:
        self.detector.record_change("param_a", 1, cycle=1)
        self.detector.record_change("param_a", 2, cycle=2)
        try:
            self.detector.record_change("param_a", 1, cycle=3)
        except ParameterFrozenError:
            pass
        # param_b unaffected
        self.detector.record_change("param_b", 0.9, cycle=3)


class TestOscillationDetectorIsFrozen:
    def test_not_frozen_initially(self) -> None:
        d = OscillationDetector()
        assert d.is_frozen("p", cycle=1) is False

    def test_frozen_after_oscillation(self) -> None:
        d = OscillationDetector(cooldown_window=5, freeze_cycles=5)
        d.record_change("p", 1, cycle=1)
        d.record_change("p", 2, cycle=2)
        try:
            d.record_change("p", 1, cycle=3)
        except ParameterFrozenError:
            pass
        assert d.is_frozen("p", cycle=4) is True

    def test_frozen_count(self) -> None:
        d = OscillationDetector(cooldown_window=5, freeze_cycles=10)
        d.record_change("p1", 1, cycle=1)
        d.record_change("p1", 2, cycle=2)
        try:
            d.record_change("p1", 1, cycle=3)
        except ParameterFrozenError:
            pass
        assert d.frozen_count() >= 1


class TestOscillationDetectorConstructor:
    def test_invalid_cooldown_window(self) -> None:
        with pytest.raises(ValueError, match="cooldown_window"):
            OscillationDetector(cooldown_window=1)

    def test_invalid_freeze_cycles(self) -> None:
        with pytest.raises(ValueError, match="freeze_cycles"):
            OscillationDetector(freeze_cycles=0)

    def test_reset_for_testing(self) -> None:
        d = OscillationDetector()
        d.record_change("p", 1, cycle=1)
        d.record_change("p", 2, cycle=2)
        try:
            d.record_change("p", 1, cycle=3)
        except ParameterFrozenError:
            pass
        d.reset_for_testing()
        # after reset, should allow changes again
        d.record_change("p", 1, cycle=1)
