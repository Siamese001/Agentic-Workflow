"""pre_user_prompt_weekly_report.py — ISO-week cadence trigger for the token-burn weekly report.

Registered in `.cursor/hooks.json` under `pre_user_prompt`. On the FIRST user
prompt of each ISO week (Mon-Sun per ISO 8601), runs
`ops_scripts/calibration/token_burn_weekly_report.py` in the background and
writes a sentinel to `.claude/state/weekly_report_<YYYY-Www>.flag` so
subsequent prompts in the same week are no-ops.

This addresses the f8c2d1 follow-up plan deferred item: "Weekly token-burn
report cadence automation — script exists but has no scheduled trigger."
Operator-manual runs meant reports drifted; now they auto-run once per week.

Behavior
--------
- Read stdin (Cursor Agent passes JSON payload). Payload ignored — this is a
  cadence trigger, not a conditional one.
- Compute current ISO year-week (YYYY-WNN).
- If `.claude/state/weekly_report_<YYYY-Www>.flag` exists → no-op, exit 0.
- Else: subprocess.Popen the weekly report script in the background (30s
  timeout, detached), write the sentinel, exit 0.
- Report output lands in `docs/reports/token-burn/<YYYY-Www>.md` as usual.

Fail policy: OPEN — any error (missing script, subprocess failure, filesystem
write error) is logged to stderr and the hook exits 0. A failed weekly report
MUST NEVER block the user's prompt.

Sentinel format: one line, ISO timestamp of when the report was triggered.
Manual rebuild: delete the sentinel and the next prompt re-runs the report.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".claude" / "state"
REPORT_SCRIPT = REPO_ROOT / "ops_scripts" / "calibration" / "token_burn_weekly_report.py"
TIMEOUT_SECONDS = 30


def _current_iso_week_label() -> str:
    now = datetime.now(timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def _sentinel_path(label: str) -> Path:
    return STATE_DIR / f"weekly_report_{label}.flag"


def _trigger_report() -> None:
    """Launch the weekly report script. Fail-open on any error."""
    if not REPORT_SCRIPT.exists():
        print(
            f"[weekly_report] WARN: report script not found at {REPORT_SCRIPT}",
            file=sys.stderr,
        )
        return
    try:
        subprocess.run(
            [sys.executable, str(REPORT_SCRIPT)],
            cwd=str(REPO_ROOT),
            timeout=TIMEOUT_SECONDS,
            capture_output=True,
            text=True,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        print(f"[weekly_report] WARN: trigger failed: {exc}", file=sys.stderr)


def _write_sentinel(path: Path) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(
            datetime.now(timezone.utc).isoformat() + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"[weekly_report] WARN: sentinel write failed: {exc}", file=sys.stderr)


def main() -> int:
    # Drain stdin if present — we don't inspect it but must not block.
    try:
        if not sys.stdin.isatty():
            sys.stdin.read()
    except (OSError, ValueError):
        pass

    label = _current_iso_week_label()
    sentinel = _sentinel_path(label)
    if sentinel.exists():
        return 0

    _trigger_report()
    _write_sentinel(sentinel)
    print(f"[weekly_report] triggered for ISO week {label}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[weekly_report] fail-open on exception: {exc}", file=sys.stderr)
        sys.exit(0)
