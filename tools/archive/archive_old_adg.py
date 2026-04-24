"""Archive old ADG artifacts to keep artifacts/adg directory clean.

Archiving Strategy
------------------
- Keep LATEST files (always current)
- Keep last N runs (default: 5) of timestamped artifacts
- Archive older runs to artifacts/adg/_archive/<YYYY-MM>/
- Compress archived files to save space

Retention Policy
----------------
- LATEST files: Never archived (always current)
- Recent runs: Keep last 5 complete runs (configurable)
- Archived runs: Moved to _archive/<YYYY-MM>/ and compressed
- Archive retention: Keep archives for 6 months (configurable)

Usage
-----
    python tools/archive_old_adg.py                    # Dry run (show what would be archived)
    python tools/archive_old_adg.py --execute          # Actually archive files
    python tools/archive_old_adg.py --keep-runs 10     # Keep last 10 runs
    python tools/archive_old_adg.py --compress         # Compress archives (default)
"""

from __future__ import annotations

import argparse
import gzip
import logging
import os
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = ROOT / "artifacts" / "adg"
ARCHIVE_DIR = ADG_DIR / "_archive"

# Default retention policy
DEFAULT_KEEP_RUNS = 5
DEFAULT_ARCHIVE_MONTHS = 6

# File patterns for each run (5 artifacts per run, non-redundant)
ARTIFACT_PATTERNS = [
    "adg_snapshot_{ts}.json",
    "adg_indexed_{ts}.sqlite",
    "adg_file_graph_{ts}.json",
    "adg_symbol_graph_{ts}.json",
    "adg_governance_graph_{ts}.json",
    "adg_graphsnap_{ts}.json",  # E7 snapshot
]


def _extract_timestamp(filename: str) -> str | None:
    """Extract timestamp from ADG artifact filename.

    Supports formats:
        New: adg_indexed_03122026.sqlite    -> 03122026  (MMDDYYYY)
        New+time: adg_indexed_04052026_1133.sqlite -> 04052026 (MMDDYYYY + time)
        New+probe: adg_indexed_04052026_1133_probe.sqlite -> 04052026_probe (with suffix)
        Old: adg_indexed_20260312T093508Z.sqlite -> 20260312T093508Z  (legacy)
        Repair: adg_repair_03312026_0951.json -> 03312026  (MMDDYYYY + time suffix)
    """
    parts = filename.split("_")
    if len(parts) < 3:
        return None

    # Handle repair file format: adg_repair_03312026_0951.json
    if len(parts) >= 4 and parts[1] == "repair":
        # Timestamp is the third part (index 2) for repair files
        ts = parts[2]
        if len(ts) == 8 and ts.isdigit():
            return ts
        return None

    # Find the 8-digit MMDDYYYY timestamp in parts
    # New format: adg_indexed_04052026_1133.sqlite or adg_indexed_04052026_1133_probe.sqlite
    for i, part in enumerate(parts):
        # Check if this part is 8 digits (MMDDYYYY)
        if len(part) == 8 and part.isdigit():
            # Found timestamp part
            # Build full timestamp including any suffix after it
            remaining_parts = parts[i:]
            # Remove extension from last part
            remaining_parts[-1] = remaining_parts[-1].split(".")[0]
            return "_".join(remaining_parts)

    # Legacy format: YYYYMMDDTHHMMSSz (16 chars) at end
    ts_with_ext = parts[-1]
    ts = ts_with_ext.split(".")[0]
    if len(ts) == 16 and ts[8] == "T" and ts.endswith("Z"):
        return ts

    return None


