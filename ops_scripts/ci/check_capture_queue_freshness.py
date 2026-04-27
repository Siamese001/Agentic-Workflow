#!/usr/bin/env python3
"""check_capture_queue_freshness.py — CI gate for the inline capture queue.

Detects a stalled drain: when ``artifacts/capture/markers.jsonl`` has been
sitting with non-empty content for longer than a threshold (default 24h),
the drain is not running and calibration data is piling up undelivered.

Exit codes:
  0 — queue fresh, or missing (nothing to drain), or empty
  1 — queue is stale (non-empty AND older than threshold); drain action needed

Can be invoked manually or wired into pre-commit / CI. In advisory mode
(``CAPTURE_QUEUE_FRESHNESS_MODE=advisory``) it always exits 0 but prints a
banner when the stale condition is met, so rollout can observe before
switching to strict enforcement.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE = REPO_ROOT / "artifacts" / "capture" / "markers.jsonl"
DEFAULT_MAX_AGE_HOURS = 24


def evaluate(queue_path: Path, max_age_hours: float) -> tuple[int, str]:
    """Return (exit_code, message). exit_code=0 means fresh or absent."""
    if not queue_path.exists():
        return 0, f"queue missing (not yet created): {queue_path}"
    size = queue_path.stat().st_size
    if size == 0:
        return 0, f"queue empty (drained recently): {queue_path}"
    mtime = datetime.fromtimestamp(queue_path.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(timezone.utc) - mtime
    age_hours = age.total_seconds() / 3600
    if age_hours <= max_age_hours:
        return 0, (
            f"queue fresh: {queue_path.name} {size}B, age {age_hours:.1f}h "
            f"(threshold {max_age_hours}h)"
        )
    return 1, (
        f"STALE capture queue: {queue_path} has {size}B pending and is "
        f"{age_hours:.1f}h old (> {max_age_hours}h threshold). "
        f"Run: python tools/capture/queue_to_ledger.py"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    args = parser.parse_args(argv)

    code, msg = evaluate(args.queue, args.max_age_hours)
    mode = os.environ.get("CAPTURE_QUEUE_FRESHNESS_MODE", "strict").lower()

    if code == 0:
        print(f"[capture-freshness] OK: {msg}")
        return 0

    if mode == "advisory":
        print(f"[capture-freshness] ADVISORY (would FAIL): {msg}", file=sys.stderr)
        return 0

    print(f"[capture-freshness] FAIL: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
