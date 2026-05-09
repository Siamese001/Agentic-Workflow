"""L6 ADG Layer-Tag Consistency Gate.

Plan: .windsurf/plans/l6-doctrinal-alignment-noninvasive-b9d3f5.md W5.

Verifies that every Python module under `system_learning/` is tagged
`layer=L6` in the latest ADG SQLite snapshot. Surfaces drift if the
ADG layer-resolution heuristic ever stops tagging a new subdir as L6.

Read-only — does NOT modify the ADG. If the snapshot is missing or
older than 7 days, the gate skips with WARNING (advisory mode).

Modes
-----
- Default: advisory (exit 0).
- Fail-closed: set `L6_LAYER_TAG_FAIL_CLOSED=1` (exit 2 on findings).
- Bypass: set `L6_LAYER_TAG_BYPASS=1`.

Output
------
Writes findings to `artifacts/windsurf/l6_layer_tag_violations.json`.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SL_ROOT = REPO_ROOT / "system_learning"
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
SKIP_SUBDIRS = {"__pycache__", "logs", "raw", "snapshots"}
STALE_SECONDS = 7 * 24 * 3600


def _latest_snapshot() -> Path | None:
    if not ADG_DIR.exists():
        return None
    candidates = sorted(
        (p for p in ADG_DIR.glob("adg_indexed_*.sqlite") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _expected_files() -> set[str]:
    """Return set of repo-relative .py paths under system_learning/ to check."""
    out: set[str] = set()
    if not SL_ROOT.exists():
        return out
    for root, dirnames, filenames in os.walk(SL_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_SUBDIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            full = Path(root) / fname
            try:
                rel = full.relative_to(REPO_ROOT).as_posix()
            except ValueError:
                continue
            out.add(rel)
    return out


def _adg_l6_files(db_path: Path) -> set[str]:
    """Return set of resolved_path values for all nodes with layer=L6."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        cur = conn.execute(
            "SELECT DISTINCT resolved_path FROM nodes WHERE layer = 'L6' AND resolved_path != ''"
        )
        return {row[0] for row in cur.fetchall() if row[0]}
    finally:
        conn.close()


def main() -> int:
    if os.environ.get("L6_LAYER_TAG_BYPASS") == "1":
        print("[l6_layer_tag] BYPASS active (L6_LAYER_TAG_BYPASS=1)")
        return 0

    out_dir = REPO_ROOT / "artifacts" / "windsurf"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "l6_layer_tag_violations.json"

    snapshot = _latest_snapshot()
    if snapshot is None:
        msg = "no ADG snapshot found under artifacts/adg/"
        print(f"[l6_layer_tag] SKIP — {msg}")
        out_path.write_text(
            json.dumps({"status": "skipped", "reason": msg}, indent=2),
            encoding="utf-8",
        )
        return 0

    age = time.time() - snapshot.stat().st_mtime
    if age > STALE_SECONDS:
        msg = f"ADG snapshot {snapshot.name} is older than 7 days"
        print(f"[l6_layer_tag] SKIP — {msg}")
        out_path.write_text(
            json.dumps(
                {"status": "skipped", "reason": msg, "snapshot": snapshot.name},
                indent=2,
            ),
            encoding="utf-8",
        )
        return 0

    expected = _expected_files()
    try:
        adg_l6 = _adg_l6_files(snapshot)
    except sqlite3.DatabaseError as exc:
        msg = f"ADG snapshot read failed: {exc}"
        print(f"[l6_layer_tag] SKIP — {msg}")
        out_path.write_text(
            json.dumps(
                {"status": "skipped", "reason": msg, "snapshot": snapshot.name},
                indent=2,
            ),
            encoding="utf-8",
        )
        return 0

    missing = sorted(expected - adg_l6)
    coverage = (
        (len(expected) - len(missing)) / len(expected) if expected else 1.0
    )

    report = {
        "status": "ok" if not missing else "findings",
        "snapshot": snapshot.name,
        "expected_count": len(expected),
        "tagged_count": len(expected) - len(missing),
        "coverage": round(coverage, 4),
        "missing": missing,
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not missing:
        print(
            f"[l6_layer_tag] OK — {len(expected)}/{len(expected)} tagged L6 "
            f"(snapshot: {snapshot.name})"
        )
        return 0

    print(
        f"[l6_layer_tag] {len(missing)} module(s) under system_learning/ NOT tagged L6 in {snapshot.name}:"
    )
    for path in missing[:20]:
        print(f"  {path}")
    if len(missing) > 20:
        print(f"  ... and {len(missing) - 20} more (see {out_path.relative_to(REPO_ROOT)})")

    if os.environ.get("L6_LAYER_TAG_FAIL_CLOSED") == "1":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
