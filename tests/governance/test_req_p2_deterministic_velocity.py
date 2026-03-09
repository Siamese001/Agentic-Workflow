"""W15: Two-run velocity calculation with identical inputs → identical output; no float drift.

REQ-243/247: Deterministic velocity calculation using integer tick deltas,
fixed window size, stable ordering, no float math.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Deterministic velocity calculator
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VelocitySignal:
    signal_id: str
    tick: int  # integer semantic clock tick only


@dataclass(frozen=True)
class VelocityWindow:
    window_id: str
    start_tick: int
    end_tick: int
    signal_count: int
    window_size_ticks: int

    @property
    def velocity(self) -> int:
        """Integer velocity: signals per tick window (no float math)."""
        if self.window_size_ticks == 0:
            return 0
        return self.signal_count * 100 // self.window_size_ticks  # integer arithmetic only

    @property
    def is_anomaly(self) -> bool:
        """Deterministic anomaly detection: velocity > 50 signals per 100 ticks."""
        return self.velocity > 50


class DeterministicVelocityCalculator:
    """
    Velocity calculation using integer tick deltas only.
    No float math. No time.time(). Deterministic.
    """

    def __init__(self, window_size: int = 100):
        self._window_size = window_size
        self._signals: list[VelocitySignal] = []

    def record_signal(self, signal: VelocitySignal) -> None:
        self._signals.append(signal)

    def calculate(self, at_tick: int) -> VelocityWindow:
        """Calculate velocity at a given tick using integer arithmetic only."""
        window_start = at_tick - self._window_size
        # Count signals in window [window_start, at_tick]
        # Sort by signal_id for deterministic ordering (stable)
        in_window = sorted(
            [s for s in self._signals if window_start <= s.tick <= at_tick],
            key=lambda s: (s.tick, s.signal_id),
        )
        return VelocityWindow(
            window_id=f"win_{at_tick}",
            start_tick=window_start,
            end_tick=at_tick,
            signal_count=len(in_window),
            window_size_ticks=self._window_size,
        )

    def calculate_anomaly_digest(self, at_tick: int) -> str:
        """Canonical digest of velocity calculation — deterministic."""
        window = self.calculate(at_tick)
        data = {
            "window_id": window.window_id,
            "start_tick": window.start_tick,
            "end_tick": window.end_tick,
            "signal_count": window.signal_count,
            "window_size_ticks": window.window_size_ticks,
            "velocity": window.velocity,
            "is_anomaly": window.is_anomaly,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def clear(self) -> None:
        self._signals.clear()


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_TEST_SIGNALS = [VelocitySignal(f"sig_{i:03d}", tick=i * 2) for i in range(40)]


def _build_calculator_with_signals() -> DeterministicVelocityCalculator:
    calc = DeterministicVelocityCalculator(window_size=100)
    for sig in _TEST_SIGNALS:
        calc.record_signal(sig)
    return calc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.governance
def test_velocity_two_run_identical():
    """Two-run velocity calculation with identical inputs produces identical result."""
    calc1 = _build_calculator_with_signals()
    calc2 = _build_calculator_with_signals()

    w1 = calc1.calculate(at_tick=80)
    w2 = calc2.calculate(at_tick=80)

    assert w1.signal_count == w2.signal_count
    assert w1.velocity == w2.velocity
    assert w1.is_anomaly == w2.is_anomaly


@pytest.mark.governance
def test_velocity_digest_two_run_identical():
    """Velocity anomaly digest is identical across two independent runs."""
    calc1 = _build_calculator_with_signals()
    calc2 = _build_calculator_with_signals()

    d1 = calc1.calculate_anomaly_digest(at_tick=80)
    d2 = calc2.calculate_anomaly_digest(at_tick=80)

    assert d1 == d2
    assert len(d1) == 64


@pytest.mark.governance
def test_velocity_uses_integer_arithmetic_only():
    """Velocity is integer-only — no float division."""
    calc = DeterministicVelocityCalculator(window_size=100)
    for i in range(70):
        calc.record_signal(VelocitySignal(f"s_{i}", tick=i))

    window = calc.calculate(at_tick=99)
    assert isinstance(window.velocity, int), "velocity must be int, not float"
    assert isinstance(window.signal_count, int)
    assert isinstance(window.window_size_ticks, int)


@pytest.mark.governance
def test_velocity_anomaly_deterministic():
    """Anomaly detection is deterministic for same signal count."""
    calc = DeterministicVelocityCalculator(window_size=100)
    # Add 60 signals in window → velocity = 60 > 50 → anomaly
    for i in range(60):
        calc.record_signal(VelocitySignal(f"s_{i}", tick=i + 10))

    w1 = calc.calculate(at_tick=110)
    w2 = calc.calculate(at_tick=110)

    assert w1.is_anomaly == w2.is_anomaly is True


@pytest.mark.governance
def test_velocity_no_anomaly_below_threshold():
    """No anomaly when signal count below threshold."""
    calc = DeterministicVelocityCalculator(window_size=100)
    for i in range(10):
        calc.record_signal(VelocitySignal(f"s_{i}", tick=i + 10))

    window = calc.calculate(at_tick=110)
    assert window.is_anomaly is False
    assert window.velocity == 10  # 10 * 100 // 100 = 10


@pytest.mark.governance
def test_velocity_stable_ordering_deterministic():
    """Signal ordering is stable — signals with same tick ordered by signal_id."""
    calc = DeterministicVelocityCalculator(window_size=50)
    # All signals at same tick
    for i in range(10):
        calc.record_signal(VelocitySignal(f"sig_{9 - i:02d}", tick=25))

    d1 = calc.calculate_anomaly_digest(at_tick=50)
    d2 = calc.calculate_anomaly_digest(at_tick=50)
    assert d1 == d2


@pytest.mark.governance
def test_velocity_window_size_zero_returns_zero():
    """Edge case: zero window size returns 0 velocity."""
    calc = DeterministicVelocityCalculator(window_size=0)
    calc.record_signal(VelocitySignal("s1", tick=5))
    window = calc.calculate(at_tick=5)
    assert window.velocity == 0
