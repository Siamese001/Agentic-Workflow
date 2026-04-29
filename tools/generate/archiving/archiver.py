"""Timestamp parsing and artifact retention for ADG generation."""

from __future__ import annotations

import re
import sqlite3
import shutil
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from tools.generate.utils.file_utils import _is_file_locked

# ---------------------------------------------------------------------------
# Session scratch cleanup (P1 of RCA 2026-04-28: generator never cleaned
# up ad-hoc `python ... > _foo.log` redirect outputs or manual wave-queue
# TSV/TXT files sitting in artifacts/adg/). These patterns target files that
# are NOT produced by the generator but accumulate indefinitely because
# they live in the same directory. Deletion is age-gated (default 3 days)
# so in-flight work is never touched.
# ---------------------------------------------------------------------------
# Fast-cycle scratch — produced by single foreground commands (e.g.
# ``python tools/generate_full_adg.py > _w1_regen.log``). Once the command
# exits, the file is reference material at most; after 1 hour it's stale.
_SESSION_SCRATCH_FAST_GLOBS: tuple[str, ...] = (
    "_*.log",
    "_*.txt",
    "_*.py",
    "_*.err",
)

# Slow-cycle scratch — produced by analysis sessions, may be referenced
# across a workday. 24-hour floor.
_SESSION_SCRATCH_SLOW_GLOBS: tuple[str, ...] = (
    "wave_*.tsv",
    "wave_*.txt",
    "wave_queue_*.tsv",
    "tech_debt_*.txt",
    "dead_*scan*.txt",
    "*_scan_*.txt",
    "stub_archive_candidates.json",
)

# Bare-SHA256 JSON filenames produced by the scan-result fingerprint cache
# (64 hex chars + ``.json``). These accumulate one per distinct scan config.
# 24-hour floor (overlaps slow group conceptually).
_SHA256_JSON_RE = re.compile(r"^[0-9a-f]{64}\.json$")

# Sentinel SQLite files (e.g. ``adg_indexed_99999999_9999.sqlite``) whose
# timestamp cannot be parsed. Age-gated deletion default.
_STALE_UNPARSEABLE_AGE_DAYS_DEFAULT = 7
# Default ages — fast group cleared aggressively, slow group preserved a day.
_SCRATCH_FAST_AGE_HOURS_DEFAULT = 1.0
_SCRATCH_SLOW_AGE_HOURS_DEFAULT = 24.0
# Back-compat alias for callers (and the docstring header).
_SCRATCH_AGE_DAYS_DEFAULT = _SCRATCH_SLOW_AGE_HOURS_DEFAULT / 24.0


