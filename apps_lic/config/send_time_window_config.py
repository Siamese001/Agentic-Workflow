"""Send-time-window configuration for temporal vetting.

W3-P7 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle D).

Industry benchmark: LinkedIn outreach sent during the recipient-local
Tue-Wed 10am-12pm window converts at ~1.5x the reply rate of unconstrained
send time. Secondary windows (Mon/Thu mornings, Tue-Thu afternoons) are
acceptable fallbacks when the primary window is blocked (holiday, very
recent outreach, etc.).

Window definitions are weekday-aware and hour-inclusive / hour-exclusive:
    hour_start <= local_hour < hour_end

Weekdays use Python ``datetime.weekday()`` convention: Monday=0 ... Sunday=6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Tuple


@dataclass(frozen=True)
class SendTimeWindow:
    """One allowed send-time window in recipient-local time.

    Attributes:
        label: Human-readable identifier for reporting / telemetry.
            Values currently in use: "primary", "secondary", "tertiary".
        weekdays: Tuple of weekday integers (Monday=0 ... Sunday=6).
            A local time matches the window if and only if its weekday
            is in this tuple AND its hour is in the half-open interval
            [hour_start, hour_end).
        hour_start: Inclusive hour (0-23).
        hour_end: Exclusive hour (0-23 or 24).
        priority: Smaller = higher priority. Primary=0, secondary=1,
            tertiary=2. Callers use the lowest-priority matching window.
    """

    label: str
    weekdays: Tuple[int, ...]
    hour_start: int
    hour_end: int
    priority: int


# Primary window: recipient-local Tue / Wed, 10am to noon.
# This is the single window that drives the 1.5x uplift claim — the
# A/B report (Bundle D) will measure uplift of sends inside this
# window vs sends outside it.
PRIMARY_WINDOW: Final[SendTimeWindow] = SendTimeWindow(
    label="primary",
    weekdays=(1, 2),  # Tuesday, Wednesday
    hour_start=10,
    hour_end=12,
    priority=0,
)

# Secondary windows — still business hours, still reply-rate-positive,
# but softer signal than the primary.
SECONDARY_WINDOWS: Final[Tuple[SendTimeWindow, ...]] = (
    SendTimeWindow(
        label="secondary_mon_thu_morning",
        weekdays=(0, 3),  # Monday, Thursday
        hour_start=10,
        hour_end=12,
        priority=1,
    ),
    SendTimeWindow(
        label="secondary_tue_thu_afternoon",
        weekdays=(1, 2, 3),  # Tuesday, Wednesday, Thursday
        hour_start=14,
        hour_end=16,
        priority=1,
    ),
)

# Every allowed window, sorted by priority (primary first). Callers that
# only want "is this time allowed at all" should scan this tuple.
ALL_ALLOWED_WINDOWS: Final[Tuple[SendTimeWindow, ...]] = (
    PRIMARY_WINDOW,
    *SECONDARY_WINDOWS,
)

# Off-hours boundary — times outside business hours are always rejected,
# even if their weekday/hour happens to match no allowed window. This is
# a belt-and-braces guard against misconfiguration.
OFF_HOURS_START: Final[int] = 18  # 6pm local
OFF_HOURS_END: Final[int] = 7  # 7am local
WEEKEND_WEEKDAYS: Final[Tuple[int, int]] = (5, 6)  # Saturday, Sunday


def is_off_hours(weekday: int, hour: int) -> bool:
    """Return True when local weekday+hour is firmly off-hours."""
    if weekday in WEEKEND_WEEKDAYS:
        return True
    if hour < OFF_HOURS_END or hour >= OFF_HOURS_START:
        return True
    return False


def matching_window(weekday: int, hour: int) -> SendTimeWindow | None:
    """Return the highest-priority window matching (weekday, hour), or None."""
    for window in ALL_ALLOWED_WINDOWS:
        if weekday in window.weekdays and window.hour_start <= hour < window.hour_end:
            return window
    return None


__all__ = [
    "ALL_ALLOWED_WINDOWS",
    "OFF_HOURS_END",
    "OFF_HOURS_START",
    "PRIMARY_WINDOW",
    "SECONDARY_WINDOWS",
    "SendTimeWindow",
    "WEEKEND_WEEKDAYS",
    "is_off_hours",
    "matching_window",
]
