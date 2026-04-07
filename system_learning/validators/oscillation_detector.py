"""G-16-22: Oscillation detector for System Learning optimization cycles.

Detects oscillating parameter values and computes freeze decisions to prevent
unstable optimization loops.

Invariants:
  - Deterministic pattern detection
  - No wall-clock access (now_utc injected)
  - Fail-closed on oscillation detection
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OscillationPolicy:
    """Policy for oscillation detection and freeze behavior.

    Fields
    ------
    window : int
        Number of recent values to check for oscillation (fixed at 5 in tests).
    epsilon : float
        Tolerance for value comparison (values within epsilon are considered equal).
    freeze_seconds : int
        Duration to freeze optimization if oscillation detected.
    """

    window: int
    epsilon: float
    freeze_seconds: int


@dataclass(frozen=True, slots=True)
class FreezeDecision:
    """Decision on whether to freeze optimization.

    Fields
    ------
    should_freeze : bool
        Whether optimization should be frozen.
    freeze_until_utc : int | None
        Unix timestamp when freeze expires (None if not frozen).
    """

    should_freeze: bool
    freeze_until_utc: int | None


def detect_oscillation(values: tuple[float, ...], policy: OscillationPolicy) -> bool:
    """Detect oscillation pattern in recent values.

    Oscillation is detected if the last N values alternate between two distinct
    values (within epsilon tolerance).

    Parameters
    ----------
    values : tuple[float, ...]
        Recent parameter values (ordered chronologically).
    policy : OscillationPolicy
        Oscillation detection policy.

    Returns
    -------
    bool
        True if oscillation detected, False otherwise.

    Examples
    --------
    >>> policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
    >>> detect_oscillation((0.8, 0.85, 0.8, 0.85, 0.8), policy)
    True
    >>> detect_oscillation((0.8, 0.81, 0.82, 0.83, 0.84), policy)
    False
    """
    if len(values) < policy.window:
        return False
    recent = values[-policy.window :]

    def values_equal(a: float, b: float) -> bool:
        return abs(a - b) <= policy.epsilon

    val_a = recent[0]
    val_b = None
    for v in recent[1:]:
        if not values_equal(v, val_a):
            val_b = v
            break
    if val_b is None:
        return False
    expected_pattern = [val_a, val_b] * (policy.window // 2 + 1)
    expected_pattern = expected_pattern[: policy.window]
    for i, v in enumerate(recent):
        if not values_equal(v, expected_pattern[i]):
            return False
    return True


def compute_freeze_decision(
    values: tuple[float, ...], last_update_utc: int, now_utc: int, policy: OscillationPolicy,
) -> FreezeDecision:
    """Compute freeze decision based on oscillation detection.

    Parameters
    ----------
    values : tuple[float, ...]
        Recent parameter values (ordered chronologically).
    last_update_utc : int
        Unix timestamp of last update.
    now_utc : int
        Current time (injected, not wall-clock).
    policy : OscillationPolicy
        Oscillation detection policy.

    Returns
    -------
    FreezeDecision
        Decision on whether to freeze optimization.

    Examples
    --------
    >>> policy = OscillationPolicy(window=5, epsilon=0.01, freeze_seconds=3600)
    >>> values = (0.8, 0.85, 0.8, 0.85, 0.8)
    >>> decision = compute_freeze_decision(values, 1700000000, 1700003600, policy)
    >>> decision.should_freeze
    True
    >>> decision.freeze_until_utc
    1700007200
    """
    oscillation_detected = detect_oscillation(values, policy)
    if oscillation_detected:
        freeze_until_utc = now_utc + policy.freeze_seconds
        return FreezeDecision(should_freeze=True, freeze_until_utc=freeze_until_utc)
    return FreezeDecision(should_freeze=False, freeze_until_utc=None)
