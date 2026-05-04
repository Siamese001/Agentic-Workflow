"""apps_lic.engines.multi_touch_sequencer — D6-P3.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P3

Determines the appropriate touch number and sequencing strategy given prior
outreach history. Returns an immutable TouchSequenceDecision.

Decision-only invariants
------------------------
- No durable state reads. Prior outreach history MUST be passed in via the
  ``outreach_history`` parameter — this engine does not read any database.
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config-gated: disabled when MULTI_TOUCH_ENABLED env var is absent/falsy.

Touch sequence model
--------------------
  touch_1  — initial cold outreach
  touch_2  — short follow-up referencing the prior touch
  touch_3  — value-add follow-up with new angle (avoids repetition)
  touch_4  — last attempt with explicit close or explicit opt-out offer
  exhausted — max touches reached; no further touches recommended

The engine also selects a sequencing_strategy:
  fresh_angle  — introduce new evidence or angle (touch 3+)
  nudge        — brief, direct follow-up (touch 2)
  close_or_optout — explicit call to close or give opt-out path (touch 4)
  initial      — first touch (touch 1)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from apps_shared.contracts.outreach_history_contract import (
    OutreachTouchRecord as _ContractOutreachTouchRecord,
)

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "multi_touch_policy.yaml"

_DEFAULT_MAX_TOUCHES = 4


@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config.
        return {}


OutreachTouchRecord = _ContractOutreachTouchRecord
"""Canonical outreach touch record — re-exported from apps_shared.contracts."""


@dataclass(frozen=True)
class TouchSequenceDecision:
    """Result of touch sequencing.

    Fields
    ------
    next_touch_number    : 1-based next touch index. 0 = exhausted.
    sequencing_strategy  : how to approach the next touch.
    max_touches          : configured ceiling.
    prior_touch_count    : number of touches in outreach_history.
    enabled              : False when feature is disabled.
    source               : "config" | "default" | "disabled".
    """

    next_touch_number: int
    sequencing_strategy: str
    max_touches: int
    prior_touch_count: int
    enabled: bool
    source: str


class MultiTouchSequencer:
    """Determines next touch number and strategy from outreach history."""

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def _max_touches(self, recipient_class: str) -> int:
        rc = recipient_class.upper()
        is_exec = rc in {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"}
        key = "exec" if is_exec else "default"
        return int(
            self._config.get("max_touches", {}).get(key, _DEFAULT_MAX_TOUCHES)
        )

    def sequence(
        self,
        *,
        recipient_class: str = "default",
        outreach_history: list[OutreachTouchRecord] | None = None,
    ) -> TouchSequenceDecision:
        """Determine next touch.

        Parameters
        ----------
        recipient_class   : recipient class string.
        outreach_history  : list of prior touch records — caller provides,
                            engine does NOT read from any store.
        """
        if not os.environ.get("MULTI_TOUCH_ENABLED"):
            return TouchSequenceDecision(
                next_touch_number=1,
                sequencing_strategy="initial",
                max_touches=_DEFAULT_MAX_TOUCHES,
                prior_touch_count=0,
                enabled=False,
                source="disabled",
            )

        history = outreach_history or []
        prior_count = len(history)
        max_t = self._max_touches(recipient_class)

        if prior_count >= max_t:
            return TouchSequenceDecision(
                next_touch_number=0,
                sequencing_strategy="exhausted",
                max_touches=max_t,
                prior_touch_count=prior_count,
                enabled=True,
                source=("config" if self._config else "default"),
            )

        next_num = prior_count + 1

        if next_num == 1:
            strategy = "initial"
        elif next_num == 2:
            strategy = "nudge"
        elif next_num >= max_t:
            strategy = "close_or_optout"
        else:
            strategy = "fresh_angle"

        return TouchSequenceDecision(
            next_touch_number=next_num,
            sequencing_strategy=strategy,
            max_touches=max_t,
            prior_touch_count=prior_count,
            enabled=True,
            source=("config" if self._config else "default"),
        )


__all__ = ["MultiTouchSequencer", "TouchSequenceDecision", "OutreachTouchRecord"]
