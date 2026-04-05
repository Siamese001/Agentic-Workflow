"""G-16-17: Dampening policies for System Learning optimization cycles.

Implements:
  - Cooldown policy (minimum time between updates)
  - Sample size policy (minimum observations before retraining)

All policies are frozen dataclasses. All validation functions are pure and
deterministic (no wall-clock reads).
"""

from __future__ import annotations

from dataclasses import dataclass


class DampeningViolation(Exception):
    """Base exception for dampening policy violations."""


class CooldownViolation(DampeningViolation):
    """Raised when cooldown period has not elapsed."""


class SampleSizeViolation(DampeningViolation):
    """Raised when sample size is below minimum."""


@dataclass(frozen=True, slots=True)
class CooldownPolicy:
    """Cooldown policy for optimization cycles.

    Fields
    ------
    min_seconds_between_updates : int
        Minimum seconds that must elapse between updates to the same surface.
    """

    min_seconds_between_updates: int


@dataclass(frozen=True, slots=True)
class SampleSizePolicy:
    """Sample size policy for optimization cycles.

    Fields
    ------
    min_observations : int
        Minimum number of observations required before retraining.
    """

    min_observations: int


def assert_cooldown_ok(last_update_utc: int, now_utc: int, cooldown_policy: CooldownPolicy) -> None:
    """Assert that cooldown period has elapsed.

    Parameters
    ----------
    last_update_utc : int
        Unix timestamp of the last update (must be injected, not wall-clock).
    now_utc : int
        Unix timestamp of the current time (must be injected, not wall-clock).
    cooldown_policy : CooldownPolicy
        The cooldown policy to enforce.

    Raises
    ------
    CooldownViolation
        If cooldown period has not elapsed.
    """
    elapsed_seconds = now_utc - last_update_utc
    if elapsed_seconds < cooldown_policy.min_seconds_between_updates:
        remaining = cooldown_policy.min_seconds_between_updates - elapsed_seconds
        raise CooldownViolation(
            f"COOLDOWN_VIOLATION: {remaining} seconds remaining (min={cooldown_policy.min_seconds_between_updates}, elapsed={elapsed_seconds})"
        )


def assert_min_sample_size(n_observations: int, sample_policy: SampleSizePolicy) -> None:
    """Assert that minimum sample size is met.

    Parameters
    ----------
    n_observations : int
        Number of observations available.
    sample_policy : SampleSizePolicy
        The sample size policy to enforce.

    Raises
    ------
    SampleSizeViolation
        If n_observations < min_observations.
    """
    if n_observations < sample_policy.min_observations:
        shortfall = sample_policy.min_observations - n_observations
        raise SampleSizeViolation(
            f"SAMPLE_SIZE_VIOLATION: {shortfall} observations short (min={sample_policy.min_observations}, actual={n_observations})"
        )
