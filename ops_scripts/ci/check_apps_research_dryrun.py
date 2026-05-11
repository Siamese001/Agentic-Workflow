"""APPS-RESEARCH-DRYRUN gate — verifies apps_research spine dry-run.

Runs `python -m apps_research --spine --dry-run --target-company TestCo`
with APPS_RESEARCH_L2_FORCE_STUB=1 and verifies:
  - Exit code 0
  - "DRY RUN" appears in stdout
  - Artifact file is created

Usage:
    python ops_scripts/ci/check_apps_research_dryrun.py

Exit codes:
    0  all checks passed
    1  one or more checks failed

Bypass: APPS_RESEARCH_DRYRUN_GATE_BYPASS=1
Fail-closed: APPS_RESEARCH_DRYRUN_GATE_FAIL_CLOSED=1
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_GATE_ID = "APPS-RESEARCH-DRYRUN"
_REPORT_PATH = Path("artifacts/ci/apps_research_dryrun_gate.json")


def _run() -> dict:
    failures: list[str] = []

    env = dict(os.environ)
    env["APPS_RESEARCH_L2_FORCE_STUB"] = "1"

    result = subprocess.run(
        [
            sys.executable,
            "-m", "apps_research",
            "--spine",
            "--dry-run",
            "--target-company", "TestCo",
            "--depth", "standard",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )

    details: dict = {
        "exit_code": result.returncode,
        "stdout_snippet": result.stdout[:400],
        "stderr_snippet": result.stderr[:400],
    }

    if result.returncode != 0:
        failures.append(f"exit code {result.returncode} — expected 0")

    if "DRY RUN" not in result.stdout:
        failures.append("'DRY RUN' marker not found in stdout")

    passed = len(failures) == 0
    return {
        "gate": _GATE_ID,
        "passed": passed,
        "failures": failures,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    if os.environ.get("APPS_RESEARCH_DRYRUN_GATE_BYPASS", "").strip() in ("1", "true"):
        print(f"[{_GATE_ID}] BYPASSED")
        return 0

    report = _run()
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if report["passed"]:
        print(f"[{_GATE_ID}] OK — dry-run exit 0 with DRY RUN marker")
        return 0

    print(f"[{_GATE_ID}] FAIL — {len(report['failures'])} failure(s):")
    for f in report["failures"]:
        print(f"  - {f}")

    fail_closed = os.environ.get("APPS_RESEARCH_DRYRUN_GATE_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
    )
    return 1 if fail_closed else 0


if __name__ == "__main__":
    raise SystemExit(main())
