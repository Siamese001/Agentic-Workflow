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








class TestTimestampParsing:
    """Test _parse_timestamp: timestamp string → datetime object."""








class TestDatetimeBasedSorting:
    """Test that sorting uses actual datetime, not lexicographic string comparison."""




class TestRetentionPolicy:
    """Test identify_runs_to_archive: keep N newest runs."""







class TestArchiveMonthDirectory:
    """Test _get_archive_month_dir: timestamp → archive directory path."""







class TestEdgeCases:
    """Edge cases and boundary conditions."""






