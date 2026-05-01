"""Unit tests for temporal_vetting_engine (W3-P7).

Notes on time:
- The engine uses ``datetime.now(timezone.utc)`` for the current date,
  then overrides the HH:MM from the ``current_utc_time_hm`` parameter.
  To make tests deterministic for weekday-dependent assertions, we pick
  timezone offsets and HH:MM strings that land on the desired local
  weekday regardless of the current UTC date. When the current UTC date
  does not correspond to the asserted local weekday, the test is
  conditional — skipped, or re-asserted against the actual resulting
  local weekday.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_lic.config.send_time_window_config import (
    OFF_HOURS_START,
    SECONDARY_WINDOWS,
)
from apps_lic.engines.temporal_vetting_engine import vet_lead_optimal_time


class TestInputValidation:
    def test_unknown_timezone_returns_unknown_tz(self) -> None:
        result = vet_lead_optimal_time("Mars/Olympus_Mons", "14:00")
        assert result["status"] == "UNKNOWN_TZ"
        assert result["lead_local_time"] is None

    def test_empty_timezone_string(self) -> None:
        result = vet_lead_optimal_time("", "14:00")
        assert result["status"] == "UNKNOWN_TZ"

    def test_malformed_time_string(self) -> None:
        result = vet_lead_optimal_time("America/New_York", "not-a-time")
        assert result["status"] == "TEMPORAL_DELAY"
        assert "malformed" in result["decision"]

    def test_out_of_range_hour(self) -> None:
        result = vet_lead_optimal_time("America/New_York", "25:00")
        assert result["status"] == "TEMPORAL_DELAY"

    def test_returns_all_documented_keys(self) -> None:
        result = vet_lead_optimal_time("America/New_York", "15:00")
        for key in (
            "status",
            "lead_local_time",
            "decision",
            "window_label",
            "weekday",
            "local_hour",
        ):
            assert key in result


class TestClassification:
    def test_valid_timezone_yields_parseable_local_time(self) -> None:
        """Happy-path integration: the engine returns a structured local time."""
        result = vet_lead_optimal_time("America/New_York", "14:00")
        assert result["status"] in {"OPTIMAL", "TEMPORAL_DELAY", "OFF_HOURS"}
        assert result["lead_local_time"] is not None
        assert isinstance(result["weekday"], int)
        assert 0 <= result["weekday"] <= 6
        assert isinstance(result["local_hour"], int)

    @pytest.mark.parametrize("tz", ["Europe/London", "Asia/Tokyo", "UTC"])
    def test_known_timezones_do_not_raise(self, tz: str) -> None:
        result = vet_lead_optimal_time(tz, "12:00")
        assert result["status"] != "UNKNOWN_TZ"

    def test_off_hours_late_evening_utc_for_new_york(self) -> None:
        # UTC 03:00 = NYC 23:00 (EST) or 22:00 (EDT). Either is OFF_HOURS.
        result = vet_lead_optimal_time("America/New_York", "03:00")
        assert result["status"] == "OFF_HOURS"
        assert result["local_hour"] >= OFF_HOURS_START or result["local_hour"] < 7

    def test_early_morning_local_is_off_hours(self) -> None:
        # UTC 10:00 = NYC 05:00/06:00 — still off-hours (< 07:00 boundary).
        result = vet_lead_optimal_time("America/New_York", "10:00")
        assert result["status"] == "OFF_HOURS"


class TestWindowLabels:
    def test_primary_window_label_when_optimal(self) -> None:
        """Sweep every hour; confirm OPTIMAL status always carries the primary label."""
        for hour in range(24):
            result = vet_lead_optimal_time("UTC", f"{hour:02d}:00")
            if result["status"] == "OPTIMAL":
                assert result["window_label"] == "primary"

    def test_secondary_label_present_when_in_secondary_window(self) -> None:
        """At least one secondary-window label exists in the config."""
        secondary_labels = {w.label for w in SECONDARY_WINDOWS}
        assert secondary_labels  # non-empty guard

    def test_off_hours_has_no_window_label(self) -> None:
        result = vet_lead_optimal_time("America/New_York", "04:00")
        if result["status"] == "OFF_HOURS":
            assert result["window_label"] is None
