"""apps_lic.engines.resurfacing_detector — D6-P4.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P4

Detects whether a recipient is a re-engagement candidate based on signals
passed in by the caller. Returns an immutable ResurfacingDecision.

Decision-only invariants
------------------------
- No durable state reads. All signals MUST be passed in — engine does not
  read any database or history store.
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config-gated: disabled when RESURFACING_ENABLED env var is absent/falsy.

Re-engagement signals
---------------------
  days_since_last_contact : float — days since most recent touch.
  prior_response_received : bool  — did recipient respond (even no-reply)?
  relationship_distance   : str   — "cold"|"warm"|"referral"|"known"
  trigger_event_detected  : bool  — external event (job change, funding, post)
                                     detected by caller — high-value re-engage.

Signal integration model
------------------------
  cold + no response + no trigger → NOT resurfacing (wait or give up)
  cold + trigger                  → RECOMMENDED resurfacing
  warm + no response + >30 days   → CONDITIONAL resurfacing
  warm + trigger                  → RECOMMENDED resurfacing
  known + any                     → RECOMMENDED resurfacing (relationship protects)
  days_since_last_contact < cool_off_days → BLOCKED (too soon)

Output recommendation values: "recommended" | "conditional" | "not_recommended" | "blocked"
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "resurfacing_policy.yaml"

_WARM_DISTANCES = frozenset({"warm", "follow_up", "referral", "warm_referral", "known", "prior_contact"})
_DEFAULT_COOL_OFF_DAYS = 14
_DEFAULT_WARM_RESUFACE_DAYS = 30


@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config.
        return {}


@dataclass(frozen=True)
class ResurfacingDecision:
    """Result of re-engagement detection.

    Fields
    ------
    recommendation   : "recommended" | "conditional" | "not_recommended" | "blocked" | "disabled"
    reason           : human-readable string explaining the decision.
    enabled          : False when feature is disabled.
    trigger_detected : True if a trigger event drove the recommendation.
    """

    recommendation: str
    reason: str
    enabled: bool
    trigger_detected: bool


class ResurfacingDetector:
    """Detects re-engagement candidacy from caller-provided signals."""

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def _cool_off_days(self) -> float:
        return float(self._config.get("cool_off_days", _DEFAULT_COOL_OFF_DAYS))

    def _warm_resurface_days(self) -> float:
        return float(self._config.get("warm_resurface_days", _DEFAULT_WARM_RESUFACE_DAYS))

    def detect(
        self,
        *,
        days_since_last_contact: Optional[float] = None,
        prior_response_received: bool = False,
        relationship_distance: str = "cold",
        trigger_event_detected: bool = False,
    ) -> ResurfacingDecision:
        """Evaluate re-engagement candidacy.

        Parameters
        ----------
        days_since_last_contact : days since last touch (None = unknown).
        prior_response_received : True if recipient replied at some point.
        relationship_distance   : canonical distance string.
        trigger_event_detected  : True when caller detected an external trigger.
        """
        if not os.environ.get("RESURFACING_ENABLED"):
            return ResurfacingDecision(
                recommendation="disabled",
                reason="RESURFACING_ENABLED not set",
                enabled=False,
                trigger_detected=trigger_event_detected,
            )

        rd = relationship_distance.lower()
        is_warm = rd in _WARM_DISTANCES
        cool_off = self._cool_off_days()
        warm_threshold = self._warm_resurface_days()

        # Blocked: too soon since last contact
        if days_since_last_contact is not None and days_since_last_contact < cool_off:
            return ResurfacingDecision(
                recommendation="blocked",
                reason=(
                    f"days_since_last_contact={days_since_last_contact:.1f} < "
                    f"cool_off={cool_off:.0f} days"
                ),
                enabled=True,
                trigger_detected=trigger_event_detected,
            )

        # Trigger event always recommends (unless blocked above)
        if trigger_event_detected:
            return ResurfacingDecision(
                recommendation="recommended",
                reason="trigger_event_detected — high-value re-engagement opportunity",
                enabled=True,
                trigger_detected=True,
            )

        # Known/warm with prior response → recommended
        if is_warm and prior_response_received:
            return ResurfacingDecision(
                recommendation="recommended",
                reason=f"warm relationship ({rd}) with prior response",
                enabled=True,
                trigger_detected=False,
            )

        # Warm, enough time elapsed, no response
        if is_warm and (days_since_last_contact is None or days_since_last_contact >= warm_threshold):
            return ResurfacingDecision(
                recommendation="conditional",
                reason=(
                    f"warm relationship ({rd}), "
                    f"days_since_last_contact={days_since_last_contact}, "
                    f"no prior response — conditional re-engage"
                ),
                enabled=True,
                trigger_detected=False,
            )

        # Cold + no trigger + no response → not recommended
        return ResurfacingDecision(
            recommendation="not_recommended",
            reason=(
                f"cold relationship ({rd}), no trigger, "
                f"no prior response — do not resurface"
            ),
            enabled=True,
            trigger_detected=False,
        )


__all__ = ["ResurfacingDetector", "ResurfacingDecision"]
