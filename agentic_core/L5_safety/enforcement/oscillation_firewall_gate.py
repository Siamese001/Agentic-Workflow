"""OscillationFirewall — L5 Safety enforcement.

Wraps the existing OscillationDetector with routing-tier-specific threshold
validation.  Prevents the routing pipeline from oscillating between tiers
(e.g. DETERMINISTIC -> QWEN -> DETERMINISTIC is an oscillation; it must be
frozen before it destabilises downstream agents).

Contract:
- record_tier_decision(tier, cycle) records the tier chosen at each cycle.
- assert_no_oscillation(tier, cycle) raises OscillationFirewallTripped if
  the tier change would complete an oscillation pattern.
- get_frozen_tiers(cycle) returns set of tiers currently frozen.

Threshold defaults (conservative, override via OscillationFirewallConfig):
  cooldown_window = 6   (check last 6 decisions)
  freeze_cycles   = 10  (frozen for 10 cycles on detection)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class OscillationFirewallTripped(RuntimeError):
    """Raised when routing-tier oscillation is detected and firewall fires."""


@dataclass(frozen=True)
class OscillationFirewallConfig:
    """Configuration for the oscillation firewall.

    Fields:
        cooldown_window: Number of recent tier decisions to inspect.
        freeze_cycles:   Number of cycles a tier is frozen after oscillation.
    """

    cooldown_window: int = 6
    freeze_cycles: int = 10

    def __post_init__(self) -> None:
        if self.cooldown_window < 2:
            raise ValueError("cooldown_window must be >= 2")
        if self.freeze_cycles < 1:
            raise ValueError("freeze_cycles must be >= 1")


class OscillationFirewall:
    """Routing-tier oscillation firewall.

    Wraps system_learning.enforcement.oscillation_detector.OscillationDetector
    with routing-tier semantics.  Each tier is tracked independently; an
    oscillation in *any* tier triggers a freeze for that tier.

    Args:
        config: OscillationFirewallConfig (defaults are conservative).
    """

    def __init__(self, config: OscillationFirewallConfig | None = None) -> None:
        from system_learning.enforcement.oscillation_detector import OscillationDetector

        cfg = config or OscillationFirewallConfig()
        self._config = cfg
        self._detector = OscillationDetector(
            cooldown_window=cfg.cooldown_window, freeze_cycles=cfg.freeze_cycles
        )
        self._tier_histories: dict[str, list[Any]] = {}

    def record_tier_decision(self, tier: str, cycle: int) -> None:
        """Record that *tier* was chosen at *cycle*.

        This is the non-raising variant — use for observation only.
        """
        if tier not in self._tier_histories:
            self._tier_histories[tier] = []
        self._tier_histories[tier].append(cycle)

    _ROUTING_PARAM = "routing_tier"

    def assert_no_oscillation(self, tier: str, cycle: int) -> None:
        """Assert that accepting *tier* at *cycle* does not complete oscillation.

        Tracks a single "routing_tier" parameter whose value is the tier name.
        DETERMINISTIC->QWEN->DETERMINISTIC is two value-flips = oscillation.

        Raises:
            OscillationFirewallTripped: if oscillation pattern is detected.
        """
        from system_learning.enforcement.oscillation_detector import ParameterFrozenError

        try:
            self._detector.record_change(self._ROUTING_PARAM, tier, cycle)
        except ParameterFrozenError as exc:
            raise OscillationFirewallTripped(
                f"OscillationFirewall: tier {tier!r} is oscillating at cycle {cycle}. Routing frozen.\nDetector: {exc}"
            ) from exc
        self.record_tier_decision(tier, cycle)

    def is_tier_frozen(self, tier: str, cycle: int) -> bool:
        """Return True if routing_tier parameter is frozen at *cycle*."""
        return self._detector.is_frozen(self._ROUTING_PARAM, cycle)

    def get_frozen_tiers(self, cycle: int) -> set[str]:
        """Return set of tier names currently frozen at *cycle*."""
        return {tier for tier in self._tier_histories if self._detector.is_frozen(tier, cycle)}

    def reset_for_testing(self) -> None:
        """Clear all state for test isolation."""
        self._detector.reset_for_testing()
        self._tier_histories.clear()


def validate_threshold(
    tier_sequence: tuple[str, ...], config: OscillationFirewallConfig | None = None
) -> bool:
    """Return True if *tier_sequence* does NOT contain an oscillation pattern.

    Stateless alternative to OscillationFirewall.  Used in invariant tests
    to assert that a recorded sequence is stable.

    An oscillation is defined as: the same tier appearing at least twice
    with a different tier interspersed, within the cooldown_window.
    """
    cfg = config or OscillationFirewallConfig()
    if len(tier_sequence) < cfg.cooldown_window:
        return True
    window = tier_sequence[-cfg.cooldown_window :]
    for i in range(len(window) - 2):
        if window[i] == window[i + 2] and window[i] != window[i + 1]:
            return False
    return True


__all__ = [
    "OscillationFirewall",
    "OscillationFirewallConfig",
    "OscillationFirewallTripped",
    "validate_threshold",
]
