"""Tests for archive_old_adg.py — timestamp parsing, sorting, and retention logic.

Covers:
- Timestamp extraction from filenames (MMDDYYYY, YYYYMMDD, YYYYMMDDTHHMMSSz)
- Timestamp parsing with format detection
- Datetime-based sorting (not lexicographic)
- Retention policy (keep N newest runs)
- Archive month directory calculation
- Repair file pattern (adg_repair_*.json)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the functions we're testing
sys.path.insert(0, str(ROOT / "tools"))
from archive_old_adg import (
    _extract_timestamp,
    _get_archive_month_dir,
    _parse_timestamp,
    identify_runs_to_archive,
)


class TestTimestampExtraction:
    """Test _extract_timestamp: filename → timestamp string."""

    def test_new_format_mmddyyyy(self):
        """New format: adg_indexed_03122026.sqlite → 03122026"""
        assert _extract_timestamp("adg_indexed_03122026.sqlite") == "03122026"
        assert _extract_timestamp("adg_snapshot_12252026.json") == "12252026"

    def test_legacy_yyyymmdd_8digit(self):
        """Legacy 8-digit: adg_canonical_ownership_20260310.json → 20260310"""
        assert _extract_timestamp("adg_canonical_ownership_20260310.json") == "20260310"

    def test_legacy_iso_format(self):
        """Legacy ISO: adg_full_20260312T104141Z.json → 20260312T104141Z"""
        assert _extract_timestamp("adg_full_20260312T104141Z.json") == "20260312T104141Z"
        assert _extract_timestamp("adg_indexed_20260311T230549Z.sqlite") == "20260311T230549Z"

    def test_repair_file_format(self):
        """Repair files: adg_repair_03312026_0951.json → 03312026"""
        assert _extract_timestamp("adg_repair_03312026_0951.json") == "03312026"
        assert _extract_timestamp("adg_repair_04012026_2215.json") == "04012026"

    def test_no_timestamp_returns_none(self):
        """Files without valid timestamps return None."""
        assert _extract_timestamp("README.md") is None
        assert _extract_timestamp("adg_summary.md") is None
        assert _extract_timestamp("scan_result_cache.json") is None

    def test_malformed_timestamp_returns_none(self):
        """Malformed timestamps return None."""
        assert _extract_timestamp("adg_indexed_123.json") is None
        assert _extract_timestamp("adg_indexed_abcd1234.json") is None


class TestTimestampParsing:
    """Test _parse_timestamp: timestamp string → datetime object."""

    def test_new_format_mmddyyyy(self):
        """MMDDYYYY: 03122026 → March 12, 2026"""
        dt = _parse_timestamp("03122026")
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 12
        assert dt.hour == 0
        assert dt.minute == 0

    def test_repair_file_parsing(self):
        """Repair file timestamps parse correctly."""
        dt = _parse_timestamp("03312026")
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 31

        dt2 = _parse_timestamp("04012026")
        assert dt2.year == 2026
        assert dt2.month == 4
        assert dt2.day == 1

    def test_legacy_yyyymmdd_8digit(self):
        """YYYYMMDD: 20260310 → March 10, 2026"""
        dt = _parse_timestamp("20260310")
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 10
        assert dt.hour == 0
        assert dt.minute == 0

    def test_legacy_iso_format(self):
        """YYYYMMDDTHHMMSSz: 20260312T104141Z → March 12, 2026 10:41:41"""
        dt = _parse_timestamp("20260312T104141Z")
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 12
        assert dt.hour == 10
        assert dt.minute == 41
        assert dt.second == 41

    def test_distinguishes_mmddyyyy_from_yyyymmdd(self):
        """8-digit formats must be correctly distinguished."""
        # 03122026 = March 12, 2026 (MMDDYYYY)
        dt1 = _parse_timestamp("03122026")
        assert dt1.month == 3 and dt1.day == 12

        # 20260312 = March 12, 2026 (YYYYMMDD)
        dt2 = _parse_timestamp("20260312")
        assert dt2.month == 3 and dt2.day == 12

        # Both should be the same date
        assert dt1.date() == dt2.date()

    def test_year_prefix_detection(self):
        """Timestamps starting with 202x-206x are treated as YYYYMMDD."""
        # All these should parse as YYYYMMDD (year first)
        for ts in ["20260101", "20300101", "20400101", "20500101", "20600101"]:
            dt = _parse_timestamp(ts)
            assert dt.year >= 2026
            assert dt.month == 1
            assert dt.day == 1


class TestDatetimeBasedSorting:
    """Test that sorting uses actual datetime, not lexicographic string comparison."""

    def test_mixed_formats_sort_by_datetime(self):
        """Mixed timestamp formats must sort by actual datetime, not string."""
        timestamps = [
            "20260311T230549Z",  # Mar 11, 2026 23:05:49
            "03122026",          # Mar 12, 2026 00:00:00
            "20260312T093508Z",  # Mar 12, 2026 09:35:08
            "20260312T104141Z",  # Mar 12, 2026 10:41:41
        ]

        # Sort by datetime (newest first)
        sorted_ts = sorted(timestamps, key=_parse_timestamp, reverse=True)

        # Expected order: 10:41 > 09:35 > 00:00 > 23:05 (prev day)
        assert sorted_ts == [
            "20260312T104141Z",
            "20260312T093508Z",
            "03122026",
            "20260311T230549Z",
        ]

    def test_lexicographic_would_fail(self):
        """Demonstrate that lexicographic sorting gives wrong order."""
        timestamps = ["03122026", "20260312T104141Z"]

        # Lexicographic sort (WRONG)
        lex_sorted = sorted(timestamps)
        assert lex_sorted == ["03122026", "20260312T104141Z"]

        # Datetime sort (CORRECT)
        dt_sorted = sorted(timestamps, key=_parse_timestamp, reverse=True)
        assert dt_sorted == ["20260312T104141Z", "03122026"]

        # They should be different
        assert lex_sorted != dt_sorted


class TestRetentionPolicy:
    """Test identify_runs_to_archive: keep N newest runs."""

    def test_keep_all_when_under_limit(self):
        """If total runs ≤ keep_runs, archive nothing."""
        runs = {
            "20260312T104141Z": [],
            "03122026": [],
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=5)
        assert to_archive == []

    def test_archive_oldest_when_over_limit(self):
        """Archive oldest runs when total > keep_runs."""
        runs = {
            "20260311T230549Z": [],  # Mar 11 23:05 - oldest
            "03122026": [],          # Mar 12 00:00 - 2nd oldest
            "20260312T093508Z": [],  # Mar 12 09:35
            "20260312T101941Z": [],  # Mar 12 10:19
            "20260312T104141Z": [],  # Mar 12 10:41 - newest
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=3)

        # Should archive the 2 oldest: 20260311T230549Z and 03122026
        assert len(to_archive) == 2
        assert "20260311T230549Z" in to_archive
        assert "03122026" in to_archive

        # Should keep the 3 newest
        assert "20260312T093508Z" not in to_archive
        assert "20260312T101941Z" not in to_archive
        assert "20260312T104141Z" not in to_archive

    def test_archive_list_sorted_oldest_first(self):
        """Returned archive list must be sorted oldest first."""
        runs = {
            "20260312T104141Z": [],  # Mar 12 10:41 - newest
            "03122026": [],          # Mar 12 00:00 - 2nd oldest
            "20260311T230549Z": [],  # Mar 11 23:05 - oldest
            "20260312T093508Z": [],  # Mar 12 09:35 - 2nd newest
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=2)

        # Should archive oldest 2: 20260311T230549Z and 03122026
        # Returned in oldest-first order
        assert len(to_archive) == 2
        assert to_archive[0] == "20260311T230549Z"
        assert to_archive[1] == "03122026"

    def test_mixed_format_retention(self):
        """Retention policy must work correctly with mixed timestamp formats."""
        runs = {
            "20260310": [],           # Mar 10 (YYYYMMDD legacy)
            "20260311T230549Z": [],   # Mar 11 23:05 (ISO legacy)
            "03122026": [],           # Mar 12 00:00 (MMDDYYYY new)
            "20260312T104141Z": [],   # Mar 12 10:41 (ISO legacy)
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=2)

        # Keep the 2 newest: 20260312T104141Z and 03122026
        # Archive the 2 oldest: 20260310 and 20260311T230549Z
        assert len(to_archive) == 2
        assert "20260310" in to_archive
        assert "20260311T230549Z" in to_archive
        assert "03122026" not in to_archive
        assert "20260312T104141Z" not in to_archive

    def test_keep_runs_one(self):
        """Test keep_runs_one: only keep 1 run."""
        runs = {
            "20260312T104141Z": [],
            "03122026": [],
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=1)
        assert len(to_archive) == 1
        assert "20260312T104141Z" not in to_archive


class TestArchiveMonthDirectory:
    """Test _get_archive_month_dir: timestamp → archive directory path."""

    def test_new_format_mmddyyyy(self):
        """MMDDYYYY: 03122026 → 2026-03"""
        path = _get_archive_month_dir("03122026")
        assert path.name == "2026-03"

    def test_legacy_yyyymmdd(self):
        """YYYYMMDD: 20260310 → 2026-03"""
        path = _get_archive_month_dir("20260310")
        assert path.name == "2026-03"

    def test_legacy_iso_format(self):
        """ISO: 20260312T104141Z → 2026-03"""
        path = _get_archive_month_dir("20260312T104141Z")
        assert path.name == "2026-03"

    def test_different_months(self):
        """Different months produce different archive directories."""
        jan = _get_archive_month_dir("01152026")
        feb = _get_archive_month_dir("02152026")
        mar = _get_archive_month_dir("03152026")

        assert jan.name == "2026-01"
        assert feb.name == "2026-02"
        assert mar.name == "2026-03"

    def test_different_years(self):
        """Different years produce different archive directories."""
        y2026 = _get_archive_month_dir("03152026")
        y2027 = _get_archive_month_dir("03152027")

        assert y2026.name == "2026-03"
        assert y2027.name == "2027-03"


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_same_day_different_times_sorted_correctly(self):
        """Multiple runs on same day must sort by time."""
        timestamps = [
            "20260312T104141Z",  # 10:41
            "20260312T093508Z",  # 09:35
            "03122026",          # 00:00
        ]
        sorted_ts = sorted(timestamps, key=_parse_timestamp, reverse=True)

        assert sorted_ts == [
            "20260312T104141Z",
            "20260312T093508Z",
            "03122026",
        ]

    def test_midnight_vs_specific_time(self):
        """MMDDYYYY (midnight) vs ISO (specific time) comparison."""
        midnight = _parse_timestamp("03122026")
        morning = _parse_timestamp("20260312T093508Z")

        assert morning > midnight

    def test_year_boundary(self):
        """Timestamps across year boundaries sort correctly."""
        timestamps = [
            "12312025",          # Dec 31, 2025
            "01012026",          # Jan 1, 2026
        ]
        sorted_ts = sorted(timestamps, key=_parse_timestamp, reverse=True)

        assert sorted_ts == ["01012026", "12312025"]

    def test_empty_runs_dict(self):
        """Empty runs dict returns empty archive list."""
        to_archive = identify_runs_to_archive({}, keep_runs=5)
        assert to_archive == []

    def test_scenario_after_new_generation(self):
        """Scenario: After generating new run, old ISO run should be archived."""
        runs = {
            "20260312T104141Z": [],  # Old ISO run (10:41 AM)
            "03122026": [],          # New run just generated (but midnight)
        }

        # If we want to keep only the newest by actual time
        to_archive = identify_runs_to_archive(runs, keep_runs=1)

        # 20260312T104141Z (10:41) is newer than 03122026 (00:00)
        # So 03122026 should be archived
        assert len(to_archive) == 1
        assert "03122026" in to_archive

    def test_scenario_keep_5_recent(self):
        """Scenario: Default retention policy keeps 5 most recent runs."""
        runs = {
            "20260310": [],
            "20260311T230549Z": [],
            "20260311T231210Z": [],
            "20260312T093508Z": [],
            "20260312T101941Z": [],
            "20260312T104141Z": [],
            "03122026": [],
        }
        to_archive = identify_runs_to_archive(runs, keep_runs=5)

        # Should archive 2 oldest: 20260310 and 20260311T230549Z
        assert len(to_archive) == 2
        assert "20260310" in to_archive
        assert "20260311T230549Z" in to_archive
