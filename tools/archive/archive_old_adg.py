"""ADG archive retention helpers kept for regression coverage.

The operational archive CLI was retired with the old tools/archive tree, but
the retention rule remains covered by tests: only sqlite-backed ADG runs count
toward the keep-N quota.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def _parse_timestamp(ts: str) -> datetime:
    date_part = ts.split("_", 1)[0]
    if len(date_part) == 8 and date_part.isdigit():
        if date_part.startswith(("202", "203", "204", "205", "206")):
            return datetime.strptime(date_part, "%Y%m%d")
        return datetime.strptime(date_part, "%m%d%Y")
    return datetime.strptime(ts, "%Y%m%dT%H%M%SZ")


def _has_sqlite(files: list[Path]) -> bool:
    """Return true only when the run has a canonical indexed sqlite artifact."""
    return any(
        path.name.startswith("adg_indexed_") and path.suffix == ".sqlite"
        for path in files
    )


def identify_runs_to_archive(runs: dict[str, list[Path]], keep_runs: int) -> list[str]:
    """Return run timestamps that should be archived, oldest first."""
    canonical_ts = [ts for ts, files in runs.items() if _has_sqlite(files)]
    stranded_ts = [ts for ts, files in runs.items() if not _has_sqlite(files)]

    canonical_sorted_newest_first = sorted(
        canonical_ts,
        key=_parse_timestamp,
        reverse=True,
    )
    to_archive = canonical_sorted_newest_first[keep_runs:] + stranded_ts
    return sorted(to_archive, key=_parse_timestamp)
