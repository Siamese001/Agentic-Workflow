"""Calibration drift detector — automated unknown-budget breach monitor.

Closes G13 gap from the runtime-gate-coverage-hardening plan
(.windsurf/plans/runtime-gate-coverage-hardening-7e3f1a.md).

Reads scorecard JSONL files in the rolling window, computes per-judge /
per-dimension Unknown-rate, and compares against the
`calibration_drift_policy` block in apps_eval/config/eval_policies.yaml.

Exit codes:
  0  : drift within acceptable bounds (or insufficient data)
  1  : warn breach (>= breach_rate_warn_threshold but < alert_threshold)
  2  : alert breach (>= breach_rate_alert_threshold) — page for human recalibration

Usage:
  python -m ops_scripts.calibration.calibration_drift_detector \\
      --scorecard-dir artifacts/eval/scorecards \\
      --window 7

  python ops_scripts/calibration/calibration_drift_detector.py --window 7
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

_log = logging.getLogger("calibration_drift")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "apps_eval" / "config" / "eval_policies.yaml"
DEFAULT_SCORECARD_DIR = REPO_ROOT / "artifacts" / "eval" / "scorecards"

EXIT_OK = 0
EXIT_WARN = 1
EXIT_ALERT = 2


def _load_policy(path: Path) -> dict[str, Any]:
    """Load calibration_drift_policy block from eval_policies.yaml."""
    if not path.exists():
        _log.warning("policy file %s missing; using built-in defaults", path)
        return _default_policy()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        _log.warning("policy parse failed: %s; using defaults", exc)
        return _default_policy()
    block = raw.get("calibration_drift_policy")
    if not isinstance(block, dict):
        _log.warning("calibration_drift_policy missing in %s; using defaults", path)
        return _default_policy()
    return block


def _default_policy() -> dict[str, Any]:
    return {
        "rolling_window_days": 7,
        "breach_rate_warn_threshold": 0.10,
        "breach_rate_alert_threshold": 0.20,
        "min_runs_for_signal": 5,
    }


def _iter_scorecard_records(
    scorecard_dir: Path,
    window_days: int,
) -> Iterable[dict[str, Any]]:
    """Yield scorecard rows from JSONL files modified within the window.

    Each scorecard file is expected to be JSON lines where each row has at
    minimum:
        {"dimension_id": "...", "judge_id": "...", "verdict": "PASS|WARN|FAIL|UNKNOWN", "score": float}
    Additional fields are tolerated.
    """
    if not scorecard_dir.exists():
        _log.warning("scorecard dir %s missing", scorecard_dir)
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    cutoff_ts = cutoff.timestamp()
    for path in scorecard_dir.glob("*.jsonl"):
        try:
            if path.stat().st_mtime < cutoff_ts:
                continue
        except OSError:
            continue
        try:
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(rec, dict):
                        yield rec
        except (OSError, UnicodeDecodeError) as exc:
            _log.warning("could not read %s: %s", path, exc)


def compute_breach_rates(
    records: Iterable[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, int], int]:
    """Compute per-judge unknown-rate.

    Returns:
        (rates_by_judge, total_by_judge, total_runs)
        rates_by_judge[judge_id] = unknown_count / total_count
    """
    total_by_judge: dict[str, int] = defaultdict(int)
    unknown_by_judge: dict[str, int] = defaultdict(int)
    runs: set[str] = set()
    for rec in records:
        judge = str(rec.get("judge_id") or rec.get("judge") or "default")
        verdict = str(rec.get("verdict") or "").upper()
        total_by_judge[judge] += 1
        if verdict == "UNKNOWN" or rec.get("score") is None:
            unknown_by_judge[judge] += 1
        run_id = rec.get("trace_id") or rec.get("run_id")
        if run_id:
            runs.add(str(run_id))
    rates = {
        j: (unknown_by_judge[j] / total_by_judge[j]) if total_by_judge[j] else 0.0 for j in total_by_judge
    }
    return rates, dict(total_by_judge), len(runs)


def evaluate_drift(
    rates: dict[str, float],
    totals: dict[str, int],
    total_runs: int,
    policy: dict[str, Any],
) -> tuple[int, list[str]]:
    """Evaluate per-judge rates against thresholds.

    Returns:
        (exit_code, message_lines)
    """
    warn_t = float(policy.get("breach_rate_warn_threshold", 0.10))
    alert_t = float(policy.get("breach_rate_alert_threshold", 0.20))
    min_runs = int(policy.get("min_runs_for_signal", 5))
    lines: list[str] = []

    if total_runs < min_runs:
        lines.append(
            f"INSUFFICIENT_DATA: {total_runs} runs in window (min_runs_for_signal={min_runs}); no alert"
        )
        return EXIT_OK, lines

    worst = EXIT_OK
    for judge, rate in sorted(rates.items()):
        n = totals.get(judge, 0)
        if rate >= alert_t:
            lines.append(
                f"ALERT: judge={judge} unknown_rate={rate:.3f} (>= alert_threshold={alert_t:.3f}, n={n})"
            )
            worst = max(worst, EXIT_ALERT)
        elif rate >= warn_t:
            lines.append(
                f"WARN: judge={judge} unknown_rate={rate:.3f} (>= warn_threshold={warn_t:.3f}, n={n})"
            )
            worst = max(worst, EXIT_WARN)
        else:
            lines.append(f"OK: judge={judge} unknown_rate={rate:.3f} (n={n})")
    return worst, lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Eval-judge calibration drift detector (G13).")
    parser.add_argument(
        "--scorecard-dir",
        type=Path,
        default=DEFAULT_SCORECARD_DIR,
        help="Directory of scorecard *.jsonl files (default: artifacts/eval/scorecards)",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_PATH,
        help="Path to eval_policies.yaml",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=None,
        help="Override rolling window (days); defaults to policy value",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-judge OK lines",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="[calibration_drift] %(levelname)s %(message)s",
        stream=sys.stderr,
    )

    policy = _load_policy(args.policy)
    window_days = args.window if args.window is not None else int(policy.get("rolling_window_days", 7))

    records = list(_iter_scorecard_records(args.scorecard_dir, window_days))
    rates, totals, total_runs = compute_breach_rates(records)
    code, lines = evaluate_drift(rates, totals, total_runs, policy)

    print(f"calibration_drift window_days={window_days} runs={total_runs} judges={len(rates)}")
    for line in lines:
        if args.quiet and line.startswith("OK:"):
            continue
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
