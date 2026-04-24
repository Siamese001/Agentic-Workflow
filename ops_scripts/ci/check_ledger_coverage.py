#!/usr/bin/env python3
"""
check_ledger_coverage.py — CI gate over the Author-Gate decision ledger.

Thin wrapper around .windsurf/scripts/audit_ledger_coverage.py that runs in
--ci mode: exit 0 on OK/WARN, exit 2 on FAIL. Emits a human-readable report
to stderr so PR reviewers see the breakdown.

Wired into:
    - .pre-commit-config.yaml (on staged changes to .windsurf/scripts/** or
      .windsurf/skills/refactor-decision-memory/**)
    - CI workflows that include gate invocation

Bypass:
    LEDGER_COVERAGE_BYPASS=1  —  logged, skips gate

CONSTITUTIONAL
    - subprocess.run with argv + shell=False + timeout
    - UTF-8 stdio
    - Specific exceptions
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = REPO_ROOT / ".windsurf" / "scripts" / "audit_ledger_coverage.py"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "ledger_coverage_bypass.jsonl"


def _log_bypass(reason: str) -> None:
    try:
        BYPASS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with BYPASS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "reason": reason,
            }) + "\n")
    except OSError:
        pass


def main() -> int:
    if os.environ.get("LEDGER_COVERAGE_BYPASS") == "1":
        _log_bypass("env:LEDGER_COVERAGE_BYPASS=1")
        print("[check_ledger_coverage] BYPASS fired (env). Logged.", file=sys.stderr)
        return 0

    if not AUDIT_SCRIPT.exists():
        print(f"[check_ledger_coverage] audit script missing: {AUDIT_SCRIPT} "
              f"(fail-open)", file=sys.stderr)
        return 0

    try:
        r = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[check_ledger_coverage] audit invocation failed: {exc} "
              f"(fail-open)", file=sys.stderr)
        return 0

    try:
        report = json.loads(r.stdout)
    except (json.JSONDecodeError, ValueError):
        print(f"[check_ledger_coverage] audit output unparseable (fail-open):\n"
              f"  stdout={r.stdout[:300]}\n  stderr={r.stderr[:300]}",
              file=sys.stderr)
        return 0

    status = report.get("status", "UNKNOWN")
    rates = report.get("rates", {})
    statuses = report.get("statuses", {})
    totals = report.get("totals", {})

    # Emit a compact summary to stderr
    print(f"[check_ledger_coverage] status={status}", file=sys.stderr)
    for k, v in rates.items():
        classify = statuses.get(k, "?")
        print(f"  {k:20s} = {v:.2%}  [{classify}]", file=sys.stderr)
    print(f"  outcomes_w_tests_passed = {totals.get('outcomes_with_tests_passed', '?')}",
          file=sys.stderr)
    print(f"  promoted_patterns       = {totals.get('promoted', '?')}", file=sys.stderr)
    print(f"  unreachable_shas        = {totals.get('unreachable_shas', '?')}",
          file=sys.stderr)

    if status == "FAIL":
        print("\n[check_ledger_coverage] FAIL — meta-learning ledger coverage below floor.",
              file=sys.stderr)
        print("  Fix: run `python .windsurf/scripts/post_commit_outcome_binder.py "
              "--lookback 100` then `python .windsurf/scripts/promote_author_gate_patterns.py`.",
              file=sys.stderr)
        print("  Bypass for unblocking (not recommended): LEDGER_COVERAGE_BYPASS=1",
              file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
