"""Timestamp parsing and artifact retention for ADG generation."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tools.generate.utils.file_utils import _is_file_locked


def _extract_timestamp(filename: str) -> str | None:
    """Extract timestamp from ADG artifact filename.

    Supports formats:
        Current: adg_indexed_03122026_0512.sqlite    -> 03122026_0512  (MMDDYYYY_HHMM)
        Legacy1: adg_indexed_03122026.sqlite         -> 03122026       (MMDDYYYY)
        Legacy2: adg_indexed_20260312T093508Z.sqlite -> 20260312T093508Z  (ISO)
    """
    parts = filename.split("_")
    if len(parts) < 3:
        return None

    # Check if last two parts form timestamp (MMDDYYYY_HHMM)
    if len(parts) >= 4:
        ts_date = parts[-2]
        ts_time_with_ext = parts[-1]
        ts_time = ts_time_with_ext.split(".")[0]

        # Current format: MMDDYYYY_HHMM
        if len(ts_date) == 8 and ts_date.isdigit() and len(ts_time) == 4 and ts_time.isdigit():
            return f"{ts_date}_{ts_time}"

    # Last part before extension should be timestamp (legacy formats)
    ts_with_ext = parts[-1]
    ts = ts_with_ext.split(".")[0]

    # Legacy format 1: MMDDYYYY (8 digits)
    if len(ts) == 8 and ts.isdigit():
        return ts
    # Legacy format 2: YYYYMMDDTHHMMSSz (16 chars)
    if len(ts) == 16 and ts[8] == "T" and ts.endswith("Z"):
        return ts
    return None


def _parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string to datetime.

    Args:
        ts: Timestamp string — "03122026_0512" (MMDDYYYY_HHMM), "03122026" (MMDDYYYY),
            "20260310" (YYYYMMDD legacy), or "20260311T160257Z" (ISO legacy)

    Returns:
        datetime object
    """
    # Current format: MMDDYYYY_HHMM
    if "_" in ts:
        return datetime.strptime(ts, "%m%d%Y_%H%M")

    if len(ts) == 8 and ts.isdigit():
        # Distinguish MMDDYYYY (new) from YYYYMMDD (legacy)
        # If first 4 chars are a plausible year (2020-2099), it's YYYYMMDD
        if ts.startswith(("202", "203", "204", "205", "206")):
            return datetime.strptime(ts, "%Y%m%d")
        return datetime.strptime(ts, "%m%d%Y")
    return datetime.strptime(ts, "%Y%m%dT%H%M%SZ")


def _archive_old_artifacts(adg_dir: Path, current_ts: str, keep_runs: int = 1) -> None:
    """Archive old ADG runs to keep artifacts directory clean.

    Uses run-based retention (keeps last N complete runs) rather than day-based.

    Args:
        adg_dir: ADG artifacts directory
        current_ts: Current timestamp (MMDDYYYY)
        keep_runs: Number of recent complete runs to keep (default: 1)
    """
    if not adg_dir.exists():
        return

    runs: dict[str, list[Path]] = defaultdict(list)

    for pattern in [
        "adg_*.json",
        "adg_*.sqlite",
        "adg_run_*.zip",
        "scan_result_cache.json",
        "*_report_*.json",
        "test_surface_coverage_*.json",
        "repair_log_*.json",
        "p2_ratchet.json",
    ]:
        for path in adg_dir.glob(pattern):
            if "LATEST" in path.name or "latest" in path.name:
                continue
            if "_archive" in str(path):
                continue

            if path.name.startswith("adg_run_") and path.suffix == ".zip":
                ts = path.stem.replace("adg_run_", "")
            else:
                ts = _extract_timestamp(path.name)

            if ts:
                runs[ts].append(path)

    if len(runs) <= keep_runs:
        return

    sorted_timestamps = sorted(runs.keys(), key=_parse_timestamp, reverse=True)
    to_archive = sorted_timestamps[keep_runs:]

    if not to_archive:
        return

    from tools.generate.archiving.zipper import _archive_zip_files

    archived_count = 0
    bytes_original = 0
    bytes_archived = 0

    for ts in to_archive:
        files = runs[ts]

        try:
            dt = _parse_timestamp(ts)
            archive_month_dir = adg_dir / "_archive" / dt.strftime("%Y-%m")
            archive_month_dir.mkdir(parents=True, exist_ok=True)
        except (ValueError, OSError) as e:
            print(f"[ADG] Archive: failed to create archive dir for {ts}: {e}")
            continue

        zip_files = [f for f in files if f.name.startswith("adg_run_") and f.suffix == ".zip"]

        if zip_files:
            print(f"[ADG] Archive: Processing run {ts} with {len(zip_files)} zip file(s)")
            zip_archived, zip_bytes_original, zip_bytes_archived = _archive_zip_files(
                zip_files,
                archive_month_dir,
            )
            archived_count += zip_archived
            bytes_original += zip_bytes_original
            bytes_archived += zip_bytes_archived

            for file_path in files:
                if file_path not in zip_files and file_path.exists():
                    try:
                        file_size = file_path.stat().st_size
                    except OSError:
                        file_size = 0
                    try:
                        if file_path.suffix == ".sqlite":
                            try:
                                temp_conn = sqlite3.connect(str(file_path))
                                temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                                temp_conn.close()
                            except Exception:  # guardian: allow-broad-exception -- best-effort cleanup: WAL checkpoint failure should not block archive deletion
                                pass
                        file_path.unlink()
                    except OSError as e:
                        print(f"[ADG] Archive: failed to remove {file_path.name}: {e}")
                        continue
                    archived_count += 1
                    bytes_original += file_size
        else:
            print(
                f"[ADG] Archive: Found orphaned run {ts} with {len(files)} individual files - DELETING (no longer archiving individual files)",
            )
            for file_path in files:
                if file_path.exists():
                    try:
                        file_size = file_path.stat().st_size
                        bytes_original += file_size
                    except OSError:
                        file_size = 0
                    try:
                        if _is_file_locked(file_path):
                            print(f"[WARNING] Archive: locked file skipped {file_path.name}")
                            print("[WARNING]   File held by another process — will be cleaned up on next run")
                            continue

                        if file_path.suffix == ".sqlite":
                            try:
                                temp_conn = sqlite3.connect(str(file_path))
                                temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                                temp_conn.close()
                            except Exception:  # guardian: allow-broad-exception -- best-effort cleanup: WAL checkpoint failure should not block orphan deletion
                                pass
                        file_path.unlink()

                        if file_path.suffix == ".sqlite":
                            wal_path = file_path.with_suffix(".sqlite-wal")
                            shm_path = file_path.with_suffix(".sqlite-shm")
                            for aux_file in [wal_path, shm_path]:
                                if aux_file.exists():
                                    try:
                                        aux_file.unlink()
                                    except OSError:
                                        pass

                        archived_count += 1
                    except OSError as e:
                        if "being used by another process" in str(e):
                            print(f"[WARNING] Archive: locked file skipped {file_path.name}")
                            print("[WARNING]   File held by another process — will be cleaned up on next run")
                        else:
                            print(f"[ADG] Archive: failed to delete {file_path.name}: {e}")
                        continue

    if bytes_original > 0:
        savings = bytes_original - bytes_archived
        pct = (savings / bytes_original * 100) if bytes_original > 0 else 0
        print(f"[ADG] Archive: archived {len(to_archive)} runs, {archived_count} files (saved {pct:.0f}%)")

    # Delegate cleanup of validation packages and MANIFEST files
    from tools.generate.reporting.analysis import _cleanup_validation_files
    _cleanup_validation_files(adg_dir, current_ts)
