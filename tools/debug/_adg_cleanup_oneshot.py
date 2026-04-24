"""One-shot ADG cleanup using the now-fixed archiver.

Keeps the most recent run in artifacts/adg/, archives older runs to
artifacts/adg/_archive/<YYYY-MM>/. Uses the fixed _archive_old_artifacts
which now recognizes both MMDDYYYY_HHMM and YYYYMMDD_HHMMSS.

Reports before/after file count and total size.
"""

from __future__ import annotations

from pathlib import Path

from tools.generate.archiving.archiver import _archive_old_artifacts, _extract_timestamp


def _tally(root: Path) -> tuple[int, int]:
    count = 0
    size = 0
    for p in root.rglob("*"):
        if p.is_file():
            count += 1
            try:
                size += p.stat().st_size
            except OSError:
                pass
    return count, size


def _pick_latest_ts(root: Path) -> str | None:
    """Use the latest recognized timestamp in the top-level directory as 'current'."""
    latest: str | None = None
    latest_numeric: str = ""
    for p in root.glob("*"):
        if not p.is_file():
            continue
        ts = _extract_timestamp(p.name)
        if ts is None:
            continue
        # Normalize for comparison: strip underscore, take as plain digit string
        norm = ts.replace("_", "")
        if norm > latest_numeric:
            latest = ts
            latest_numeric = norm
    return latest


def main() -> int:
    adg_dir = Path("artifacts/adg")
    if not adg_dir.exists():
        print(f"[SKIP] {adg_dir} does not exist")
        return 0

    before_count, before_bytes = _tally(adg_dir)
    print(f"BEFORE: {before_count} files, {before_bytes / 1024 / 1024:.1f} MB")

    current_ts = _pick_latest_ts(adg_dir)
    if current_ts is None:
        print("[ERROR] Could not identify a 'current' timestamp")
        return 1

    print(f"Treating as current run: {current_ts}")
    print("Running _archive_old_artifacts with keep_runs=1 ...")
    _archive_old_artifacts(adg_dir=adg_dir, current_ts=current_ts, keep_runs=1)

    after_count, after_bytes = _tally(adg_dir)
    freed = before_bytes - after_bytes
    print()
    print(f"AFTER:  {after_count} files, {after_bytes / 1024 / 1024:.1f} MB")
    print(f"FREED:  {(before_count - after_count)} files, {freed / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
