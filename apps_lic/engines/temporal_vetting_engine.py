"""Temporal vetting engine for governed outreach.

W3-P7 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle D).

Replaces the placeholder ``vet_lead_optimal_time`` in
``apps_lic/outreach_engine/governed_outreach.py`` (added 2026-05-01
during the HOP1-9 restore) with a real, deterministic implementation.

Contract (unchanged from the placeholder for backward compatibility):

    vet_lead_optimal_time(
        lead_timezone: str,
        current_utc_time_hm: str,
        tools: dict,
        logger: Any | None,
    ) -> dict

    returns {
        "status": "OPTIMAL" | "TEMPORAL_DELAY" | "OFF_HOURS" | "UNKNOWN_TZ",
        "lead_local_time": str | None,     # "YYYY-MM-DD HH:MM WEEKDAY"
        "decision": str,                    # human-readable rationale
        "window_label": str | None,         # e.g. "primary" / "secondary_..."
        "weekday": int | None,              # Monday=0 .. Sunday=6
        "local_hour": int | None,
    }

Status semantics (tightened from the placeholder):

    OPTIMAL         — time falls in the PRIMARY window (Tue/Wed 10-12 local).
                      Caller should send.
    TEMPORAL_DELAY  — time is business-hours-ish but not primary.
                      Caller should defer to the next primary window.
    OFF_HOURS       — evenings, nights, or weekends. Hard reject.
    UNKNOWN_TZ      — lead_timezone is not a valid IANA zone name.
                      Caller should flag for operator review.

Dependencies:
    - ``zoneinfo`` (stdlib, Python 3.9+) — no third-party timezone lib.
    - ``apps_lic.config.send_time_window_config`` for the window table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover -- Python < 3.9 fallback never exercised on CI
    ZoneInfo = None  # type: ignore[assignment]
    ZoneInfoNotFoundError = Exception  # type: ignore[assignment,misc]

from apps_lic.config.send_time_window_config import (
    PRIMARY_WINDOW,
    is_off_hours,
    matching_window,
)

_WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def vet_lead_optimal_time(
    lead_timezone: str,
    current_utc_time_hm: str,
    tools: Optional[Dict[str, Any]] = None,
    logger: Optional[Any] = None,
) -> Dict[str, Any]:
    """Decide whether to send now based on recipient-local time.

    Args:
        lead_timezone: IANA timezone name of the recipient
            (e.g., ``"America/New_York"``, ``"Europe/London"``).
        current_utc_time_hm: Current time in UTC, formatted ``"HH:MM"``.
            The current-day date is taken from ``datetime.now(timezone.utc)``
            so callers do not need to pass a full ISO timestamp — the
            placeholder signature required only ``HH:MM``.
        tools: Reserved for future use (currently unused, kept for
            backward-compat with the placeholder signature).
        logger: Optional logger with ``.info / .warning / .error``. When
            None, no log emits occur. Never raises on logger failure.

    Returns:
        Status dict described in module docstring. Never raises —
        malformed input yields ``UNKNOWN_TZ`` or ``TEMPORAL_DELAY``
        with a diagnostic ``decision`` field.
    """
    # 1. Resolve timezone.
    if ZoneInfo is None:
        return _build_unknown_tz(
            lead_timezone,
            "zoneinfo module unavailable (Python < 3.9)",
            logger,
        )
    try:
        tz = ZoneInfo(lead_timezone)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return _build_unknown_tz(lead_timezone, "invalid IANA zone name", logger)
    except Exception as exc:  # guardian: allow-log-and-swallow -- any zoneinfo failure degrades to UNKNOWN_TZ
        return _build_unknown_tz(lead_timezone, f"zoneinfo error: {exc}", logger)

    # 2. Parse UTC HH:MM onto today's UTC date.
    try:
        hh, mm = current_utc_time_hm.split(":")
        hour = int(hh)
        minute = int(mm)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("hour/minute out of range")
    except (ValueError, AttributeError):
        return {
            "status": "TEMPORAL_DELAY",
            "lead_local_time": None,
            "decision": f"malformed current_utc_time_hm={current_utc_time_hm!r}",
            "window_label": None,
            "weekday": None,
            "local_hour": None,
        }

    today_utc = datetime.now(timezone.utc).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )

    # 3. Convert to recipient-local.
    local = today_utc.astimezone(tz)
    weekday = local.weekday()
    local_hour = local.hour
    local_str = local.strftime("%Y-%m-%d %H:%M ") + _WEEKDAY_NAMES[weekday]

    # 4. Classify.
    if is_off_hours(weekday, local_hour):
        return {
            "status": "OFF_HOURS",
            "lead_local_time": local_str,
            "decision": "recipient local time is outside business hours",
            "window_label": None,
            "weekday": weekday,
            "local_hour": local_hour,
        }

    window = matching_window(weekday, local_hour)
    if window is None:
        return {
            "status": "TEMPORAL_DELAY",
            "lead_local_time": local_str,
            "decision": (
                "recipient local time is in business hours but outside the "
                "allowed send windows"
            ),
            "window_label": None,
            "weekday": weekday,
            "local_hour": local_hour,
        }

    if window.priority == PRIMARY_WINDOW.priority:
        return {
            "status": "OPTIMAL",
            "lead_local_time": local_str,
            "decision": (
                f"recipient local time falls in the primary window "
                f"({window.label}, {window.hour_start:02d}-{window.hour_end:02d})"
            ),
            "window_label": window.label,
            "weekday": weekday,
            "local_hour": local_hour,
        }

    # Secondary / tertiary windows — still delay to primary for the uplift.
    return {
        "status": "TEMPORAL_DELAY",
        "lead_local_time": local_str,
        "decision": (
            f"recipient local time is in a secondary window "
            f"({window.label}); delay to primary for full uplift"
        ),
        "window_label": window.label,
        "weekday": weekday,
        "local_hour": local_hour,
    }


def _build_unknown_tz(
    lead_timezone: str,
    reason: str,
    logger: Optional[Any],
) -> Dict[str, Any]:
    """Return an UNKNOWN_TZ status dict and log a warning."""
    if logger is not None:
        try:
            logger.warning(
                "temporal_vetting UNKNOWN_TZ: zone=%r reason=%s",
                lead_timezone,
                reason,
            )
        except (AttributeError, TypeError):  # guardian: allow-log-and-swallow -- logger must not break vetting
            pass
    return {
        "status": "UNKNOWN_TZ",
        "lead_local_time": None,
        "decision": reason,
        "window_label": None,
        "weekday": None,
        "local_hour": None,
    }


__all__ = [
    "vet_lead_optimal_time",
]
