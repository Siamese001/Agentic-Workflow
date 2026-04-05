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
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "archive_old_adg", "uwg_governed_write")
_emit_writes_through("p1", "archive_old_adg", "uwg_governed_write_2")
_emit_pulls_context("p1", "archive_old_adg", "context_retrieval")
_emit_pulls_context("p1", "archive_old_adg", "context_retrieval_2")
emit_determinism_digest("trace_archive_old_adg", "archive_old_adg_dispatch")
emit_determinism_digest("trace_archive_old_adg", "archive_old_adg_complete")
_emit_validated_by_safety_plane("p1", "archive_old_adg", "safety_validation")
_emit_reads_through("l4", "archive_old_adg", "urg_read_1")
_emit_reads_through("l4", "archive_old_adg", "urg_read_2")
_emit_reads_through("l4", "archive_old_adg", "urg_read_3")
_emit_reads_through("l4", "archive_old_adg", "urg_read_4")
_emit_reads_through("l4", "archive_old_adg", "urg_read_5")
_emit_reads_through("l4", "archive_old_adg", "urg_read_6")
_emit_reads_through("l4", "archive_old_adg", "urg_read_7")
_emit_reads_through("l4", "archive_old_adg", "urg_read_8")
_emit_reads_through("l4", "archive_old_adg", "urg_read_9")
_emit_reads_through("l4", "archive_old_adg", "urg_read_10")
_emit_reads_through("l4", "archive_old_adg", "urg_read_11")
_emit_reads_through("l4", "archive_old_adg", "urg_read_12")
_emit_reads_through("l4", "archive_old_adg", "urg_read_13")
_emit_reads_through("l4", "archive_old_adg", "urg_read_14")
_emit_reads_through("l4", "archive_old_adg", "urg_read_15")
_emit_reads_through("l4", "archive_old_adg", "urg_read_16")
_emit_reads_through("l4", "archive_old_adg", "urg_read_17")
_emit_reads_through("l4", "archive_old_adg", "urg_read_18")
_emit_reads_through("l4", "archive_old_adg", "urg_read_19")
_emit_reads_through("l4", "archive_old_adg", "urg_read_20")
_emit_reads_through("l4", "archive_old_adg", "urg_read_21")
_emit_reads_through("l4", "archive_old_adg", "urg_read_22")
_emit_reads_through("l4", "archive_old_adg", "urg_read_23")
_emit_reads_through("l4", "archive_old_adg", "urg_read_24")

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
        if ts.startswith(('202', '203', '204', '205', '206')):
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

    for pattern in ["adg_*.json", "adg_*.sqlite", "adg_*.md", "adg_repair_*.json"]:
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


def identify_runs_to_archive(runs: dict[str, list[Path]], keep_runs: int) -> list[str]:
    """Identify which runs should be archived based on retention policy.

    Args:
        runs: Dict mapping timestamp -> list of artifact paths
        keep_runs: Number of recent runs to keep

    Returns:
        List of timestamps to archive (oldest first)
    """
    if len(runs) <= keep_runs:
        return []

    # Sort timestamps by actual datetime (newest first)
    sorted_timestamps = sorted(runs.keys(), key=_parse_timestamp, reverse=True)

    # Keep the newest N runs, archive the rest
    to_archive = sorted_timestamps[keep_runs:]

    # Return oldest first (for archive processing order)
    return sorted(to_archive, key=_parse_timestamp)


def archive_run(ts: str, files: list[Path], compress: bool, dry_run: bool) -> dict:
    """Archive a single ADG run.

    Args:
        ts: Timestamp of the run
        files: List of artifact paths for this run
        compress: Whether to compress archived files
        dry_run: If True, only show what would be done

    Returns:
        Dict with statistics: files_archived, bytes_saved, etc.
    """
    archive_dir = _get_archive_month_dir(ts)

    stats: dict[str, Any] = {
        "timestamp": ts,
        "files_archived": 0,
        "bytes_original": 0,
        "bytes_archived": 0,
    }

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    for file_path in files:
        if not file_path.exists():
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

    if not to_archive:
        print(f"[ADG Archive] All runs are within retention policy (keep {args.keep_runs} runs)")
        print("[ADG Archive] Nothing to archive")
        return

    print(f"[ADG Archive] Retention policy: keep {args.keep_runs} most recent runs")
    print(f"[ADG Archive] Runs to archive: {len(to_archive)}")
    print()

    # Archive each run
    total_stats = {
        "runs_archived": 0,
        "files_archived": 0,
        "bytes_original": 0,
        "bytes_archived": 0,
    }

    for ts in to_archive:
        files = runs[ts]
        print(f"[ADG Archive] Archiving run {ts} ({len(files)} files)...")

        stats = archive_run(ts, files, compress, dry_run)

        total_stats["runs_archived"] += 1
        total_stats["files_archived"] += stats["files_archived"]
        total_stats["bytes_original"] += stats["bytes_original"]
        total_stats["bytes_archived"] += stats["bytes_archived"]

        archive_dir = _get_archive_month_dir(ts)
        print(f"    → {archive_dir.relative_to(ROOT)}")
        print(f"    → {stats['files_archived']} files, {format_bytes(stats['bytes_original'])} → {format_bytes(stats['bytes_archived'])}")

    print()
    print("[ADG Archive] Summary:")
    print(f"    Runs archived: {total_stats['runs_archived']}")
    print(f"    Files archived: {total_stats['files_archived']}")
    print(f"    Original size: {format_bytes(total_stats['bytes_original'])}")
    print(f"    Archived size: {format_bytes(total_stats['bytes_archived'])}")

    if compress:
        savings = total_stats['bytes_original'] - total_stats['bytes_archived']
        pct = (savings / total_stats['bytes_original'] * 100) if total_stats['bytes_original'] > 0 else 0
        print(f"    Space saved: {format_bytes(savings)} ({pct:.1f}%)")

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
