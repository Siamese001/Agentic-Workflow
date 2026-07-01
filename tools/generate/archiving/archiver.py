"""Timestamp parsing and artifact retention for ADG generation."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

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

_RETENTION_PATTERNS: tuple[str, ...] = (
    "adg_*.json",
    "adg_*.md",
    "adg_*.yaml",
    "adg_*.yml",
    "adg_*.sqlite",
    "adg_*.sqlite-shm",
    "adg_*.sqlite-wal",
    "adg_*.sqlite.intoto.jsonl",
    "adg_run_*.zip",
    "archive_skipped_*.txt",
    "graphdb_*",
    "scan_result_cache.json",
    "*_report_*.json",
    "*_report_*.md",
    "*_report_*.yaml",
    "*_report_*.yml",
    "dead_code_zone_control_report_*.json",
    "dead_code_zone_control_report_*.md",
    "dead_code_zone_control_report_*.yaml",
    "dead_code_zone_control_report_*.yml",
    "repair_log_*.json",
    "test_surface_coverage_*.json",
    "p1_ratchet.json",
    "p2_ratchet.json",
)

_SQLITE_RUN_RE = re.compile(r"adg_indexed_(\d{8}_\d{4})\.sqlite")


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


def _extract_sqlite_run_id(value: object) -> str | None:
    """Return main-generator run id embedded in a path-ish value."""
    if not isinstance(value, str) or not value:
        return None
    match = _SQLITE_RUN_RE.search(value.replace("\\", "/"))
    return match.group(1) if match else None


def _walk_json_values(value: Any) -> list[str]:
    """Collect string values from small JSON metadata for retention grouping."""
    found: list[str] = []
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            found.append(item)
        elif isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    return found


def _run_id_from_json_metadata(path: Path, *, max_bytes: int = 2_000_000) -> str | None:
    """Map helper artifacts back to their canonical ``adg_indexed_<run>.sqlite``.

    Gate results and watchlists often use UTC stamps such as
    ``20260701_080018`` while their payload points at the main local run id
    (``07012026_0354``). Retention must group those helpers with the SQLite
    run instead of treating them as independent newer runs.
    """
    if path.suffix.lower() != ".json":
        return None
    try:
        if path.stat().st_size > max_bytes:
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    priority_keys = (
        "sqlite_source",
        "sqlite_used",
        "sqlite_path",
        "snapshot_path",
        "snapshot",
        "adg_snapshot",
        "published_snapshot",
        "baseline_snapshot",
    )
    if isinstance(data, dict):
        for key in priority_keys:
            run_id = _extract_sqlite_run_id(data.get(key))
            if run_id:
                return run_id
            nested = data.get(key)
            if isinstance(nested, dict):
                for value in nested.values():
                    run_id = _extract_sqlite_run_id(value)
                    if run_id:
                        return run_id

    for value in _walk_json_values(data):
        run_id = _extract_sqlite_run_id(value)
        if run_id:
            return run_id
    return None


def _is_year_leading_timestamp(ts: str | None) -> bool:
    if ts is None or "_" not in ts:
        return False
    date_part, time_part = ts.split("_", 1)
    return (
        len(date_part) == 8
        and date_part.startswith(("202", "203", "204", "205", "206"))
        and len(time_part) == 6
    )


def _artifact_retention_run_id(path: Path) -> str | None:
    """Return the retention bucket id for an artifact."""
    if path.name.startswith("adg_run_") and path.suffix == ".zip":
        return path.stem.replace("adg_run_", "")

    ts_opt = _extract_timestamp(path.name)
    if _is_year_leading_timestamp(ts_opt) or ts_opt is None:
        metadata_run_id = _run_id_from_json_metadata(path)
        if metadata_run_id:
            return metadata_run_id
    return ts_opt


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


def _archive_loose_artifacts(
    files: list[Path],
    zip_files: list[Path],
    archive_month_dir: Path,
) -> tuple[int, int, int]:
    """Move non-zip run artifacts into ``_archive/<YYYY-MM>/`` (gzip for files, move for dirs).

    Returns:
        Tuple of (archived_count, bytes_original, bytes_archived)
    """
    from tools.generate.archiving.zipper import _archive_individual_files

    archived_count = 0
    bytes_original = 0
    bytes_archived = 0
    zip_set = set(zip_files)
    loose_files: list[Path] = []

    for path in files:
        if path in zip_set or not path.exists():
            continue
        if path.is_dir():
            dest = archive_month_dir / path.name
            try:
                size = _path_size_bytes(path)
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(path), str(dest))
                archived_count += 1
                bytes_original += size
                bytes_archived += size
            except OSError as exc:
                print(f"[ADG] Archive: failed to move directory {path.name}: {exc}")
            continue
        if path.is_file():
            loose_files.append(path)

    if loose_files:
        file_archived, file_orig, file_arch = _archive_individual_files(loose_files, archive_month_dir)
        archived_count += file_archived
        bytes_original += file_orig
        bytes_archived += file_arch

    return archived_count, bytes_original, bytes_archived


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


def _has_primary_sqlite(files: list[Path], ts: str) -> bool:
    return any(path.name == f"adg_indexed_{ts}.sqlite" for path in files)


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
    seen_paths: dict[str, set[Path]] = defaultdict(set)

    for pattern in _RETENTION_PATTERNS:
        for path in adg_dir.glob(pattern):  # tqdm: pre-scan accumulation, no display needed
            if "LATEST" in path.name or "latest" in path.name:
                continue
            if "_archive" in path.parts:
                continue

            ts_opt = _artifact_retention_run_id(path)
            if ts_opt:
                if path in seen_paths[ts_opt]:
                    continue
                runs[ts_opt].append(path)
                seen_paths[ts_opt].add(path)

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
    canonical_timestamps = [
        ts for ts in sorted_timestamps if _has_primary_sqlite(runs.get(ts, []), ts)
    ]
    protected_timestamps = set(canonical_timestamps[:keep_runs])
    if current_ts:
        protected_timestamps.add(current_ts)
    if not protected_timestamps:
        protected_timestamps.update(sorted_timestamps[:keep_runs])
    to_archive = [ts for ts in sorted_timestamps if ts not in protected_timestamps]

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
        else:
            print(
                f"[ADG] Archive: Archiving orphaned run {ts} ({len(files)} loose artifacts, no run zip)",
            )

        loose_archived, loose_orig, loose_arch = _archive_loose_artifacts(
            files,
            zip_files,
            archive_month_dir,
        )
        archived_count += loose_archived
        bytes_original += loose_orig
        bytes_archived += loose_arch

    if bytes_original > 0:
        savings = bytes_original - bytes_archived
        pct = (savings / bytes_original * 100) if bytes_original > 0 else 0
        print(f"[ADG] Archive: archived {len(to_archive)} runs, {archived_count} files (saved {pct:.0f}%)")

    _write_retention_manifest(
        adg_dir=adg_dir,
        current_ts=current_ts,
        protected_timestamps=sorted(protected_timestamps),
        archived_timestamps=to_archive,
        archived_count=archived_count,
        bytes_original=bytes_original,
        bytes_archived=bytes_archived,
    )

    # Delegate cleanup of validation packages and MANIFEST files
    from tools.generate.reporting.analysis import _cleanup_validation_files

    _cleanup_validation_files(adg_dir, current_ts)

    # P1 of RCA 2026-04-28: age-gated cleanup of session scratch (ad-hoc
    # redirect logs, wave queue files, triage outputs). Runs AFTER the
    # main retention pass so it can't race the current-run zip or delete
    # anything the generator touched this cycle.
    _cleanup_session_scratch(adg_dir, max_age_days=_SCRATCH_AGE_DAYS_DEFAULT)


def _write_retention_manifest(
    *,
    adg_dir: Path,
    current_ts: str,
    protected_timestamps: list[str],
    archived_timestamps: list[str],
    archived_count: int,
    bytes_original: int,
    bytes_archived: int,
) -> None:
    """Write a compact receipt for retention decisions."""
    if not current_ts:
        return
    payload = {
        "schema_version": "adg-retention-manifest/v1",
        "current_ts": current_ts,
        "protected_timestamps": protected_timestamps,
        "archived_timestamps": archived_timestamps,
        "archived_count": archived_count,
        "bytes_original": bytes_original,
        "bytes_archived": bytes_archived,
        "generated_at_epoch": time.time(),
    }
    try:
        path = adg_dir / f"adg_retention_manifest_{current_ts}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"[ADG] Archive: failed to write retention manifest: {exc}")


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
