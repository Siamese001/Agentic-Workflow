"""Migrate legacy R1A cache entries from plain-text r1a_key.txt to JSON stamp.

Reads all run directories under ``artifacts/apps_rg/runs/`` that contain only
the legacy ``r1a_key.txt`` (no ``r1a_stamp.json``) and rewrites them with the
new JSON envelope so that per-entry policy/blueprint validation works.

Usage::

    python tools/apps_rg/migrate_r1a_cache.py [--runs-dir PATH] [--dry-run]

The script is idempotent: directories that already have ``r1a_stamp.json`` are
skipped.  After migration the legacy ``r1a_key.txt`` is left in place for a
two-release read-compat window; it will be pruned by a future maintenance run.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

_log = logging.getLogger(__name__)

_STAMP_FILENAME = "r1a_stamp.json"
_LEGACY_STAMP_FILENAME = "r1a_key.txt"


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        stream=sys.stdout,
    )


def migrate_runs_dir(runs_dir: Path, dry_run: bool = False) -> dict:
    """Migrate all eligible run directories.

    Returns a summary dict with keys: scanned, skipped, migrated, failed.
    """
    summary = {"scanned": 0, "skipped": 0, "migrated": 0, "failed": 0}

    if not runs_dir.is_dir():
        _log.warning("runs_dir does not exist: %s", runs_dir)
        return summary

    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        summary["scanned"] += 1

        stamp_file = run_dir / _STAMP_FILENAME
        legacy_file = run_dir / _LEGACY_STAMP_FILENAME

        if stamp_file.exists():
            _log.debug("Skip (already migrated): %s", run_dir.name)
            summary["skipped"] += 1
            continue

        if not legacy_file.exists():
            _log.debug("Skip (no stamp at all): %s", run_dir.name)
            summary["skipped"] += 1
            continue

        try:
            raw_key = legacy_file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            _log.warning("Failed to read legacy stamp for %s: %s", run_dir.name, exc)
            summary["failed"] += 1
            continue

        new_stamp = {
            "key": raw_key,
            "schema_version": "1",
            "stamped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "_migrated_from": _LEGACY_STAMP_FILENAME,
        }

        if dry_run:
            _log.info("[dry-run] Would migrate: %s  key=%s...", run_dir.name, raw_key[:16])
            summary["migrated"] += 1
            continue

        try:
            stamp_file.write_text(json.dumps(new_stamp, indent=2), encoding="utf-8")
            _log.info("Migrated: %s  key=%s...", run_dir.name, raw_key[:16])
            summary["migrated"] += 1
        except OSError as exc:
            _log.warning("Failed to write new stamp for %s: %s", run_dir.name, exc)
            summary["failed"] += 1

    return summary


def main(argv: list[str] | None = None) -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-dir",
        default="artifacts/apps_rg/runs",
        help="Path to the runs directory (default: artifacts/apps_rg/runs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be migrated without writing any files",
    )
    args = parser.parse_args(argv)

    runs_dir = Path(args.runs_dir)
    _log.info("Migrating R1A cache in: %s  (dry_run=%s)", runs_dir, args.dry_run)

    summary = migrate_runs_dir(runs_dir, dry_run=args.dry_run)

    _log.info(
        "Done.  scanned=%d  skipped=%d  migrated=%d  failed=%d",
        summary["scanned"],
        summary["skipped"],
        summary["migrated"],
        summary["failed"],
    )
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
