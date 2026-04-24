"""hotspot_defect_join.py — Hotspot prediction vs actual 30-day defect/churn join.

Reads the latest ADG snapshot's mv_hotspot_centrality top-N, joins against git
churn over a configurable window, and emits predicted/outcome rows to the
hotspot_defect ledger.

Usage:
    python ops_scripts/calibration/hotspot_defect_join.py
    python ops_scripts/calibration/hotspot_defect_join.py --top-n 50 --window-days 30
    python ops_scripts/calibration/hotspot_defect_join.py --dry-run

Exit codes:
    0 = success (report written, ledger rows emitted or dry-run complete)
    2 = no ADG snapshot found / mv_hotspot_centrality missing
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT_BOOTSTRAP = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_BOOTSTRAP))

ADG_DIR = _REPO_ROOT_BOOTSTRAP / "artifacts" / "adg"
ADG_SNAPSHOT_RE = re.compile(r"^adg_indexed_\d{8}_\d{4}\.sqlite$")


def _latest_adg_snapshot() -> Path | None:
    if not ADG_DIR.exists():
        return None
    candidates = sorted(
        (p for p in ADG_DIR.iterdir() if ADG_SNAPSHOT_RE.match(p.name)),
        reverse=True,
    )
    return candidates[0] if candidates else None


def _git_churn(window_days: int) -> dict[str, int]:
    """Return map of file_path -> number of commits touching it in the window."""
    try:
        cmd = [
            "git", "log",
            f"--since={window_days}.days.ago",
            "--pretty=format:",
            "--name-only",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_REPO_ROOT_BOOTSTRAP),
            shell=False,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[hotspot_defect_join] git log failed: {exc}", file=sys.stderr)
        return {}
    churn: dict[str, int] = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        churn[line] = churn.get(line, 0) + 1
    return churn


def _read_hotspots(adg_db: Path, top_n: int) -> tuple[list[dict], str]:
    """Return (rows, source) where source is 'mv_hotspot_centrality' or 'violations_fallback'."""
    try:
        conn = sqlite3.connect(str(adg_db), timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            tbl = conn.execute(
                "SELECT name FROM sqlite_master WHERE name='mv_hotspot_centrality'"
            ).fetchone()
            if tbl:
                rows = conn.execute(
                    """
                    SELECT * FROM mv_hotspot_centrality
                     ORDER BY COALESCE(impact_score, hotspot_score, fan_in) DESC
                     LIMIT ?
                    """,
                    (top_n,),
                ).fetchall()
                return [dict(r) for r in rows], "mv_hotspot_centrality"

            # Fallback: top-N files by violation count joined with nodes for layer info
            has_viol = conn.execute(
                "SELECT name FROM sqlite_master WHERE name='violations'"
            ).fetchone()
            if not has_viol:
                return [], "none"
            rows = conn.execute(
                """
                SELECT file_path,
                       COUNT(*) AS violation_count,
                       GROUP_CONCAT(DISTINCT severity) AS severities,
                       GROUP_CONCAT(DISTINCT category) AS categories
                  FROM violations
                 WHERE file_path IS NOT NULL AND file_path != ''
                 GROUP BY file_path
                 ORDER BY violation_count DESC
                 LIMIT ?
                """,
                (top_n,),
            ).fetchall()
            return [dict(r) for r in rows], "violations_fallback"
        finally:
            conn.close()
    except sqlite3.Error as exc:
        print(f"[hotspot_defect_join] ADG query failed: {exc}", file=sys.stderr)
        return [], "error"


def _resolve_file_path(hotspot_row: dict) -> str:
    """Best-effort file_path extraction; mv columns vary by snapshot version."""
    for key in ("file_path", "path", "file", "module_path"):
        val = hotspot_row.get(key)
        if val:
            return str(val)
    return ""


def _band(predicted_rank: int, actual_rank: int | None) -> str:
    if actual_rank is None:
        return "under_predicted"  # predicted but never churned -> over-predicted elsewhere
    delta = predicted_rank - actual_rank
    if abs(delta) <= 5:
        return "confirmed"
    if delta > 5:
        return "over_predicted"
    return "under_predicted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-n", type=int, default=100)
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    snapshot = _latest_adg_snapshot()
    if snapshot is None:
        print("[hotspot_defect_join] no ADG snapshot found under artifacts/adg/",
              file=sys.stderr)
        return 2

    hotspots, source = _read_hotspots(snapshot, args.top_n)
    if not hotspots:
        print(f"[hotspot_defect_join] no hotspots derivable from {snapshot.name} "
              f"(source={source}); dry_run={args.dry_run}", file=sys.stderr)
        return 0 if args.dry_run else 2

    churn = _git_churn(args.window_days)
    # Rank churn files so we can compute rank_delta
    churn_ranked = {
        path: rank
        for rank, (path, _) in enumerate(
            sorted(churn.items(), key=lambda kv: kv[1], reverse=True), start=1
        )
    }

    emitted = 0
    skipped_no_path = 0

    try:
        from tools.ledgers.hook_helpers import emit_ledger_event
    except ImportError:
        print("[hotspot_defect_join] ledger helpers missing; dry-run only",
              file=sys.stderr)
        emit_ledger_event = None  # type: ignore[assignment]

    for pred_rank, row in enumerate(hotspots, start=1):
        file_path = _resolve_file_path(row)
        if not file_path:
            skipped_no_path += 1
            continue
        actual_rank = churn_ranked.get(file_path)
        actual_churn = churn.get(file_path, 0)
        band = _band(pred_rank, actual_rank)
        if args.dry_run or emit_ledger_event is None:
            continue
        emit_ledger_event(
            ledger="hotspot_defect",
            event_kind="defect_join",
            prediction={
                "predicted_rank": pred_rank,
                "impact_score": row.get("impact_score") or row.get("hotspot_score"),
                "layer": row.get("layer"),
                "archetype": row.get("archetype"),
                "node_id": row.get("node_id") or row.get("id"),
            },
            outcome={
                "actual_churn_30d": actual_churn,
                "actual_rank_by_churn": actual_rank,
                "rank_delta": (pred_rank - actual_rank) if actual_rank is not None else None,
                "was_refactored": actual_churn > 0,
                "window_days": args.window_days,
            },
            score_band=band,
            score_numeric=float(row.get("impact_score") or row.get("hotspot_score") or 0.0),
            adg_snapshot_id=snapshot.stem,
            repo_area=file_path,
        )
        emitted += 1

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mode = "dry-run" if args.dry_run else "emitted"
    print(
        f"[hotspot_defect_join] {stamp} snapshot={snapshot.name} "
        f"top_n={args.top_n} window={args.window_days}d "
        f"{mode}={emitted} skipped_no_path={skipped_no_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
