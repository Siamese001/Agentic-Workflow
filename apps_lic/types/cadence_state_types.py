"""Cadence state types for the 3-touch follow-up sequence engine.

W3-P9 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Industry benchmark: a 3-touch outreach sequence (initial + 2 follow-ups)
delivers ~3x the cumulative reply rate of single-touch outreach. Each
touch uses a distinct message template (initial / followup / final)
and fires at a calibrated interval:

    Day 0   — INITIAL        (baseline message)
    Day 5   — FOLLOWUP_1     (soft nudge)
    Day 12  — FOLLOWUP_2     (final touch, no further outreach)

Any reply received at any point terminates the sequence immediately.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Final, Optional


class CadenceState(str, Enum):
    """State machine for a single recipient's outreach cadence."""

    INITIAL = "INITIAL"
    FOLLOWUP_1 = "FOLLOWUP_1"
    FOLLOWUP_2 = "FOLLOWUP_2"
    TERMINATED = "TERMINATED"


class CadenceAction(str, Enum):
    """The action the engine prescribes for the current call."""

    SEND = "SEND"
    WAIT = "WAIT"
    NO_ACTION = "NO_ACTION"


# Interval from INITIAL to FOLLOWUP_1 in days.
DAYS_TO_FOLLOWUP_1: Final[int] = 5

# Interval from FOLLOWUP_1 to FOLLOWUP_2 in days.
DAYS_TO_FOLLOWUP_2: Final[int] = 7

# Total sequence length in days (Day 0 + Day 5 + Day 12 = 12 days).
TOTAL_SEQUENCE_DAYS: Final[int] = DAYS_TO_FOLLOWUP_1 + DAYS_TO_FOLLOWUP_2


@dataclass
class CadenceStateRecord:
    """Mutable state for a single recipient's cadence.

    Intended to be persisted per-campaign / per-recipient. The engine
    updates these fields on every ``advance`` call. All datetimes are
    UTC-naive or UTC-aware ``datetime`` objects — the engine does not
    perform timezone conversion here (that's the temporal vetting
    engine's job, W3-P7).

    Attributes:
        campaign_id: Stable identifier for the parent campaign.
        recipient_id: Stable identifier for the recipient.
        current_state: Current cadence state.
        next_action_at_utc: Earliest UTC datetime at which the next
            SEND action should fire. When ``current_state`` is
            TERMINATED this is ignored.
        last_sent_at_utc: When the most recent send occurred, or None
            if no send yet.
        initial_scheduled_at_utc: The original day-0 scheduled time.
            Persists across state transitions for audit.
        replied: True once a reply is observed. Forces transition to
            TERMINATED on the next ``advance`` call.
        send_count: Count of SEND actions emitted by the engine.
        terminated_reason: Set when ``current_state`` becomes TERMINATED.
            One of ``{"replied", "sequence_complete", "operator_stop"}``
            or ``None``.
    """

    campaign_id: str
    recipient_id: str
    current_state: CadenceState = CadenceState.INITIAL
    next_action_at_utc: Optional[datetime] = None
    last_sent_at_utc: Optional[datetime] = None
    initial_scheduled_at_utc: Optional[datetime] = None
    replied: bool = False
    send_count: int = 0
    terminated_reason: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CadenceDecision:
    """One decision returned by the engine's ``advance`` call."""

    action: CadenceAction
    next_state: CadenceState
    message_template: Optional[str]  # "initial" / "followup_1" / "followup_2" / None
    next_check_at_utc: Optional[datetime]
    reason: str


__all__ = [
    "CadenceAction",
    "CadenceDecision",
    "CadenceState",
    "CadenceStateRecord",
    "DAYS_TO_FOLLOWUP_1",
    "DAYS_TO_FOLLOWUP_2",
    "TOTAL_SEQUENCE_DAYS",
]
