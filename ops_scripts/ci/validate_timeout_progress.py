"""Timeout + Progress Compliance Validator.

Implements Step 6 of `.cursor/workflows/timeout-progress-enforcement.md`
by delegating to the two existing checkers:

  §14 subprocess timeout  → ops_scripts/ci/check_terminal_cleanup.py
  §16 query progress bar  → ops_scripts/ci/check_query_progress_bar.py

Exit codes:
    0 — both checks passed
    1 — at least one violation found

Usage:
    python ops_scripts/ci/validate_timeout_progress.py [--staged]

Rationale:
    The timeout-progress workflow previously pointed at a non-existent
    script. Rather than duplicating detection logic, this thin entry-point
    runs the two authoritative gates in sequence so the workflow's
    "Validate Compliance" step is reachable.
"""

from __future__ import annotations

import argparse
import subprocess  # noqa: S404 -- invokes sibling CI gates
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_GATES = [
    ("§14 subprocess timeout / terminal cleanup", "check_terminal_cleanup.py"),
    ("§16 query progress bar", "check_query_progress_bar.py"),
]


def _run_gate(script: str, staged: bool) -> int:
    argv = [sys.executable, str(_ROOT / "ops_scripts" / "ci" / script)]
    if staged:
        argv.append("--staged")
    result = subprocess.run(  # noqa: S603 -- argv list, no shell
        argv,
        cwd=str(_ROOT),
        timeout=300,
        check=False,
    )
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Limit each gate to files staged for commit",
    )
    args = parser.parse_args(argv)

    failures: list[str] = []
    for label, script in _GATES:
        print(f"\n=== {label} ===", flush=True)
        rc = _run_gate(script, staged=args.staged)
        if rc != 0:
            failures.append(label)

    if failures:
        print("\n[validate_timeout_progress] FAIL:", ", ".join(failures))
        return 1
    print("\n[validate_timeout_progress] OK: all timeout + progress gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