def _extract_timestamp(filename: str) -> str | None:
    """Extract timestamp from ADG artifact filename.

    Supports formats:
        Current:  adg_indexed_03122026_0512.sqlite        -> 03122026_0512     (MMDDYYYY_HHMM)
        ISO-like: adg_graph_watchlist_20260423_155151.json -> 20260423_155151  (YYYYMMDD_HHMMSS)
        Legacy1:  adg_indexed_03122026.sqlite             -> 03122026          (MMDDYYYY)
        Legacy2:  adg_indexed_20260312T093508Z.sqlite     -> 20260312T093508Z  (ISO compact)

    The YYYYMMDD_HHMMSS variant is emitted by sub-builders (anomaly watchlist,
    graph watchlist, gate results). Without this branch, ~200 files per week
    accumulate without ever being recognized by the archiver.
    """
    # Strip all extensions (handles .sqlite, .sqlite-shm, .sqlite-wal, .json, .zip)
    bare = filename.split(".")[0]
    parts = bare.split("_")
    if len(parts) < 3:
        return None

    # Check if last two parts form a dated timestamp
    if len(parts) >= 3:
        ts_date = parts[-2]
        ts_time = parts[-1]

        if len(ts_date) == 8 and ts_date.isdigit() and ts_time.isdigit():
            # MMDDYYYY_HHMM (4-digit time) — main generator format
            if len(ts_time) == 4:
                return f"{ts_date}_{ts_time}"
            # YYYYMMDD_HHMMSS (6-digit time) — sub-builder format
            # Disambiguate by year-leading prefix (20xx/21xx)
            if len(ts_time) == 6 and ts_date.startswith(("202", "203", "204", "205", "206")):
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
        ts: Timestamp string in one of:
            - "03122026_0512"      (MMDDYYYY_HHMM   — main generator)
            - "20260312_093508"    (YYYYMMDD_HHMMSS — sub-builders)
            - "03122026"           (MMDDYYYY        — legacy)
            - "20260310"           (YYYYMMDD        — legacy)
            - "20260311T160257Z"   (ISO compact     — legacy)

    Returns:
        datetime object
    """
    # Dated formats with underscore separator
    if "_" in ts:
        date_part, time_part = ts.split("_", 1)
        # YYYYMMDD_HHMMSS: year-leading date + 6-digit time
        if (
            len(date_part) == 8
            and date_part.isdigit()
            and date_part.startswith(("202", "203", "204", "205", "206"))
            and len(time_part) == 6
            and time_part.isdigit()
        ):
            return datetime.strptime(ts, "%Y%m%d_%H%M%S")
        # MMDDYYYY_HHMM: 8+4 digits, month-leading
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


def _path_size_bytes(path: Path) -> int:
    """Best-effort size accounting for files and directories."""
    try:
        if path.is_dir():
            return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())
        return path.stat().st_size
    except OSError:
        return 0


def _remove_artifact_path(path: Path) -> int:
    """Remove an archived artifact path (file, SQLite family, or directory)."""
    if path.is_dir():
        shutil.rmtree(path)
        return 1

    if path.name.endswith(_SQLITE_SIDE_SUFFIXES):
        if _sqlite_family_locked(path):
            raise OSError(f"SQLite family locked: {_sqlite_family_root(path).name}")
        return _unlink_sqlite_family(path)

    path.unlink()
    return 1


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
        "graphdb_*",
        "scan_result_cache.json",
        "*_report_*.json",
        "test_surface_coverage_*.json",
        "repair_log_*.json",
        "p1_ratchet.json",
        "p2_ratchet.json",
        "archive_skipped_*.txt",
    ]:
        for path in adg_dir.glob(pattern):  # tqdm: pre-scan accumulation, no display needed
            if "LATEST" in path.name or "latest" in path.name:
                continue
            if "_archive" in path.parts:
                continue

            if path.name.startswith("adg_run_") and path.suffix == ".zip":
                ts_opt: str | None = path.stem.replace("adg_run_", "")
            else:
                ts_opt = _extract_timestamp(path.name)

            if ts_opt:
                runs[ts_opt].append(path)

    if len(runs) <= keep_runs:
        return

    valid_timestamps = []
    unparseable_ts: list[str] = []
    for ts in runs.keys():
        try:
            valid_timestamps.append((ts, _parse_timestamp(ts)))
        except ValueError as exc:
            print(f"[ADG] Archive: malformed timestamp {ts}: {exc} (will age-check)")
            unparseable_ts.append(ts)

    # P2 of RCA 2026-04-28: files with unparseable timestamps (e.g. the
    # sentinel ``adg_indexed_99999999_9999.sqlite``) used to be silently
    # skipped forever. Now age-gated: if every file in the bucket is older
    # than _STALE_UNPARSEABLE_AGE_DAYS_DEFAULT, delete it.
    _purge_unparseable_buckets(runs, unparseable_ts, _STALE_UNPARSEABLE_AGE_DAYS_DEFAULT)

    sorted_timestamps = [ts for ts, _dt in sorted(valid_timestamps, key=lambda item: item[1], reverse=True)]
    to_archive = sorted_timestamps[keep_runs:]

    # 2026-04-28 RCA: the run that just completed (``current_ts``) MUST NEVER
    # be archived, even if a sub-builder artifact in a different timezone
    # has a numerically larger timestamp. Sub-builders use UTC
    # (YYYYMMDD_HHMMSS) while the main run uses local time (MMDDYYYY_HHMM);
    # naive datetime comparison can rank UTC sub-builder timestamps from
    # the same wall-clock moment as "newer" than the main run, causing
    # the current run's zip + sqlite to be moved to ``_archive/`` and the
    # downstream Redis/git-commit steps to fail with "SQLite artifact not
    # found". Belt-and-suspenders: also exclude any bucket whose files
    # belong to the current run by filename.
    if current_ts in to_archive:
        to_archive.remove(current_ts)
        print(f"[ADG] Archive: protecting current run {current_ts} from archival (TZ-safe guard)")
    # Exclude buckets that contain a file with current_ts in its name —
    # catches sub-builder artifacts from the same run that landed in a
    # different timestamp bucket due to TZ skew.
    safe_to_archive: list[str] = []
    for ts in to_archive:
        files = runs.get(ts, [])
        if any(current_ts in p.name for p in files):
            print(f"[ADG] Archive: protecting bucket {ts} — contains current_ts={current_ts} files")
            continue
        safe_to_archive.append(ts)
    to_archive = safe_to_archive

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
                    file_size = _path_size_bytes(file_path)
                    try:
                        archived_count += _remove_artifact_path(file_path)
                    except OSError as e:
                        if "SQLite family locked" in str(e):
                            print(f"[WARNING] Archive: locked SQLite family skipped {e}")
                            print("[WARNING]   MCP server holds this file open. It will NOT auto-clean.")
                            print("[WARNING]   Fix: call adg_close_connections() MCP tool, then re-run.")
                            continue
                        print(f"[ADG] Archive: failed to remove {file_path.name}: {e}")
                        continue
                    bytes_original += file_size
        else:
            print(
                f"[ADG] Archive: Found orphaned run {ts} with {len(files)} individual files - DELETING (no longer archiving individual files)",
            )
            for file_path in files:  # tqdm: inner cleanup, progress shown by outer run loop
                if file_path.exists():
                    file_size = _path_size_bytes(file_path)
                    bytes_original += file_size
                    try:
                        archived_count += _remove_artifact_path(file_path)
                    except OSError as e:
                        if "SQLite family locked" in str(e):
                            print(f"[WARNING] Archive: locked SQLite family skipped {e}")
                            print("[WARNING]   MCP server holds this file open. It will NOT auto-clean.")
                            print("[WARNING]   Fix: call adg_close_connections() MCP tool, then re-run.")
                        elif "being used by another process" in str(e):
                            print(f"[WARNING] Archive: locked file skipped {file_path.name}")
                            print("[WARNING]   MCP server holds this file open. It will NOT auto-clean.")
                            print("[WARNING]   Fix: call adg_close_connections() MCP tool, then re-run.")
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

    # P1 of RCA 2026-04-28: age-gated cleanup of session scratch (ad-hoc
    # redirect logs, wave queue files, triage outputs). Runs AFTER the
    # main retention pass so it can't race the current-run zip or delete
    # anything the generator touched this cycle.
    _cleanup_session_scratch(adg_dir, max_age_days=_SCRATCH_AGE_DAYS_DEFAULT)


def _purge_unparseable_buckets(
    runs: dict[str, list[Path]],
    unparseable_ts: list[str],
    max_age_days: int,
) -> None:
    """Delete artifact buckets whose timestamp could not be parsed, if stale.

    A bucket is purged only when **every** file in it is older than
    ``max_age_days``. This prevents accidental deletion of in-flight work
    while still retiring long-lived sentinels like
    ``adg_indexed_99999999_9999.sqlite``.
    """
    if not unparseable_ts:
        return

    cutoff = time.time() - (max_age_days * 86400)
    for ts in unparseable_ts:
        files = runs.get(ts, [])
        if not files:
            continue
        try:
            all_stale = all(p.exists() and p.stat().st_mtime < cutoff for p in files)
        except OSError:
            continue
        if not all_stale:
            continue
        for path in files:
            try:
                _remove_artifact_path(path)
                print(f"[ADG] Archive: purged stale unparseable artifact {path.name}")
            except OSError as exc:
                print(f"[ADG] Archive: failed to purge {path.name}: {exc}")


def _cleanup_session_scratch(
    adg_dir: Path,
    max_age_days: float | None = None,
    *,
    fast_age_hours: float = _SCRATCH_FAST_AGE_HOURS_DEFAULT,
    slow_age_hours: float = _SCRATCH_SLOW_AGE_HOURS_DEFAULT,
) -> None:
    """Delete ad-hoc session scratch files older than the appropriate age floor.

    Two age tiers, applied per pattern group:

    - **Fast** (default 1 hour): single-command redirect outputs — ``_*.log``,
      ``_*.txt``, ``_*.py``, ``_*.err``. Once the producing command exits the
      file is reference material at most; an hour is generous.
    - **Slow** (default 24 hours): multi-step analysis artifacts —
      ``wave_*.tsv``/``.txt``, ``tech_debt_*.txt``, ``*_scan_*.txt``,
      ``stub_archive_candidates.json``, bare-SHA256 ``.json`` fingerprints.
      May be referenced across a workday.

    Args:
        adg_dir: ``artifacts/adg/`` (or test-injected equivalent).
        max_age_days: Back-compat — when provided, applies a single uniform
            floor (in days) to ALL pattern groups. If ``None`` (default),
            the two-tier behavior is used.
        fast_age_hours: Override the fast-tier floor.
        slow_age_hours: Override the slow-tier floor.
    """
    if not adg_dir.exists():
        return

    if max_age_days is not None:
        # Back-compat: uniform floor — both tiers use the same cutoff.
        fast_cutoff = slow_cutoff = time.time() - (max_age_days * 86400)
    else:
        now = time.time()
        fast_cutoff = now - (fast_age_hours * 3600)
        slow_cutoff = now - (slow_age_hours * 3600)

    fast_candidates: set[Path] = set()
    for pattern in _SESSION_SCRATCH_FAST_GLOBS:
        for path in adg_dir.glob(pattern):
            if not path.is_file() or "_archive" in path.parts:
                continue
            fast_candidates.add(path)

    slow_candidates: set[Path] = set()
    for pattern in _SESSION_SCRATCH_SLOW_GLOBS:
        for path in adg_dir.glob(pattern):
            if not path.is_file() or "_archive" in path.parts:
                continue
            slow_candidates.add(path)

    # Bare-SHA256 json files (scan fingerprint cache) — slow tier
    for path in adg_dir.glob("*.json"):
        if not path.is_file() or "_archive" in path.parts:
            continue
        if _SHA256_JSON_RE.match(path.name):
            slow_candidates.add(path)

    deleted = 0
    bytes_freed = 0
    for path, cutoff in (
        [(p, fast_cutoff) for p in fast_candidates]
        + [(p, slow_cutoff) for p in slow_candidates]
    ):
        try:
            st = path.stat()
        except OSError:
            continue
        if st.st_mtime >= cutoff:
            continue  # too fresh — likely current session
        try:
            path.unlink()
            deleted += 1
            bytes_freed += st.st_size
        except OSError as exc:
            print(f"[ADG] Archive: failed to delete scratch {path.name}: {exc}")

    if deleted:
        mb = bytes_freed / (1024 * 1024)
        if max_age_days is not None:
            tier_msg = f">{max_age_days}d old"
        else:
            tier_msg = f"fast>{fast_age_hours}h, slow>{slow_age_hours}h"
        print(f"[ADG] Archive: cleaned {deleted} session scratch files ({mb:.1f} MB freed, {tier_msg})")