def _parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string to datetime.

    Args:
        ts: Timestamp string — "03122026" (MMDDYYYY), "04042026_1942" (MMDDYYYY + time),
            "20260310" (YYYYMMDD legacy), or "20260311T160257Z" (ISO legacy)

    Returns:
        datetime object
    """
    # Handle new format with time suffix: "04042026_1942"
    if "_" in ts:
        ts_parts = ts.split("_")
        date_part = ts_parts[0]
        if len(date_part) == 8 and date_part.isdigit():
            # MMDDYYYY format
            return datetime.strptime(date_part, "%m%d%Y")

    if len(ts) == 8 and ts.isdigit():
        # Distinguish MMDDYYYY (new) from YYYYMMDD (legacy)
        # If first 4 chars are a plausible year (2020-2099), it's YYYYMMDD
        if ts.startswith(("202", "203", "204", "205", "206")):
            return datetime.strptime(ts, "%Y%m%d")
        return datetime.strptime(ts, "%m%d%Y")
    return datetime.strptime(ts, "%Y%m%dT%H%M%SZ")


def _get_archive_month_dir(ts: str) -> Path:
    """Get archive directory for a timestamp.

    Args:
        ts: Timestamp string — either "03122026" (MMDDYYYY) or legacy ISO format

    Returns:
        Path like artifacts/adg/_archive/2026-03/
    """
    dt = _parse_timestamp(ts)
    month_str = dt.strftime("%Y-%m")
    return ARCHIVE_DIR / month_str


def discover_runs() -> dict[str, list[Path]]:
    """Discover all ADG runs by grouping files by timestamp.

    Returns:
        Dict mapping timestamp -> list of artifact paths for that run
    """
    runs: dict[str, list[Path]] = defaultdict(list)
    seen_files: set[Path] = set()

    for pattern in [
        "adg_*.json",
        "adg_*.sqlite",
        "adg_*.md",
        "adg_repair_*.json",
        "*_report_*.json",
        "test_surface_coverage_*.json",
        "*_log_*.json",
        "execution_impact_*.json",
        "repair_log_*.json",
        "scan_result_cache.json",
        "adg_*.zip",
    ]:
        for path in ADG_DIR.glob(pattern):
            # Skip LATEST files
            if "LATEST" in path.name:
                continue

            # Skip archived files
            if path.is_relative_to(ARCHIVE_DIR):
                continue

            # Deduplicate (repair files may match both patterns)
            if path in seen_files:
                continue
            seen_files.add(path)

            ts = _extract_timestamp(path.name)
            if ts:
                runs[ts].append(path)

    return dict(runs)


def _has_sqlite(files: list[Path]) -> bool:
    """A run is 'real' only if it includes at least one adg_indexed_*.sqlite file.

    This constraint prevents a JSON-only or repair-only timestamp from being
    treated as a canonical run. Without it, a stray `adg_snapshot_<ts>.json`
    left over from a failed indexing step could be promoted into the keep-N
    set and push a REAL sqlite-backed run into the archive queue.

    Regression precedent: 2026-04-23 cleanup run auto-archived a live
    adg_indexed_*.sqlite because a JSON-only timestamp outranked it.
    """
    return any(
        p.name.startswith("adg_indexed_") and p.suffix == ".sqlite"
        for p in files
    )


def identify_runs_to_archive(runs: dict[str, list[Path]], keep_runs: int) -> list[str]:
    """Identify which runs should be archived based on retention policy.

    A run is considered canonical ONLY when it includes at least one
    `adg_indexed_*.sqlite` file (see `_has_sqlite`). Runs without a sqlite
    backing (e.g. stranded JSON / repair artifacts from a crashed generator)
    are ALWAYS eligible for archive regardless of keep-N \u2014 they are not
    counted toward the keep quota.

    Args:
        runs: Dict mapping timestamp -> list of artifact paths
        keep_runs: Number of recent SQLite-backed runs to keep

    Returns:
        List of timestamps to archive (oldest first)
    """
    # Partition: canonical (has sqlite) vs stranded (no sqlite).
    canonical_ts = [ts for ts, files in runs.items() if _has_sqlite(files)]
    stranded_ts = [ts for ts, files in runs.items() if not _has_sqlite(files)]

    # Keep the newest N CANONICAL runs only. Stranded runs go straight to
    # the archive queue regardless of age.
    canonical_sorted_newest_first = sorted(
        canonical_ts, key=_parse_timestamp, reverse=True
    )
    canonical_to_archive = canonical_sorted_newest_first[keep_runs:]

    to_archive = canonical_to_archive + stranded_ts

    # Return oldest first (for archive processing order)
    return sorted(to_archive, key=_parse_timestamp)


def archive_run(
    ts: str,
    files: list[Path],
    compress: bool,
    dry_run: bool,
    active_timestamp: str | None = None,
) -> dict:
    """Archive a single ADG run.

    Args:
        ts: Timestamp of the run
        files: List of artifact paths for this run
        compress: Whether to compress archived files
        dry_run: If True, only show what would be done
        active_timestamp: Timestamp of the currently active ADG (files with this timestamp are skipped)

    Returns:
        Dict with statistics: files_archived, bytes_saved, files_skipped, etc.
    """
    archive_dir = _get_archive_month_dir(ts)

    stats: dict[str, Any] = {
        "timestamp": ts,
        "files_archived": 0,
        "bytes_original": 0,
        "bytes_archived": 0,
        "files_skipped": 0,
        "skip_reasons": [],
    }

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    for file_path in files:
        if not file_path.exists():
            continue

        # Check if file belongs to active ADG
        if active_timestamp and active_timestamp in file_path.name:
            reason = f"active ADG database ({active_timestamp})"
            stats["files_skipped"] += 1
            stats["skip_reasons"].append(f"{file_path.name}: {reason}")
            logger.info("Skipping %s: %s", file_path.name, reason)
            continue

        # Check if file is locked
        if _is_file_locked(file_path):
            reason = "file locked by another process"
            stats["files_skipped"] += 1
            stats["skip_reasons"].append(f"{file_path.name}: {reason}")
            logger.warning("Skipping %s: %s", file_path.name, reason)
            continue

        original_size = file_path.stat().st_size
        stats["bytes_original"] += original_size

        if compress and file_path.suffix in [".json", ".sqlite", ".md"]:
            # Compress and archive
            archive_path = archive_dir / f"{file_path.name}.gz"

            if not dry_run:
                with open(file_path, "rb") as f_in:
                    with gzip.open(archive_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                file_path.unlink()

            if archive_path.exists():
                stats["bytes_archived"] += archive_path.stat().st_size
            else:
                # Estimate compression ratio for dry run
                stats["bytes_archived"] += int(original_size * 0.15)  # ~85% compression
        else:
            # Move without compression
            archive_path = archive_dir / file_path.name

            if not dry_run:
                shutil.move(str(file_path), str(archive_path))

            stats["bytes_archived"] += original_size

        stats["files_archived"] += 1

    return stats


def cleanup_old_archives(archive_months: int, dry_run: bool) -> dict:
    """Remove archives older than specified months.

    Args:
        archive_months: Keep archives for this many months
        dry_run: If True, only show what would be deleted

    Returns:
        Dict with statistics
    """
    if not ARCHIVE_DIR.exists():
        return {"dirs_removed": 0, "bytes_freed": 0}

    cutoff_date = datetime.now() - timedelta(days=archive_months * 30)

    stats = {"dirs_removed": 0, "bytes_freed": 0}

    for month_dir in ARCHIVE_DIR.iterdir():
        if not month_dir.is_dir():
            continue

        # Parse directory name: YYYY-MM
        try:
            dir_date = datetime.strptime(month_dir.name, "%Y-%m")
        except ValueError as e:
            logger.warning("Invalid input: %s", e)
            continue

        if dir_date < cutoff_date:
            # Calculate size before deletion
            dir_size = sum(f.stat().st_size for f in month_dir.rglob("*") if f.is_file())
            stats["bytes_freed"] += dir_size

            if not dry_run:
                shutil.rmtree(month_dir)

            stats["dirs_removed"] += 1

    return stats


def format_bytes(bytes_count: float) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


def _is_file_locked(file_path: Path) -> bool:
    """Check if a file is locked by another process.

    On Windows, attempts to open the file exclusively.
    On Unix, checks if the file has associated WAL files (SQLite indicator).

    Args:
        file_path: Path to the file to check

    Returns:
        True if file is locked, False otherwise
    """
    if not file_path.exists():
        return False

    # Check for SQLite WAL files (indicates active connection)
    if file_path.suffix == ".sqlite":
        wal_file = file_path.with_suffix(".sqlite-wal")
        shm_file = file_path.with_suffix(".sqlite-shm")
        if wal_file.exists() or shm_file.exists():
            return True

    # On Windows, try to open the file exclusively
    if os.name == "nt":
        try:
            # Try to open file in exclusive read mode
            open(file_path, "rb", buffering=0).close()
            return False
        except (PermissionError, OSError) as e:
            logger.debug("File locked: %s - %s", file_path.name, e)
            return True

    # On Unix, we can't reliably detect locks without additional tools
    # Fall back to WAL file check above
    return False


def _get_active_adg_timestamp() -> str | None:
    """Get the timestamp of the currently active ADG database.

    Reads the ADG snapshot metadata to identify the active database.

    Returns:
        Timestamp string (e.g., "04052026_1842") or None if not found
    """
    # Check for snapshot files to identify latest ADG
    snapshot_files = list(ADG_DIR.glob("adg_snapshot_*.json"))
    if not snapshot_files:
        return None

    # Get the most recent snapshot
    latest_snapshot = max(snapshot_files, key=lambda p: p.stat().st_mtime)
    ts = _extract_timestamp(latest_snapshot.name)
    return ts


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive old ADG artifacts")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually archive files (default is dry run)",
    )
    parser.add_argument(
        "--keep-runs",
        type=int,
        default=DEFAULT_KEEP_RUNS,
        help=f"Number of recent runs to keep (default: {DEFAULT_KEEP_RUNS})",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        default=True,
        help="Compress archived files (default: True)",
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Do not compress archived files",
    )
    parser.add_argument(
        "--archive-months",
        type=int,
        default=DEFAULT_ARCHIVE_MONTHS,
        help=f"Keep archives for this many months (default: {DEFAULT_ARCHIVE_MONTHS})",
    )
    parser.add_argument(
        "--cleanup-old",
        action="store_true",
        help="Also cleanup archives older than --archive-months",
    )

    args = parser.parse_args()

    compress = args.compress and not args.no_compress
    dry_run = not args.execute

    if dry_run:
        print("[DRY RUN] No files will be modified. Use --execute to actually archive.")
        print()

    # Discover all runs
    print(f"[ADG Archive] Scanning {ADG_DIR}...")
    runs = discover_runs()
    print(f"[ADG Archive] Found {len(runs)} timestamped runs")
    print()

    # Identify runs to archive
    to_archive = identify_runs_to_archive(runs, args.keep_runs)

    # Get active ADG timestamp to skip locked files
    active_timestamp = _get_active_adg_timestamp()
    if active_timestamp:
        print(f"[ADG Archive] Active ADG timestamp: {active_timestamp}")
        print("[ADG Archive] Files with this timestamp will be skipped")
        print()

    if not to_archive:
        print(f"[ADG Archive] All runs are within retention policy (keep {args.keep_runs} runs)")
        print("[ADG Archive] Nothing to archive")
        return

    print(f"[ADG Archive] Retention policy: keep {args.keep_runs} most recent runs")
    print(f"[ADG Archive] Runs to archive: {len(to_archive)}")
    print()

    # Archive each run
    total_stats: dict[str, Any] = {
        "runs_archived": 0,
        "files_archived": 0,
        "bytes_original": 0,
        "bytes_archived": 0,
        "files_skipped": 0,
        "skip_reasons": [],
    }

    for ts in to_archive:
        files = runs[ts]
        print(f"[ADG Archive] Archiving run {ts} ({len(files)} files)...")

        stats = archive_run(ts, files, compress, dry_run, active_timestamp)

        total_stats["runs_archived"] += 1
        total_stats["files_archived"] += stats["files_archived"]
        total_stats["bytes_original"] += stats["bytes_original"]
        total_stats["bytes_archived"] += stats["bytes_archived"]
        total_stats["files_skipped"] += stats["files_skipped"]
        total_stats["skip_reasons"].extend(stats["skip_reasons"])

        archive_dir = _get_archive_month_dir(ts)
        print(f"    → {archive_dir.relative_to(ROOT)}")
        if stats["files_skipped"] > 0:
            print(
                f"    → {stats['files_archived']} files archived, {stats['files_skipped']} files skipped (locked or active)",
            )
            print(f"    → {format_bytes(stats['bytes_original'])} → {format_bytes(stats['bytes_archived'])}")
        else:
            print(
                f"    → {stats['files_archived']} files, {format_bytes(stats['bytes_original'])} → {format_bytes(stats['bytes_archived'])}",
            )

    print()
    print("[ADG Archive] Summary:")
    print(f"    Runs archived: {total_stats['runs_archived']}")
    print(f"    Files archived: {total_stats['files_archived']}")
    if total_stats["files_skipped"] > 0:
        print(f"    Files skipped: {total_stats['files_skipped']}")
    print(f"    Original size: {format_bytes(total_stats['bytes_original'])}")
    print(f"    Archived size: {format_bytes(total_stats['bytes_archived'])}")

    if compress:
        savings = total_stats["bytes_original"] - total_stats["bytes_archived"]
        pct = (savings / total_stats["bytes_original"] * 100) if total_stats["bytes_original"] > 0 else 0
        print(f"    Space saved: {format_bytes(savings)} ({pct:.1f}%)")

    # Show skip reasons if any files were skipped
    if total_stats["skip_reasons"]:
        print()
        print("[ADG Archive] Skipped files (reasons):")
        for reason in total_stats["skip_reasons"]:
            print(f"    - {reason}")

    # Cleanup old archives if requested
    if args.cleanup_old:
        print()
        print(f"[ADG Archive] Cleaning up archives older than {args.archive_months} months...")
        cleanup_stats = cleanup_old_archives(args.archive_months, dry_run)

        if cleanup_stats["dirs_removed"] > 0:
            print(f"    Removed {cleanup_stats['dirs_removed']} archive directories")
            print(f"    Freed {format_bytes(cleanup_stats['bytes_freed'])}")
        else:
            print("    No old archives to remove")


if __name__ == "__main__":
    main()
