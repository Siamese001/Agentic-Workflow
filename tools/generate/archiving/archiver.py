"""Timestamp parsing and artifact retention for ADG generation."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from tools.generate.utils.file_utils import _is_file_locked


def _extract_timestamp(filename: str) -> str | None:
    """Extract timestamp from ADG artifact filename.

    Supports formats:
        Current: adg_indexed_03122026_0512.sqlite    -> 03122026_0512  (MMDDYYYY_HHMM)
        Legacy1: adg_indexed_03122026.sqlite         -> 03122026       (MMDDYYYY)
        Legacy2: adg_indexed_20260312T093508Z.sqlite -> 20260312T093508Z  (ISO)
    """
    # Strip all extensions (handles .sqlite, .sqlite-shm, .sqlite-wal, .json, .zip)
    bare = filename.split(".")[0]
    parts = bare.split("_")
    if len(parts) < 3:
        return None

    # Check if last two parts form timestamp (MMDDYYYY_HHMM)
    if len(parts) >= 4:
        ts_date = parts[-2]
        ts_time = parts[-1]

        # Current format: MMDDYYYY_HHMM
        if len(ts_date) == 8 and ts_date.isdigit() and len(ts_time) == 4 and ts_time.isdigit():
            return f"{ts_date}_{ts_time}"

    # Last part is timestamp (legacy formats)
    ts = parts[-1]

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


_SQLITE_SIDE_SUFFIXES = (".sqlite", ".sqlite-wal", ".sqlite-shm")


def _sqlite_family_root(path: Path) -> Path:
    """Return the primary .sqlite file for a SQLite sidecar family."""
    if path.name.endswith(".sqlite-wal"):
        return path.with_name(path.name[: -len("-wal")])
    if path.name.endswith(".sqlite-shm"):
        return path.with_name(path.name[: -len("-shm")])
    return path


def _sqlite_family_locked(path: Path) -> bool:
    """Treat a SQLite family as locked if its primary database file is locked."""
    root_path = _sqlite_family_root(path)
    return root_path.exists() and _is_file_locked(root_path)


def _unlink_sqlite_family(file_path: Path) -> int:
    """Delete a SQLite file and its sidecars as one unit. Returns deleted file count."""
    deleted = 0
    root_path = _sqlite_family_root(file_path)
    targets = [root_path, root_path.with_suffix(".sqlite-wal"), root_path.with_suffix(".sqlite-shm")]

    if _sqlite_family_locked(root_path):
        raise OSError(f"SQLite family locked: {root_path.name}")

    if root_path.exists():
        temp_conn = None
        try:
            temp_conn = sqlite3.connect(str(root_path))
            temp_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:
            pass
        finally:
            if temp_conn is not None:
                temp_conn.close()

    for target in targets:
        if target.exists():
            target.unlink()
            deleted += 1

    return deleted


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
        "adg_*.sqlite-shm",
        "adg_*.sqlite-wal",
        "adg_run_*.zip",
        "scan_result_cache.json",
        "*_report_*.json",
        "test_surface_coverage_*.json",
        "repair_log_*.json",
        "p1_ratchet.json",
        "p2_ratchet.json",
    ]:
        for path in adg_dir.glob(pattern):  # tqdm: pre-scan accumulation, no display needed
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

    for ts in tqdm(to_archive, desc="[ADG] Archiving old runs", unit="run"):
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

            for file_path in files:  # tqdm: inner cleanup, progress shown by outer run loop
                if file_path not in zip_files and file_path.exists():
                    try:
                        file_size = file_path.stat().st_size
                    except OSError:
                        file_size = 0
                    try:
                        if file_path.name.endswith(_SQLITE_SIDE_SUFFIXES):
                            if _sqlite_family_locked(file_path):
                                print(
                                    f"[WARNING] Archive: locked SQLite family skipped {_sqlite_family_root(file_path).name}"
                                )
                                print(
                                    "[WARNING]   Main database is held by another process - sidecars preserved"
                                )
                                continue
                            archived_count += _unlink_sqlite_family(file_path)
                        else:
                            file_path.unlink()
                            archived_count += 1
                    except OSError as e:
                        print(f"[ADG] Archive: failed to remove {file_path.name}: {e}")
                        continue
                    bytes_original += file_size
        else:
            print(
                f"[ADG] Archive: Found orphaned run {ts} with {len(files)} individual files - DELETING (no longer archiving individual files)",
            )
            for file_path in files:  # tqdm: inner cleanup, progress shown by outer run loop
                if file_path.exists():
                    try:
                        file_size = file_path.stat().st_size
                        bytes_original += file_size
                    except OSError:
                        file_size = 0
                    try:
                        if file_path.name.endswith(_SQLITE_SIDE_SUFFIXES) and _sqlite_family_locked(
                            file_path
                        ):
                            print(
                                f"[WARNING] Archive: locked SQLite family skipped {_sqlite_family_root(file_path).name}"
                            )
                            print(
                                "[WARNING]   File held by another process - family will be cleaned up on next run"
                            )
                            continue

                        if file_path.name.endswith(_SQLITE_SIDE_SUFFIXES):
                            archived_count += _unlink_sqlite_family(file_path)
                        else:
                            file_path.unlink()
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
