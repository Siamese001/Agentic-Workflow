"""prompt_classifier_binder.py — Bind actual commit stats to tier predictions.

For every `tier_prediction` prediction row in the prompt_classifier ledger
that has no bound outcome, find the earliest commit after its ts_utc and
bind outcome = {files_edited, lines_changed, layers_touched, actual_tier}.

Actual tier is derived the same way classify_tier does, applied retroactively
to observables rather than keywords:

    T0  files_edited == 0
    T1  files_edited <= 1 and lines_changed <= 20
    T2  files_edited <= 5 and layers_touched <= 1
    T3  files_edited > 5 or layers_touched > 1

Usage:
    python ops_scripts/calibration/prompt_classifier_binder.py
    python ops_scripts/calibration/prompt_classifier_binder.py --lookback 50 --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

LEDGER_DB = _REPO_ROOT / "artifacts" / "ledgers" / "prompt_classifier.sqlite"
LAYER_RE = re.compile(r"(?:^|/)(L[0-6]_[a-z_]+|apps_[a-z_]+|agentic_core|infrastructure|system_learning)/")


def _recent_commits(lookback: int) -> list[dict]:
    """Return [{sha, ts_iso, files:[...], lines_added, lines_deleted}, ...] newest first."""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{lookback}", "--pretty=format:@@@%H@@@%cI", "--numstat", "--no-merges"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"[prompt_classifier_binder] git log failed: {exc}", file=sys.stderr)
        return []

    commits: list[dict] = []
    for line in result.stdout.splitlines():
        if line.startswith("@@@"):
            try:
                _, sha, ts_iso = line.split("@@@")
            except ValueError:
                continue
            commits.append(
                {
                    "sha": sha,
                    "ts_iso": ts_iso,
                    "files": [],
                    "lines_added": 0,
                    "lines_deleted": 0,
                }
            )
            continue
        if not line.strip() or not commits:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        try:
            a = int(added) if added != "-" else 0
            d = int(deleted) if deleted != "-" else 0
        except ValueError:
            a, d = 0, 0
        current = commits[-1]
        current["lines_added"] += a
        current["lines_deleted"] += d
        current["files"].append(path)
    return commits


def _unbound_predictions(conn: sqlite3.Connection, limit: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT event_id, ts_utc, prediction_json
          FROM events
         WHERE event_kind = 'tier_prediction'
           AND status = 'predicted'
         ORDER BY ts_utc ASC
         LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result = []
    for eid, ts_utc, pred_json in rows:
        try:
            pred = json.loads(pred_json) if pred_json else {}
        except json.JSONDecodeError:
            pred = {}
        result.append({"event_id": eid, "ts_utc": ts_utc, "prediction": pred})
    return result


def _layers_touched(files: list[str]) -> tuple[int, list[str]]:
    layers: set[str] = set()
    for path in files:
        m = LAYER_RE.search(path)
        if m:
            layers.add(m.group(1))
    return len(layers), sorted(layers)


def _derive_actual_tier(files_edited: int, lines_changed: int, layers_touched: int) -> str:
    if files_edited == 0:
        return "T0"
    if files_edited <= 1 and lines_changed <= 20:
        return "T1"
    if files_edited <= 5 and layers_touched <= 1:
        return "T2"
    return "T3"


def _accuracy_band(predicted: str, actual: str) -> str:
    if predicted == actual:
        return "exact"
    order = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}
    try:
        delta = order[predicted] - order[actual]
    except KeyError:
        return "miss"
    if delta == 1 or delta == -1:
        return "off_by_one"
    return "miss"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback", type=int, default=100, help="Max predictions to scan (default 100)")
    parser.add_argument("--commit-lookback", type=int, default=50, help="Max commits to scan (default 50)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not LEDGER_DB.exists():
        print(f"[prompt_classifier_binder] ledger not found: {LEDGER_DB}", file=sys.stderr)
        return 0

    commits = _recent_commits(args.commit_lookback)
    if not commits:
        print("[prompt_classifier_binder] no commits returned from git log.", file=sys.stderr)
        return 0

    try:
        from tools.ledgers.hook_helpers import bind_ledger_outcome
    except ImportError:
        print("[prompt_classifier_binder] ledger helpers missing", file=sys.stderr)
        return 2

    conn = sqlite3.connect(str(LEDGER_DB), timeout=5)
    try:
        predictions = _unbound_predictions(conn, args.lookback)
    finally:
        conn.close()

    if not predictions:
        print("[prompt_classifier_binder] no unbound tier_prediction rows.", file=sys.stderr)
        return 0

    # commits sorted newest-first from git log; reverse so we scan oldest-first
    commits_oldest_first = list(reversed(commits))
    bound = 0

    for pred in predictions:
        pred_ts = pred["ts_utc"]
        # Find first commit strictly AFTER pred_ts
        match = next((c for c in commits_oldest_first if c["ts_iso"] > pred_ts), None)
        if match is None:
            continue
        files_edited = len(match["files"])
        lines_changed = match["lines_added"] + match["lines_deleted"]
        layers_touched, layers_list = _layers_touched(match["files"])
        actual_tier = _derive_actual_tier(files_edited, lines_changed, layers_touched)
        predicted_tier = pred["prediction"].get("predicted_tier", "unknown")
        band = _accuracy_band(predicted_tier, actual_tier)

        if args.dry_run:
            bound += 1
            continue

        ok = bind_ledger_outcome(
            ledger="prompt_classifier",
            event_id=pred["event_id"],
            outcome={
                "actual_tier": actual_tier,
                "files_edited": files_edited,
                "lines_changed": lines_changed,
                "layers_touched": layers_touched,
                "layers_list": layers_list,
                "commit_sha": match["sha"],
            },
            score_band=band,
            score_numeric=0.0 if band == "exact" else (0.5 if band == "off_by_one" else 1.0),
        )
        if ok:
            bound += 1

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mode = "would bind" if args.dry_run else "bound"
    print(
        f"[prompt_classifier_binder] {stamp} {mode}={bound} "
        f"scanned_predictions={len(predictions)} scanned_commits={len(commits)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
