#!/usr/bin/env python3
"""
check_adg_violation_log_delta.py — CI gate (P3).

Fails the build when the ADG enforcement violation logs have grown
relative to the base branch (``main`` by default). Converts the
append-only audit trail into a PR-level deterrent.

Monitors:
    artifacts/governance/adg_first_violations.jsonl
    artifacts/governance/graph_layer_violations.jsonl
    artifacts/governance/plan_evidence_violations.jsonl

For each, compares line count in HEAD vs base branch. Any growth = failure.

Env overrides:
    ADG_VIOLATION_LOG_BASE_BRANCH (default: "main")
    ADG_VIOLATION_LOG_DELTA_BYPASS=1 → exit 0 with "BYPASSED" banner

Run manually:
    python ops_scripts/ci/check_adg_violation_log_delta.py

Fail policy: CLOSED — growth detected → exit 1.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

_MONITORED_LOGS = [
    "artifacts/governance/adg_first_violations.jsonl",
    "artifacts/governance/graph_layer_violations.jsonl",
    "artifacts/governance/plan_evidence_violations.jsonl",
]

_BYPASS_ENV = "ADG_VIOLATION_LOG_DELTA_BYPASS"
_BASE_BRANCH_ENV = "ADG_VIOLATION_LOG_BASE_BRANCH"


def _count_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def _get_file_at_ref(ref: str, path: str) -> str:
    """Return the content of `path` at `ref`. Empty string if missing."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def _current_count(path: str) -> int:
    p = _ROOT / path
    if not p.exists():
        return 0
    try:
        return _count_lines(p.read_text(encoding="utf-8"))
    except OSError:
        return 0


def main() -> int:
    if os.environ.get(_BYPASS_ENV):
        print(f"[check_adg_violation_log_delta] BYPASSED (env {_BYPASS_ENV}=1)")
        return 0

    base_branch = os.environ.get(_BASE_BRANCH_ENV, "main")

    # Resolve the merge-base commit for a fair comparison when HEAD is ahead.
    try:
        mb = subprocess.run(
            ["git", "merge-base", "HEAD", base_branch],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
            check=False,
        )
        if mb.returncode == 0 and mb.stdout.strip():
            base_ref = mb.stdout.strip()
        else:
            base_ref = base_branch
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        base_ref = base_branch

    print(f"[check_adg_violation_log_delta] base_ref={base_ref}")

    failures: list[str] = []
    for path in _MONITORED_LOGS:
        base_content = _get_file_at_ref(base_ref, path)
        base_count = _count_lines(base_content)
        head_count = _current_count(path)
        delta = head_count - base_count
        marker = "OK" if delta <= 0 else "FAIL"
        print(f"  [{marker}] {path}: base={base_count} head={head_count} delta={delta:+d}")
        if delta > 0:
            failures.append(f"{path} grew by {delta} line(s)")

    if failures:
        print("")
        print("[check_adg_violation_log_delta] FAIL — ADG enforcement violation log(s) grew:")
        for f in failures:
            print(f"  - {f}")
        print(
            f"\nFix by addressing the violation(s) at their source, or set "
            f"{_BYPASS_ENV}=1 for an emergency bypass (logged)."
        )
        return 1

    print("[check_adg_violation_log_delta] OK — no violation log growth detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
